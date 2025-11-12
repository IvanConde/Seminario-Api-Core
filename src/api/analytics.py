"""Analytics API endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict

from src.database import get_db
from src.services.analytics_service import AnalyticsService
from src.utils.logger import get_logger
from src.api.auth import get_current_user

logger = get_logger(__name__)
router = APIRouter()


@router.get("/analytics/dashboard")
async def get_dashboard(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Obtener dashboard con métricas generales y semanales.
    Requiere un usuario autenticado sin restricción de rol.
    
    Retorna:
    - general: Métricas históricas completas
    - semana_anterior: Métricas de la semana pasada (lunes-domingo)
    - semana_actual: Métricas de esta semana (lunes-domingo)
    - comparativa_semanal: Comparación porcentual entre semanas
    """
    try:
        service = AnalyticsService(db)
        dashboard_data = service.dashboard()
        logger.info("Dashboard metrics generated")
        return dashboard_data
    except Exception as e:
        logger.error(f"Error generating dashboard: {str(e)}", exc_info=True)
        raise

