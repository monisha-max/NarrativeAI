from fastapi import APIRouter

from app.api.v1.dossiers import router as dossiers_router
from app.api.v1.briefing import router as briefing_router
from app.api.v1.entities import router as entities_router
from app.api.v1.search import router as search_router
from app.api.v1.stories import router as stories_router
from app.api.v1.ripples import router as ripples_router
from app.api.v1.user import router as user_router
from app.api.v1.delta import router as delta_router
from app.api.v1.market_pulse import router as market_pulse_router
from app.api.v1.earnings import router as earnings_router
from app.api.v1.rumor_tracker import router as rumor_tracker_router
from app.api.v1.portfolio_impact import router as portfolio_impact_router
from app.api.v1.debate import router as debate_router
from app.api.v1.chat import router as chat_router
from app.api.v1.ws import router as ws_router

v1_router = APIRouter()

v1_router.include_router(dossiers_router, prefix="/dossiers", tags=["dossiers"])
v1_router.include_router(briefing_router, prefix="/briefing", tags=["briefing"])
v1_router.include_router(entities_router, prefix="/entities", tags=["entities"])
v1_router.include_router(search_router, prefix="/search", tags=["search"])
v1_router.include_router(stories_router, prefix="/stories", tags=["stories"])
v1_router.include_router(ripples_router, prefix="/ripples", tags=["ripples"])
v1_router.include_router(user_router, prefix="/users", tags=["users"])
v1_router.include_router(delta_router, prefix="/delta", tags=["delta"])
v1_router.include_router(market_pulse_router, prefix="/market-pulse", tags=["market-pulse"])
v1_router.include_router(earnings_router, prefix="/earnings", tags=["earnings"])
v1_router.include_router(rumor_tracker_router, prefix="/rumors", tags=["rumors"])
v1_router.include_router(portfolio_impact_router, prefix="/portfolio", tags=["portfolio"])
v1_router.include_router(debate_router, prefix="/debate", tags=["debate"])
v1_router.include_router(chat_router, prefix="/chat", tags=["chat"])
v1_router.include_router(ws_router, tags=["websocket"])
