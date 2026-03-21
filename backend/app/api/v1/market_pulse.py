"""Market Pulse Live — Real-time market dashboard with AI commentary."""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.services.claude import claude_service

router = APIRouter()

# Simulated market data (in production, would come from NSE/BSE APIs)
MARKET_DATA = {
    "indices": [
        {"name": "SENSEX", "value": 76432.18, "change": 342.56, "change_pct": 0.45, "trend": "up"},
        {"name": "NIFTY 50", "value": 23178.45, "change": 98.12, "change_pct": 0.42, "trend": "up"},
        {"name": "NIFTY BANK", "value": 49876.32, "change": -124.56, "change_pct": -0.25, "trend": "down"},
        {"name": "NIFTY IT", "value": 34521.87, "change": 267.34, "change_pct": 0.78, "trend": "up"},
    ],
    "top_gainers": [
        {"symbol": "TATAPOWER", "price": 412.50, "change_pct": 4.2, "volume": "12.3M"},
        {"symbol": "ADANIENT", "price": 2876.30, "change_pct": 3.8, "volume": "8.7M"},
        {"symbol": "BAJFINANCE", "price": 7234.15, "change_pct": 2.9, "volume": "5.1M"},
        {"symbol": "RELIANCE", "price": 2543.80, "change_pct": 2.1, "volume": "15.6M"},
        {"symbol": "INFY", "price": 1567.90, "change_pct": 1.8, "volume": "9.4M"},
    ],
    "top_losers": [
        {"symbol": "ZOMATO", "price": 187.45, "change_pct": -3.1, "volume": "18.2M"},
        {"symbol": "PAYTM", "price": 432.10, "change_pct": -2.7, "volume": "11.5M"},
        {"symbol": "TATAMOTORS", "price": 678.90, "change_pct": -1.9, "volume": "7.8M"},
    ],
    "sectors": [
        {"name": "IT", "change_pct": 0.78, "mood": "bullish"},
        {"name": "Banking", "change_pct": -0.25, "mood": "cautious"},
        {"name": "Pharma", "change_pct": 0.45, "mood": "stable"},
        {"name": "Auto", "change_pct": -0.12, "mood": "mixed"},
        {"name": "Energy", "change_pct": 1.2, "mood": "bullish"},
        {"name": "FMCG", "change_pct": 0.3, "mood": "stable"},
        {"name": "Metals", "change_pct": -0.8, "mood": "bearish"},
        {"name": "Realty", "change_pct": 1.5, "mood": "bullish"},
    ],
    "fii_dii": {
        "fii_net": -1234.56,  # crores
        "dii_net": 2345.67,
        "fii_trend": "selling",
        "dii_trend": "buying",
    },
}


@router.get("/data")
async def get_market_data():
    """Get current market pulse data."""
    return MARKET_DATA


@router.get("/ai-commentary")
async def get_ai_commentary():
    """Get AI-generated market commentary based on current data."""
    prompt = f"""Current Indian market snapshot:
- Sensex: {MARKET_DATA['indices'][0]['value']} ({MARKET_DATA['indices'][0]['change_pct']:+.2f}%)
- Nifty: {MARKET_DATA['indices'][1]['value']} ({MARKET_DATA['indices'][1]['change_pct']:+.2f}%)
- Bank Nifty: {MARKET_DATA['indices'][2]['value']} ({MARKET_DATA['indices'][2]['change_pct']:+.2f}%)
- FII: Net {MARKET_DATA['fii_dii']['fii_trend']} (₹{abs(MARKET_DATA['fii_dii']['fii_net']):.0f} Cr)
- DII: Net {MARKET_DATA['fii_dii']['dii_trend']} (₹{MARKET_DATA['fii_dii']['dii_net']:.0f} Cr)
- Top sectors: Energy (+1.2%), Realty (+1.5%), IT (+0.78%)
- Weak sectors: Metals (-0.8%), Banking (-0.25%)

Generate a 3-paragraph AI market commentary:
1. What's driving the market today (2-3 sentences)
2. Key sector rotation and FII/DII dynamics (2-3 sentences)
3. What to watch for the rest of the day (2-3 sentences)

Be specific, use data, sound like a sharp market analyst. No generic filler."""

    try:
        commentary = await claude_service.complete(
            system_prompt="You are a senior market analyst at ET Markets. Write sharp, data-driven commentary. Use specific numbers. Be concise.",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )
        return {"commentary": commentary}
    except Exception as e:
        return {"commentary": "Market commentary unavailable. Connect your API key for AI-powered analysis."}


@router.post("/sector-deep-dive")
async def sector_deep_dive(sector: str = "IT"):
    """AI deep-dive into a specific sector's performance."""
    prompt = f"""Provide a deep-dive analysis of the Indian {sector} sector today:

1. Key drivers (what's moving the sector)
2. Top 3 stocks to watch and why
3. Risk factors
4. Outlook for the next week

Be specific to Indian markets. Use real company names and current dynamics."""

    try:
        analysis = await claude_service.complete(
            system_prompt="You are an Indian equity research analyst. Be specific, data-driven, and actionable.",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
        )
        return {"sector": sector, "analysis": analysis}
    except Exception:
        return {"sector": sector, "analysis": "Connect API key for sector analysis."}
