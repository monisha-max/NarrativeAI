"""Smart Earnings Decoder — AI auto-analyzes quarterly results."""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.services.claude import claude_service

router = APIRouter()

# Sample earnings data (in production, would come from BSE/NSE filings API)
SAMPLE_EARNINGS = {
    "RELIANCE": {
        "company": "Reliance Industries Ltd",
        "quarter": "Q3 FY26",
        "revenue": 265432,  # crores
        "revenue_yoy": 12.3,
        "net_profit": 19878,
        "net_profit_yoy": 8.7,
        "ebitda_margin": 16.2,
        "eps": 29.34,
        "key_segments": [
            {"name": "O2C", "revenue": 156000, "growth": 5.2},
            {"name": "Digital Services (Jio)", "revenue": 38000, "growth": 18.5},
            {"name": "Retail", "revenue": 52000, "growth": 22.1},
            {"name": "Oil & Gas", "revenue": 19432, "growth": -3.4},
        ],
        "analyst_estimate_beat": True,
        "estimate_beat_pct": 4.2,
    },
    "TCS": {
        "company": "Tata Consultancy Services",
        "quarter": "Q3 FY26",
        "revenue": 63028,
        "revenue_yoy": 5.6,
        "net_profit": 12380,
        "net_profit_yoy": 3.2,
        "ebitda_margin": 24.8,
        "eps": 33.89,
        "key_segments": [
            {"name": "BFSI", "revenue": 21000, "growth": 6.2},
            {"name": "Retail & CPG", "revenue": 10500, "growth": 4.1},
            {"name": "Technology & Media", "revenue": 8200, "growth": 8.7},
            {"name": "Manufacturing", "revenue": 7800, "growth": 2.3},
        ],
        "analyst_estimate_beat": False,
        "estimate_beat_pct": -1.8,
    },
}


@router.get("/companies")
async def list_earnings():
    """List available earnings reports."""
    return {
        "companies": [
            {"symbol": k, "company": v["company"], "quarter": v["quarter"]}
            for k, v in SAMPLE_EARNINGS.items()
        ]
    }


@router.get("/decode/{symbol}")
async def decode_earnings(symbol: str, user_type: str = "retail_investor"):
    """AI-decode earnings for a specific company, adapted to user type."""
    symbol = symbol.upper()
    if symbol not in SAMPLE_EARNINGS:
        return {"error": f"No earnings data for {symbol}"}

    data = SAMPLE_EARNINGS[symbol]

    segments_text = "\n".join(
        f"  - {s['name']}: ₹{s['revenue']:,} Cr ({s['growth']:+.1f}% YoY)" for s in data["key_segments"]
    )

    prompt = f"""Decode these quarterly earnings for a {user_type}:

Company: {data['company']} ({symbol})
Quarter: {data['quarter']}
Revenue: ₹{data['revenue']:,} Cr ({data['revenue_yoy']:+.1f}% YoY)
Net Profit: ₹{data['net_profit']:,} Cr ({data['net_profit_yoy']:+.1f}% YoY)
EBITDA Margin: {data['ebitda_margin']}%
EPS: ₹{data['eps']}
Analyst Estimate: {"Beat by" if data['analyst_estimate_beat'] else "Missed by"} {abs(data['estimate_beat_pct'])}%

Segment Breakdown:
{segments_text}

Provide:
1. **TL;DR** (2 sentences max — was this quarter good or bad and why?)
2. **The Good** (2-3 bullet points of positive signals)
3. **The Concern** (2-3 bullet points of worries)
4. **Hidden Signal** (one thing most people will miss in these numbers)
5. **What It Means For You** (tailored to {user_type}: portfolio impact, career signal, or business implication)
6. **Numbers to Watch Next Quarter** (2-3 specific metrics)

Adapt complexity to {user_type}. If student, explain terms. If CFO, go deep on margins."""

    try:
        analysis = await claude_service.complete(
            system_prompt=f"You are an expert equity research analyst writing for a {user_type}. Be specific, use the actual numbers, highlight what matters.",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200,
        )
        return {"symbol": symbol, "data": data, "analysis": analysis, "user_type": user_type}
    except Exception:
        return {"symbol": symbol, "data": data, "analysis": "Connect API key for AI earnings analysis.", "user_type": user_type}


@router.post("/compare")
async def compare_earnings(symbols: list[str]):
    """Compare earnings across multiple companies."""
    companies = {s.upper(): SAMPLE_EARNINGS.get(s.upper()) for s in symbols if s.upper() in SAMPLE_EARNINGS}

    if len(companies) < 2:
        return {"error": "Need at least 2 valid companies to compare"}

    comparison_text = ""
    for symbol, data in companies.items():
        comparison_text += f"\n{symbol} ({data['company']}):\n  Revenue: ₹{data['revenue']:,} Cr ({data['revenue_yoy']:+.1f}%)\n  Profit: ₹{data['net_profit']:,} Cr ({data['net_profit_yoy']:+.1f}%)\n  Margin: {data['ebitda_margin']}%\n"

    prompt = f"""Compare these earnings results head-to-head:
{comparison_text}

Produce:
1. Who won this quarter and why (2 sentences)
2. Comparative table: revenue growth, profit growth, margins
3. Which stock looks better for next quarter and why
4. The one metric that separates them"""

    try:
        analysis = await claude_service.complete(
            system_prompt="You are a comparative equity analyst. Be direct about winners and losers.",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
        )
        return {"companies": companies, "comparison": analysis}
    except Exception:
        return {"companies": companies, "comparison": "Connect API key for comparison analysis."}
