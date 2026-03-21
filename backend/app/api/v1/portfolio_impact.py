"""Portfolio Impact Simulator — How does this news affect MY portfolio?"""

from fastapi import APIRouter

from app.services.claude import claude_service

router = APIRouter()

# Sample portfolio for demo
SAMPLE_PORTFOLIOS = {
    "aggressive_growth": {
        "name": "Aggressive Growth",
        "holdings": [
            {"symbol": "RELIANCE", "shares": 50, "avg_price": 2400, "current_price": 2543.80, "weight": 22},
            {"symbol": "INFY", "shares": 100, "avg_price": 1450, "current_price": 1567.90, "weight": 18},
            {"symbol": "ADANIENT", "shares": 20, "avg_price": 2500, "current_price": 2876.30, "weight": 10},
            {"symbol": "BAJFINANCE", "shares": 15, "avg_price": 6800, "current_price": 7234.15, "weight": 15},
            {"symbol": "TATAPOWER", "shares": 200, "avg_price": 380, "current_price": 412.50, "weight": 12},
            {"symbol": "ZOMATO", "shares": 300, "avg_price": 165, "current_price": 187.45, "weight": 8},
            {"symbol": "TCS", "shares": 30, "avg_price": 3600, "current_price": 3789.50, "weight": 15},
        ],
        "total_value": 582340,
        "total_invested": 540000,
        "overall_return_pct": 7.8,
    },
    "conservative": {
        "name": "Conservative Income",
        "holdings": [
            {"symbol": "HDFCBANK", "shares": 60, "avg_price": 1580, "current_price": 1678.40, "weight": 25},
            {"symbol": "TCS", "shares": 40, "avg_price": 3550, "current_price": 3789.50, "weight": 20},
            {"symbol": "ITC", "shares": 500, "avg_price": 420, "current_price": 458.70, "weight": 18},
            {"symbol": "RELIANCE", "shares": 30, "avg_price": 2350, "current_price": 2543.80, "weight": 15},
            {"symbol": "SBI", "shares": 150, "avg_price": 620, "current_price": 678.30, "weight": 12},
            {"symbol": "NESTLEIND", "shares": 10, "avg_price": 22000, "current_price": 23450, "weight": 10},
        ],
        "total_value": 745000,
        "total_invested": 695000,
        "overall_return_pct": 7.2,
    },
}


@router.get("/portfolios")
async def list_portfolios():
    """List sample portfolios."""
    return {
        "portfolios": [
            {"id": k, "name": v["name"], "total_value": v["total_value"], "return_pct": v["overall_return_pct"]}
            for k, v in SAMPLE_PORTFOLIOS.items()
        ]
    }


@router.get("/{portfolio_id}")
async def get_portfolio(portfolio_id: str):
    """Get portfolio details."""
    portfolio = SAMPLE_PORTFOLIOS.get(portfolio_id)
    if not portfolio:
        return {"error": "Portfolio not found"}
    return portfolio


@router.post("/{portfolio_id}/impact")
async def simulate_impact(portfolio_id: str, news_event: str):
    """Simulate how a news event would impact a specific portfolio."""
    portfolio = SAMPLE_PORTFOLIOS.get(portfolio_id)
    if not portfolio:
        return {"error": "Portfolio not found"}

    holdings_text = "\n".join(
        f"  - {h['symbol']}: {h['shares']} shares @ ₹{h['current_price']} ({h['weight']}% weight)"
        for h in portfolio["holdings"]
    )

    prompt = f"""A user has this portfolio:
{holdings_text}
Total value: ₹{portfolio['total_value']:,}

News event: "{news_event}"

Analyze the impact on this SPECIFIC portfolio:

1. **Overall Impact Score**: -5 (devastating) to +5 (windfall), with explanation
2. **Stock-by-Stock Impact**:
   For each holding, estimate:
   - Direction: up/down/neutral
   - Estimated price impact: percentage
   - Why: one-line reasoning
3. **Portfolio Value Change**: estimated ₹ change and new total
4. **Immediate Action**: What should this investor do RIGHT NOW (hold/buy more/reduce/hedge)?
5. **Risk Alert**: Any position that's now dangerously exposed?
6. **Opportunity**: Any position that could benefit if you add?

Be specific with numbers. This is personalized financial intelligence, not generic advice."""

    try:
        analysis = await claude_service.complete(
            system_prompt="You are a portfolio strategist at a wealth management firm. Give specific, actionable analysis tied to the user's actual holdings. Use real numbers.",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
        )
        return {
            "portfolio": portfolio_id,
            "event": news_event,
            "analysis": analysis,
            "holdings": portfolio["holdings"],
        }
    except Exception:
        return {"portfolio": portfolio_id, "event": news_event, "analysis": "Connect API key for portfolio impact analysis."}
