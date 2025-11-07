"""Analytics service for calculating metrics from MySQL database."""
from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Dict, Optional
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
from collections import OrderedDict

from src.models import Message, Conversation, Channel
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def dashboard(self) -> Dict[str, object]:
        """Generate dashboard with general and weekly metrics."""
        try:
            zone = ZoneInfo("America/Argentina/Buenos_Aires")
        except Exception as e:
            logger.warning(f"Could not load timezone: {e}. Using UTC.")
            zone = ZoneInfo("UTC")
        
        today = datetime.now(zone).date()

        # Calculate week boundaries (Monday to Sunday)
        this_week_start = today - timedelta(days=today.weekday())
        this_week_end = this_week_start + timedelta(days=6)
        last_week_start = this_week_start - timedelta(weeks=1)
        last_week_end = this_week_start - timedelta(days=1)

        # Build dashboard data
        r: Dict[str, object] = OrderedDict()
        r["general"] = self._build_general_metrics(zone)
        
        semana_anterior = self._build_weekly_metrics(last_week_start, last_week_end, zone)
        semana_actual = self._build_weekly_metrics(this_week_start, this_week_end, zone)
        
        r["semana_anterior"] = semana_anterior
        r["semana_actual"] = semana_actual
        r["comparativa_semanal"] = self._build_weekly_comparison(semana_anterior, semana_actual)
        
        return r

    def _build_general_metrics(self, zone: ZoneInfo) -> Dict[str, object]:
        """Build general metrics from all conversations and messages."""
        total_conv = self.db.query(Conversation).count()

        # Calculate FRT and SLA
        frt_data = self._calculate_frt_all()
        frts_min = [frt for frt in frt_data.values() if frt is not None]
        frt_avg = (sum(frts_min) / len(frts_min)) if frts_min else None
        
        ok24 = sum(1 for frt in frts_min if frt <= 1440)
        pct24h = (100.0 * ok24 / total_conv) if total_conv > 0 else None

        # Count messages by direction
        total_in = self.db.query(Message).filter(Message.direction == "incoming").count()
        total_out = self.db.query(Message).filter(Message.direction == "outgoing").count()

        # Messages by channel - optimized query
        por_canal = self._get_messages_by_channel()

        return OrderedDict({
            "frt_avg_min": round(frt_avg, 2) if frt_avg is not None else None,
            "pct_respondido_24h": round(pct24h, 2) if pct24h is not None else None,
            "conversations_total": total_conv,
            "mensajes_totales_in": total_in,
            "mensajes_totales_out": total_out,
            "por_canal_total": por_canal
        })

    def _build_weekly_metrics(self, week_start: date, week_end: date, zone: ZoneInfo) -> Dict[str, object]:
        """Build weekly metrics for a specific week."""
        # Convert week boundaries to UTC
        from_dt, to_dt = self._get_week_boundaries_utc(week_start, week_end, zone)
        
        # Get all messages in the week (single query)
        msgs_in_week = self.db.query(Message).filter(
            and_(
                Message.timestamp >= from_dt.replace(tzinfo=None),
                Message.timestamp < to_dt.replace(tzinfo=None)
            )
        ).all()

        # Build conversation cache to avoid N+1 queries
        conv_cache = self._build_conversation_cache(msgs_in_week)
        
        # Calculate basic metrics
        conversations = len(set(msg.conversation_id for msg in msgs_in_week))
        total_in = sum(1 for m in msgs_in_week if m.direction == "incoming")
        total_out = sum(1 for m in msgs_in_week if m.direction == "outgoing")

        # Messages by channel, day, and day+channel
        channels = self.db.query(Channel).all()
        por_canal = self._count_messages_by_channel(msgs_in_week, channels, conv_cache)
        por_dia = self._count_messages_by_day(msgs_in_week, week_start, week_end, zone)
        por_dia_por_canal = self._count_messages_by_day_and_channel(
            msgs_in_week, week_start, week_end, zone, channels, conv_cache
        )

        # Calculate FRT and SLA for the week
        frt_weekly = self._calculate_frt_weekly(from_dt, to_dt)
        frt_avg = (sum(frt_weekly) / len(frt_weekly)) if frt_weekly else None
        
        conv_in_week = self._get_conversations_with_first_in_in_week(from_dt, to_dt)
        pct24h = self._calculate_sla_weekly(conv_in_week)

        # Build response
        zone_name = zone.key if hasattr(zone, 'key') else str(zone)
        return OrderedDict({
            "ventana": {
                "desde_lunes": str(week_start),
                "hasta_domingo": str(week_end),
                "zona": zone_name,
            },
            "frt_avg_min": round(frt_avg, 2) if frt_avg is not None else None,
            "pct_respondido_24h": round(pct24h, 2) if pct24h is not None else None,
            "conversations": conversations,
            "mensajes_totales_in": total_in,
            "mensajes_totales_out": total_out,
            "por_canal": por_canal,
            "mensajes_por_dia": por_dia,
            "mensajes_por_dia_por_canal": por_dia_por_canal
        })

    def _build_weekly_comparison(self, semana_anterior: Dict, semana_actual: Dict) -> Dict[str, object]:
        """Calculate percentage changes between weeks."""
        def calc_change(prev, curr) -> Optional[float]:
            if prev is None or curr is None or prev == 0:
                return None if prev == 0 and curr != 0 else 0.0
            return ((curr - prev) / prev) * 100.0
        
        def calc_points_diff(prev, curr) -> Optional[float]:
            """Calculate difference in percentage points (for metrics already in %)."""
            if prev is None or curr is None:
                return None
            return curr - prev
        
        def build_comparison(key, use_points_diff=False):
            prev = semana_anterior.get(key, 0)
            curr = semana_actual.get(key, 0)
            change = calc_points_diff(prev, curr) if use_points_diff else calc_change(prev, curr)
            return {
                "semana_anterior": prev,
                "semana_actual": curr,
                "cambio_porcentual": round(change, 2) if change is not None else None
            }

        return OrderedDict({
            "mensajes_totales_in": build_comparison("mensajes_totales_in"),
            "mensajes_respondidos": build_comparison("mensajes_totales_out"),
            "tiempo_promedio_respuesta_min": build_comparison("frt_avg_min"),
            "tasa_respuesta_24h": build_comparison("pct_respondido_24h", use_points_diff=True),
            "conversaciones": build_comparison("conversations")
        })

    # ============================== HELPER METHODS ==============================
    
    def _get_week_boundaries_utc(self, week_start: date, week_end: date, zone: ZoneInfo) -> tuple:
        """Convert week boundaries from local timezone to UTC."""
        try:
            utc_zone = ZoneInfo("UTC")
        except Exception:
            from datetime import timezone as dt_timezone
            utc_zone = dt_timezone.utc
        
        from_dt = datetime.combine(week_start, time.min, tzinfo=zone).astimezone(utc_zone)
        to_dt = datetime.combine(week_end + timedelta(days=1), time.min, tzinfo=zone).astimezone(utc_zone)
        return from_dt, to_dt

    def _normalize_timestamp(self, ts: datetime, zone: ZoneInfo) -> datetime:
        """Normalize timestamp to handle both naive and aware datetimes."""
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=ZoneInfo("UTC"))
        return ts.astimezone(zone)

    def _build_conversation_cache(self, messages: list) -> Dict[int, Conversation]:
        """Build a cache of conversations to avoid N+1 queries."""
        conv_ids = set(msg.conversation_id for msg in messages)
        conversations = self.db.query(Conversation).filter(Conversation.id.in_(conv_ids)).all()
        return {conv.id: conv for conv in conversations}

    def _get_messages_by_channel(self, from_dt=None, to_dt=None) -> OrderedDict:
        """Get message counts by channel."""
        por_canal = OrderedDict()
        channels = self.db.query(Channel).all()
        
        for channel in channels:
            query = self.db.query(Message).join(Conversation).filter(
                Conversation.channel_id == channel.id
            )
            if from_dt and to_dt:
                query = query.filter(
                    and_(Message.timestamp >= from_dt, Message.timestamp < to_dt)
                )
            
            messages = query.all()
            ins = sum(1 for m in messages if m.direction == "incoming")
            outs = sum(1 for m in messages if m.direction == "outgoing")
            por_canal[channel.name] = {"in": ins, "out": outs}
        
        return por_canal

    def _count_messages_by_channel(self, messages: list, channels: list, conv_cache: Dict) -> OrderedDict:
        """Count messages by channel from pre-loaded messages."""
        por_canal = OrderedDict()
        
        # Create channel lookup
        channel_lookup = {ch.id: ch.name for ch in channels}
        
        # Initialize counters
        for channel in channels:
            por_canal[channel.name] = {"in": 0, "out": 0}
        
        # Count messages
        for msg in messages:
            conv = conv_cache.get(msg.conversation_id)
            if conv and conv.channel_id in channel_lookup:
                channel_name = channel_lookup[conv.channel_id]
                if msg.direction == "outgoing":
                    por_canal[channel_name]["out"] += 1
                else:
                    por_canal[channel_name]["in"] += 1
        
        return por_canal

    def _count_messages_by_day(self, messages: list, week_start: date, week_end: date, zone: ZoneInfo) -> OrderedDict:
        """Count messages by day."""
        por_dia = OrderedDict()
        
        # Initialize all days
        d = week_start
        while d <= week_end:
            por_dia[str(d)] = {"in": 0, "out": 0}
            d += timedelta(days=1)
        
        # Count messages
        for msg in messages:
            local_dt = self._normalize_timestamp(msg.timestamp, zone)
            day_str = str(local_dt.date())
            if day_str in por_dia:
                if msg.direction == "outgoing":
                    por_dia[day_str]["out"] += 1
                else:
                    por_dia[day_str]["in"] += 1
        
        return por_dia

    def _count_messages_by_day_and_channel(
        self, messages: list, week_start: date, week_end: date, 
        zone: ZoneInfo, channels: list, conv_cache: Dict
    ) -> OrderedDict:
        """Count messages by day and channel."""
        por_dia_por_canal = OrderedDict()
        channel_lookup = {ch.id: ch.name for ch in channels}
        
        # Initialize structure
        d = week_start
        while d <= week_end:
            por_dia_por_canal[str(d)] = OrderedDict()
            for channel in channels:
                por_dia_por_canal[str(d)][channel.name] = {"in": 0, "out": 0}
            d += timedelta(days=1)
        
        # Count messages
        for msg in messages:
            local_dt = self._normalize_timestamp(msg.timestamp, zone)
            day_str = str(local_dt.date())
            
            if day_str in por_dia_por_canal:
                conv = conv_cache.get(msg.conversation_id)
                if conv and conv.channel_id in channel_lookup:
                    channel_name = channel_lookup[conv.channel_id]
                    if msg.direction == "outgoing":
                        por_dia_por_canal[day_str][channel_name]["out"] += 1
                    else:
                        por_dia_por_canal[day_str][channel_name]["in"] += 1
        
        return por_dia_por_canal

    def _calculate_frt_all(self) -> Dict[int, Optional[int]]:
        """Calculate FRT (First Response Time) in minutes for all conversations."""
        frt_data = {}
        conversations = self.db.query(Conversation).all()
        
        for conv in conversations:
            first_in = self.db.query(Message).filter(
                and_(Message.conversation_id == conv.id, Message.direction == "incoming")
            ).order_by(Message.timestamp.asc()).first()
            
            first_out = self.db.query(Message).filter(
                and_(Message.conversation_id == conv.id, Message.direction == "outgoing")
            ).order_by(Message.timestamp.asc()).first()
            
            if first_in and first_out:
                delta = first_out.timestamp - first_in.timestamp
                frt_data[conv.id] = int(delta.total_seconds() // 60)
            else:
                frt_data[conv.id] = None
        
        return frt_data

    def _calculate_frt_weekly(self, from_dt: datetime, to_dt: datetime) -> list[int]:
        """Calculate FRT for conversations where first response is in the week."""
        from_dt_naive = from_dt.replace(tzinfo=None)
        to_dt_naive = to_dt.replace(tzinfo=None)
        
        # Get conversations with first outgoing in the week
        conv_ids = [row.conversation_id for row in self.db.query(Message.conversation_id).filter(
            and_(
                Message.direction == "outgoing",
                Message.timestamp >= from_dt_naive,
                Message.timestamp < to_dt_naive
            )
        ).distinct().all()]
        
        frt_weekly = []
        for conv_id in conv_ids:
            first_in = self.db.query(Message).filter(
                and_(Message.conversation_id == conv_id, Message.direction == "incoming")
            ).order_by(Message.timestamp.asc()).first()
            
            first_out = self.db.query(Message).filter(
                and_(Message.conversation_id == conv_id, Message.direction == "outgoing")
            ).order_by(Message.timestamp.asc()).first()
            
            if first_in and first_out:
                delta = first_out.timestamp - first_in.timestamp
                frt_weekly.append(int(delta.total_seconds() // 60))
        
        return frt_weekly

    def _get_conversations_with_first_in_in_week(self, from_dt: datetime, to_dt: datetime) -> list[int]:
        """Get conversation IDs where first incoming message is in the week."""
        from_dt_naive = from_dt.replace(tzinfo=None)
        to_dt_naive = to_dt.replace(tzinfo=None)
        
        result = []
        conversations = self.db.query(Conversation).all()
        
        for conv in conversations:
            first_in = self.db.query(Message).filter(
                and_(Message.conversation_id == conv.id, Message.direction == "incoming")
            ).order_by(Message.timestamp.asc()).first()
            
            if first_in:
                ts = first_in.timestamp.replace(tzinfo=None) if first_in.timestamp.tzinfo else first_in.timestamp
                if from_dt_naive <= ts < to_dt_naive:
                    result.append(conv.id)
        
        return result

    def _calculate_sla_weekly(self, conv_in_week: list[int]) -> Optional[float]:
        """Calculate SLA (% responded in 24h) for conversations."""
        if not conv_in_week:
            return None
        
        frt_data_all = self._calculate_frt_all()
        ok24 = sum(
            1 for conv_id in conv_in_week
            if conv_id in frt_data_all and frt_data_all[conv_id] is not None 
            and frt_data_all[conv_id] <= 1440
        )
        
        return (100.0 * ok24 / len(conv_in_week))

