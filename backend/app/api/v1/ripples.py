from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.dossier import Dossier
from app.models.ripple import RippleAlert, RippleConnection

router = APIRouter()


@router.get("/{dossier_slug}")
async def get_ripples(dossier_slug: str, db: AsyncSession = Depends(get_db)):
    """Get cross-story ripple connections for a dossier."""
    dossier_result = await db.execute(select(Dossier.id).where(Dossier.slug == dossier_slug))
    dossier_id = dossier_result.scalar_one_or_none()
    if not dossier_id:
        return {"connections": [], "alerts": []}

    # Get connections where this dossier is source or target
    conn_result = await db.execute(
        select(RippleConnection).where(
            (RippleConnection.source_dossier_id == dossier_id)
            | (RippleConnection.target_dossier_id == dossier_id)
        )
    )
    connections = conn_result.scalars().all()

    # Get active alerts
    alert_result = await db.execute(
        select(RippleAlert)
        .where(
            (RippleAlert.target_dossier_id == dossier_id)
            & (RippleAlert.status == "active")
        )
        .order_by(RippleAlert.created_at.desc())
    )
    alerts = alert_result.scalars().all()

    return {"connections": connections, "alerts": alerts}
