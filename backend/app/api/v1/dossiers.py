from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.dossier import Dossier, DossierEvent
from app.schemas.dossier import DossierCreateIn, DossierListOut, DossierOut

router = APIRouter()


@router.get("/", response_model=DossierListOut)
async def list_dossiers(
    status: str = "active",
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List all dossiers."""
    query = (
        select(Dossier)
        .where(Dossier.status == status)
        .options(selectinload(Dossier.events))
        .offset(offset)
        .limit(limit)
        .order_by(Dossier.updated_at.desc())
    )
    result = await db.execute(query)
    dossiers = result.scalars().all()
    return DossierListOut(dossiers=dossiers, total=len(dossiers))


@router.get("/{slug}", response_model=DossierOut)
async def get_dossier(slug: str, db: AsyncSession = Depends(get_db)):
    """Get a single dossier by slug with all events."""
    query = (
        select(Dossier)
        .where(Dossier.slug == slug)
        .options(selectinload(Dossier.events))
    )
    result = await db.execute(query)
    dossier = result.scalar_one_or_none()
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier not found")
    return dossier


@router.post("/", response_model=DossierOut, status_code=201)
async def create_dossier(data: DossierCreateIn, db: AsyncSession = Depends(get_db)):
    """Create a new dossier."""
    slug = data.title.lower().replace(" ", "-").replace("'", "")
    dossier = Dossier(
        title=data.title,
        slug=slug,
        description=data.description,
        tags=data.tags,
    )
    db.add(dossier)
    await db.flush()
    await db.refresh(dossier, attribute_names=["events"])
    return dossier


@router.get("/{slug}/events")
async def get_dossier_events(
    slug: str,
    event_type: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Get events for a dossier, optionally filtered by type."""
    dossier_query = select(Dossier.id).where(Dossier.slug == slug)
    result = await db.execute(dossier_query)
    dossier_id = result.scalar_one_or_none()
    if not dossier_id:
        raise HTTPException(status_code=404, detail="Dossier not found")

    query = select(DossierEvent).where(DossierEvent.dossier_id == dossier_id)
    if event_type:
        query = query.where(DossierEvent.event_type == event_type)
    query = query.order_by(DossierEvent.occurred_at)

    result = await db.execute(query)
    events = result.scalars().all()
    return {"events": events, "total": len(events)}


@router.post("/{slug}/build")
async def build_dossier(slug: str, db: AsyncSession = Depends(get_db)):
    """Trigger the full agent pipeline for a dossier (non-streaming REST fallback)."""
    from app.agents.orchestrator import OrchestratorAgent
    from app.agents.base import AgentContext

    dossier_query = select(Dossier).where(Dossier.slug == slug)
    result = await db.execute(dossier_query)
    dossier = result.scalar_one_or_none()
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier not found")

    context = AgentContext(
        dossier_id=str(dossier.id),
        query=dossier.title,
        data={"dossier_slug": slug},
    )

    orchestrator = OrchestratorAgent()
    agent_result = await orchestrator.run(context)

    return {
        "success": agent_result.success,
        "data": agent_result.data,
        "duration_ms": agent_result.duration_ms,
    }


@router.get("/{slug}/contrarian")
async def get_contrarian(slug: str, db: AsyncSession = Depends(get_db)):
    """Get contrarian analysis for a dossier using Claude."""
    from app.services.claude import claude_service

    dossier_query = select(Dossier).where(Dossier.slug == slug).options(selectinload(Dossier.events))
    result = await db.execute(dossier_query)
    dossier = result.scalar_one_or_none()
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier not found")

    events_text = "\n".join(
        f"- [{e.occurred_at.strftime('%Y-%m-%d')}] ({e.event_type}) {e.title}: {e.summary}"
        for e in sorted(dossier.events, key=lambda x: x.occurred_at)[-15:]
    )

    prompt = f"""Story: "{dossier.title}"

Key events:
{events_text}

Analyze the narrative landscape and produce JSON with:
1. consensus: {{summary: string, key_evidence: [string], confidence: float 0-1}}
2. contrarian_view: {{summary: string, key_evidence: [string], confidence: float 0-1}}
3. evidence_comparison: [{{point: string, supports: "consensus" or "contrarian", strength: "strong"/"moderate"/"weak"}}]
4. unresolved_questions: [string]
5. verdict: string (one sentence)"""

    try:
        analysis = await claude_service.complete_json(
            system_prompt="You are an expert contrarian analyst for Indian business news. Surface credible counter-narratives with evidence.",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
        )
        return analysis
    except Exception:
        return {
            "consensus": {"summary": "Connect your Anthropic API key to see AI-powered contrarian analysis.", "key_evidence": [], "confidence": 0},
            "contrarian_view": {"summary": "Contrarian view unavailable without API key.", "key_evidence": [], "confidence": 0},
            "evidence_comparison": [],
            "unresolved_questions": [],
            "verdict": "API key required for analysis.",
        }


@router.get("/{slug}/claims")
async def get_claims(slug: str, db: AsyncSession = Depends(get_db)):
    """Get claims vs facts analysis for a dossier using Claude."""
    from app.services.claude import claude_service

    dossier_query = select(Dossier).where(Dossier.slug == slug).options(selectinload(Dossier.events))
    result = await db.execute(dossier_query)
    dossier = result.scalar_one_or_none()
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier not found")

    events_text = "\n".join(
        f"- [{e.occurred_at.strftime('%Y-%m-%d')}] {e.title}: {e.summary}"
        for e in sorted(dossier.events, key=lambda x: x.occurred_at)
    )

    prompt = f"""Story: "{dossier.title}"

Timeline:
{events_text}

Extract 5-10 claims vs confirmed facts. Return JSON array where each item has:
- claim: the assertion made (string)
- status: one of "confirmed", "invalidated", "unverified", "partially_confirmed"
- detail: evidence for the current status (string)
- source: who made the claim (string)
- date: when claim was made or resolved (string)"""

    try:
        claims = await claude_service.complete_json(
            system_prompt="You are an investigative journalist tracking claims and their outcomes in Indian business news. Be precise about what is confirmed vs unverified.",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
        )
        if isinstance(claims, dict) and "claims" in claims:
            return {"claims": claims["claims"]}
        if isinstance(claims, list):
            return {"claims": claims}
        return {"claims": []}
    except Exception:
        return {"claims": [
            {"claim": "Connect API key for AI-powered claims tracking", "status": "unverified", "detail": "Anthropic API key required", "source": "System", "date": ""},
        ]}
