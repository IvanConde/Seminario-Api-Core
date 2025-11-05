"""Analytics service for calculating metrics from MySQL database."""
from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from sqlalchemy.sql import case
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
            # Fallback if zoneinfo not available
            logger.warning(f"Could not load timezone: {e}. Using UTC.")
            zone = ZoneInfo("UTC")
        
        today = datetime.now(zone).date()

        # Monday to Sunday
        this_week_start = today - timedelta(days=today.weekday())  # Monday
        this_week_end = this_week_start + timedelta(days=6)  # Sunday
        last_week_start = this_week_start - timedelta(weeks=1)
        last_week_end = this_week_start - timedelta(days=1)

        r: Dict[str, object] = OrderedDict()
        r["general"] = self._build_general_metrics(zone)
        
        semana_anterior = self._build_weekly_metrics(last_week_start, last_week_end, zone)
        semana_actual = self._build_weekly_metrics(this_week_start, this_week_end, zone)
        
        r["semana_anterior"] = semana_anterior
        r["semana_actual"] = semana_actual
        r["comparativa_semanal"] = self._build_weekly_comparison(semana_anterior, semana_actual)
        
        return r

    # ============================== GENERAL (histórico completo) ==============================
    def _build_general_metrics(self, zone: ZoneInfo) -> Dict[str, object]:
        """Build general metrics from all conversations and messages."""
        # Get all conversations
        total_conv = self.db.query(Conversation).count()

        # Calculate FRT (First Response Time) for each conversation
        # FRT = first_response_at - first_received_at
        frt_data = self._calculate_frt_all()
        frts_min = [frt for frt in frt_data.values() if frt is not None]
        frt_avg: Optional[float] = None if not frts_min else (sum(frts_min) / len(frts_min))

        # SLA 24h: conversations responded within 24 hours (1440 minutes)
        ok24 = sum(1 for frt in frts_min if frt <= 1440)
        pct24h = None if total_conv == 0 else (100.0 * ok24 / total_conv)

        # Count messages by direction
        total_in = self.db.query(Message).filter(Message.direction == "incoming").count()
        total_out = self.db.query(Message).filter(Message.direction == "outgoing").count()

        # Messages by channel
        por_canal = OrderedDict()
        channels = self.db.query(Channel).all()
        for channel in channels:
            ins = self.db.query(Message).join(Conversation).filter(
                and_(
                    Conversation.channel_id == channel.id,
                    Message.direction == "incoming"
                )
            ).count()
            outs = self.db.query(Message).join(Conversation).filter(
                and_(
                    Conversation.channel_id == channel.id,
                    Message.direction == "outgoing"
                )
            ).count()
            por_canal[channel.name] = {"in": ins, "out": outs}

        g: Dict[str, object] = OrderedDict()
        g["frt_avg_min"] = round(frt_avg, 2) if frt_avg is not None else None
        g["pct_respondido_24h"] = round(pct24h, 2) if pct24h is not None else None
        g["conversations_total"] = total_conv
        g["mensajes_totales_in"] = total_in
        g["mensajes_totales_out"] = total_out
        g["por_canal_total"] = por_canal
        return g

    # ============================== SEMANAL (lunes–domingo) ==============================
    def _build_weekly_metrics(self, week_start: date, week_end: date, zone: ZoneInfo) -> Dict[str, object]:
        """Build weekly metrics for a specific week."""
        # Ventana [from, to) en UTC
        try:
            utc_zone = ZoneInfo("UTC")
        except Exception:
            from datetime import timezone as dt_timezone
            utc_zone = dt_timezone.utc
            
        from_dt = datetime.combine(week_start, time.min, tzinfo=zone).astimezone(utc_zone)
        to_dt = datetime.combine(week_end + timedelta(days=1), time.min, tzinfo=zone).astimezone(utc_zone)

        # Messages in the week
        # Handle both timezone-aware and naive timestamps in DB
        msgs_in_week = self.db.query(Message).filter(
            and_(
                Message.timestamp >= from_dt.replace(tzinfo=None) if from_dt.tzinfo else from_dt,
                Message.timestamp < to_dt.replace(tzinfo=None) if to_dt.tzinfo else to_dt
            )
        ).all()

        # Conversaciones por semana = conversaciones distintas con actividad en la semana
        conversations = len(set(msg.conversation_id for msg in msgs_in_week))

        total_in = sum(1 for m in msgs_in_week if m.direction == "incoming")
        total_out = sum(1 for m in msgs_in_week if m.direction == "outgoing")

        # Por canal
        por_canal = OrderedDict()
        channels = self.db.query(Channel).all()
        for channel in channels:
            # Query messages in week for this channel
            msgs_channel = self.db.query(Message).join(Conversation).filter(
                and_(
                    Conversation.channel_id == channel.id,
                    Message.timestamp >= from_dt,
                    Message.timestamp < to_dt
                )
            ).all()
            ins = sum(1 for m in msgs_channel if m.direction == "incoming")
            outs = sum(1 for m in msgs_channel if m.direction == "outgoing")
            por_canal[channel.name] = {"in": ins, "out": outs}

        # Mensajes por día (IN/OUT)
        por_dia = OrderedDict()
        d = week_start
        while d <= week_end:
            por_dia[str(d)] = {"in": 0, "out": 0}
            d += timedelta(days=1)
        
        for m in msgs_in_week:
            # Handle timezone-aware and naive timestamps
            if m.timestamp.tzinfo is None:
                # Naive datetime, assume UTC
                ts_utc = m.timestamp.replace(tzinfo=ZoneInfo("UTC"))
            else:
                ts_utc = m.timestamp
            local_dt = ts_utc.astimezone(zone)
            ld = str(local_dt.date())
            if ld in por_dia:
                if m.direction == "outgoing":
                    por_dia[ld]["out"] += 1
                else:
                    por_dia[ld]["in"] += 1

        # FRT semanal: se atribuye a la semana del OUT (first_response_at en la semana)
        frt_weekly = self._calculate_frt_weekly(from_dt, to_dt)
        frt_avg = None if not frt_weekly else (sum(frt_weekly) / len(frt_weekly))

        # SLA duro semanal: denominador = conv con primer IN en la semana
        conv_in_week = self._get_conversations_with_first_in_in_week(from_dt, to_dt)
        total_conv_week = len(conv_in_week)
        
        # Calculate OK24 for conversations in week
        frt_data_all = self._calculate_frt_all()
        ok24week = sum(
            1 for conv_id in conv_in_week
            if conv_id in frt_data_all and frt_data_all[conv_id] is not None and frt_data_all[conv_id] <= 1440
        )
        pct24h = None if total_conv_week == 0 else (100.0 * ok24week / total_conv_week)

        out: Dict[str, object] = OrderedDict()
        # Get zone name safely - ZoneInfo has 'key' attribute, timezone objects don't
        if hasattr(zone, 'key'):
            zone_name = zone.key
        else:
            zone_name = str(zone)
        out["ventana"] = {
            "desde_lunes": str(week_start),
            "hasta_domingo": str(week_end),
            "zona": zone_name,
        }
        out["frt_avg_min"] = round(frt_avg, 2) if frt_avg is not None else None
        out["pct_respondido_24h"] = round(pct24h, 2) if pct24h is not None else None
        out["conversations"] = conversations
        out["mensajes_totales_in"] = total_in
        out["mensajes_totales_out"] = total_out
        out["por_canal"] = por_canal
        out["mensajes_por_dia"] = por_dia
        return out

    # ============================== COMPARATIVA SEMANAL ==============================
    def _build_weekly_comparison(self, semana_anterior: Dict[str, object], semana_actual: Dict[str, object]) -> Dict[str, object]:
        """Calculate percentage changes between weeks."""
        def calcular_cambio_porcentual(valor_anterior, valor_actual) -> Optional[float]:
            """Calcula el % de cambio: ((actual - anterior) / anterior) * 100"""
            if valor_anterior is None or valor_actual is None:
                return None
            if valor_anterior == 0:
                if valor_actual == 0:
                    return 0.0
                return None  # No se puede calcular % cuando se divide por 0
            return ((valor_actual - valor_anterior) / valor_anterior) * 100.0

        comparativa: Dict[str, object] = OrderedDict()
        
        # Mensajes totales (entrantes)
        msg_in_anterior = semana_anterior.get("mensajes_totales_in", 0)
        msg_in_actual = semana_actual.get("mensajes_totales_in", 0)
        comparativa["mensajes_totales_in"] = {
            "semana_anterior": msg_in_anterior,
            "semana_actual": msg_in_actual,
            "cambio_porcentual": round(calcular_cambio_porcentual(msg_in_anterior, msg_in_actual), 2) if calcular_cambio_porcentual(msg_in_anterior, msg_in_actual) is not None else None
        }
        
        # Mensajes respondidos (salientes)
        msg_out_anterior = semana_anterior.get("mensajes_totales_out", 0)
        msg_out_actual = semana_actual.get("mensajes_totales_out", 0)
        comparativa["mensajes_respondidos"] = {
            "semana_anterior": msg_out_anterior,
            "semana_actual": msg_out_actual,
            "cambio_porcentual": round(calcular_cambio_porcentual(msg_out_anterior, msg_out_actual), 2) if calcular_cambio_porcentual(msg_out_anterior, msg_out_actual) is not None else None
        }
        
        # Tiempo promedio de respuesta (FRT en minutos)
        frt_anterior = semana_anterior.get("frt_avg_min")
        frt_actual = semana_actual.get("frt_avg_min")
        comparativa["tiempo_promedio_respuesta_min"] = {
            "semana_anterior": frt_anterior,
            "semana_actual": frt_actual,
            "cambio_porcentual": round(calcular_cambio_porcentual(frt_anterior, frt_actual), 2) if calcular_cambio_porcentual(frt_anterior, frt_actual) is not None else None
        }
        
        # Tasa de respuesta (% respondido en 24h)
        tasa_anterior = semana_anterior.get("pct_respondido_24h")
        tasa_actual = semana_actual.get("pct_respondido_24h")
        comparativa["tasa_respuesta_24h"] = {
            "semana_anterior": tasa_anterior,
            "semana_actual": tasa_actual,
            "cambio_porcentual": round(calcular_cambio_porcentual(tasa_anterior, tasa_actual), 2) if calcular_cambio_porcentual(tasa_anterior, tasa_actual) is not None else None
        }
        
        # Conversaciones totales
        conv_anterior = semana_anterior.get("conversations", 0)
        conv_actual = semana_actual.get("conversations", 0)
        comparativa["conversaciones"] = {
            "semana_anterior": conv_anterior,
            "semana_actual": conv_actual,
            "cambio_porcentual": round(calcular_cambio_porcentual(conv_anterior, conv_actual), 2) if calcular_cambio_porcentual(conv_anterior, conv_actual) is not None else None
        }
        
        return comparativa

    # ============================== HELPER METHODS ==============================
    def _calculate_frt_all(self) -> Dict[int, Optional[int]]:
        """Calculate FRT (First Response Time) in minutes for all conversations."""
        frt_data = {}
        
        # Get all conversations
        conversations = self.db.query(Conversation).all()
        
        for conv in conversations:
            # Get first incoming message
            first_incoming = self.db.query(Message).filter(
                and_(
                    Message.conversation_id == conv.id,
                    Message.direction == "incoming"
                )
            ).order_by(Message.timestamp.asc()).first()
            
            # Get first outgoing message
            first_outgoing = self.db.query(Message).filter(
                and_(
                    Message.conversation_id == conv.id,
                    Message.direction == "outgoing"
                )
            ).order_by(Message.timestamp.asc()).first()
            
            if first_incoming and first_outgoing:
                # Handle timezone-aware and naive timestamps
                received = first_incoming.timestamp
                response = first_outgoing.timestamp
                
                if received.tzinfo is None:
                    received = received.replace(tzinfo=None)
                if response.tzinfo is None:
                    response = response.replace(tzinfo=None)
                
                delta = response - received
                frt_minutes = int(delta.total_seconds() // 60)
                frt_data[conv.id] = frt_minutes
            else:
                frt_data[conv.id] = None

        return frt_data

    def _calculate_frt_weekly(self, from_dt: datetime, to_dt: datetime) -> list[int]:
        """Calculate FRT for conversations where first_response_at is in the week."""
        # Convert to naive datetime for DB comparison
        from_dt_naive = from_dt.replace(tzinfo=None) if from_dt.tzinfo else from_dt
        to_dt_naive = to_dt.replace(tzinfo=None) if to_dt.tzinfo else to_dt
        
        # Get conversations where first outgoing message is in the week
        outgoing_in_week = self.db.query(Message.conversation_id).filter(
            and_(
                Message.direction == "outgoing",
                Message.timestamp >= from_dt_naive,
                Message.timestamp < to_dt_naive
            )
        ).distinct().all()
        
        conv_ids = [row.conversation_id for row in outgoing_in_week]
        
        frt_weekly = []
        for conv_id in conv_ids:
            # Get first incoming for this conversation
            first_incoming = self.db.query(Message).filter(
                and_(
                    Message.conversation_id == conv_id,
                    Message.direction == "incoming"
                )
            ).order_by(Message.timestamp.asc()).first()
            
            # Get first outgoing (should be in week)
            first_outgoing = self.db.query(Message).filter(
                and_(
                    Message.conversation_id == conv_id,
                    Message.direction == "outgoing"
                )
            ).order_by(Message.timestamp.asc()).first()
            
            if first_incoming and first_outgoing:
                received = first_incoming.timestamp
                response = first_outgoing.timestamp
                
                # Handle timezone
                if received.tzinfo is None:
                    received = received.replace(tzinfo=None)
                if response.tzinfo is None:
                    response = response.replace(tzinfo=None)
                
                delta = response - received
                frt_minutes = int(delta.total_seconds() // 60)
                frt_weekly.append(frt_minutes)

        return frt_weekly

    def _get_conversations_with_first_in_in_week(self, from_dt: datetime, to_dt: datetime) -> list[int]:
        """Get conversation IDs where first incoming message is in the week."""
        # Convert to naive datetime for DB comparison
        from_dt_naive = from_dt.replace(tzinfo=None) if from_dt.tzinfo else from_dt
        to_dt_naive = to_dt.replace(tzinfo=None) if to_dt.tzinfo else to_dt
        
        # Get all conversations
        conversations = self.db.query(Conversation).all()
        result = []
        
        for conv in conversations:
            # Get first incoming message for this conversation
            first_incoming = self.db.query(Message).filter(
                and_(
                    Message.conversation_id == conv.id,
                    Message.direction == "incoming"
                )
            ).order_by(Message.timestamp.asc()).first()
            
            if first_incoming:
                first_ts = first_incoming.timestamp
                # Handle timezone
                if first_ts.tzinfo:
                    first_ts = first_ts.replace(tzinfo=None)
                
                if first_ts >= from_dt_naive and first_ts < to_dt_naive:
                    result.append(conv.id)

        return result

