"""Rumor vs Reality — Verification engine tracking market rumors to outcomes."""

from datetime import datetime, timezone
from fastapi import APIRouter

from app.services.claude import claude_service

router = APIRouter()

# Curated rumor database (in production, would be crowd-sourced + AI-detected)
RUMORS = [
    {
        "id": "r1",
        "rumor": "Reliance to acquire Disney+ Hotstar India operations",
        "source": "Multiple media reports",
        "date_surfaced": "2024-08-15",
        "status": "confirmed",
        "date_resolved": "2024-11-14",
        "reality": "Reliance-Viacom18 and Disney Star merger completed. Combined entity JioStar launched.",
        "market_impact": "RIL stock +3.2% on confirmation",
        "accuracy_score": 0.9,
        "category": "M&A",
    },
    {
        "id": "r2",
        "rumor": "RBI to cut rates by 50 bps in February 2025",
        "source": "Analyst speculation, social media",
        "date_surfaced": "2025-01-10",
        "status": "partially_true",
        "date_resolved": "2025-02-07",
        "reality": "RBI cut by only 25 bps, not 50 bps as rumored. Dovish stance confirmed though.",
        "market_impact": "Mild disappointment, Bank Nifty flat",
        "accuracy_score": 0.5,
        "category": "Policy",
    },
    {
        "id": "r3",
        "rumor": "Byju's to receive $500M rescue funding from UAE investors",
        "source": "Anonymous sources in business media",
        "date_surfaced": "2024-05-20",
        "status": "debunked",
        "date_resolved": "2024-07-16",
        "reality": "No rescue funding materialized. NCLT insolvency proceedings initiated instead.",
        "market_impact": "N/A (unlisted)",
        "accuracy_score": 0.0,
        "category": "Funding",
    },
    {
        "id": "r4",
        "rumor": "Government considering cryptocurrency ban in India",
        "source": "Unnamed government sources",
        "date_surfaced": "2025-01-28",
        "status": "unresolved",
        "date_resolved": None,
        "reality": "Budget 2026 mentioned 'regulatory framework for digital assets' but no ban announced. Situation remains ambiguous.",
        "market_impact": "Crypto exchanges saw 15% volume drop on rumor",
        "accuracy_score": None,
        "category": "Regulation",
    },
    {
        "id": "r5",
        "rumor": "TCS to announce major layoffs in Q4 FY26",
        "source": "Social media, anonymous employee posts",
        "date_surfaced": "2026-02-15",
        "status": "unresolved",
        "date_resolved": None,
        "reality": "TCS management denied in earnings call. Attrition remains at 12.5%. No formal layoff announcement.",
        "market_impact": "TCS stock dipped 1.8% on rumor day",
        "accuracy_score": None,
        "category": "Corporate",
    },
    {
        "id": "r6",
        "rumor": "Adani Group to delist Adani Wilmar from exchanges",
        "source": "Market speculation after promoter stake increase",
        "date_surfaced": "2025-11-10",
        "status": "confirmed",
        "date_resolved": "2026-01-22",
        "reality": "Adani Group completed delisting offer for Adani Wilmar at ₹305/share.",
        "market_impact": "Stock surged 18% to delisting price",
        "accuracy_score": 0.85,
        "category": "M&A",
    },
]


@router.get("/all")
async def get_all_rumors():
    """Get all tracked rumors."""
    return {
        "rumors": RUMORS,
        "stats": {
            "total": len(RUMORS),
            "confirmed": sum(1 for r in RUMORS if r["status"] == "confirmed"),
            "debunked": sum(1 for r in RUMORS if r["status"] == "debunked"),
            "partially_true": sum(1 for r in RUMORS if r["status"] == "partially_true"),
            "unresolved": sum(1 for r in RUMORS if r["status"] == "unresolved"),
        },
    }


@router.get("/{rumor_id}")
async def get_rumor(rumor_id: str):
    """Get details on a specific rumor."""
    rumor = next((r for r in RUMORS if r["id"] == rumor_id), None)
    if not rumor:
        return {"error": "Rumor not found"}
    return rumor


@router.post("/analyze")
async def analyze_rumor(rumor_text: str):
    """AI analysis of a market rumor — credibility assessment."""
    prompt = f"""Analyze this market rumor for credibility:

Rumor: "{rumor_text}"

Provide:
1. **Credibility Score**: 0-100% based on source quality, historical patterns, and plausibility
2. **Evidence For**: what supports this rumor being true
3. **Evidence Against**: what suggests this is false
4. **Historical Pattern**: similar rumors in the past and what happened
5. **Market Impact If True**: how would markets react
6. **Market Impact If False**: how would markets react
7. **Verification Checklist**: 3-5 specific things to watch that would confirm or deny this
8. **Verdict**: Most likely true / Likely false / Insufficient evidence / Plausible but unconfirmed

Return as structured analysis."""

    try:
        analysis = await claude_service.complete(
            system_prompt="You are a market intelligence analyst specializing in rumor verification for Indian markets. Be rigorous, cite patterns, and never present speculation as fact.",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
        )
        return {"rumor": rumor_text, "analysis": analysis}
    except Exception:
        return {"rumor": rumor_text, "analysis": "Connect API key for AI rumor analysis."}
