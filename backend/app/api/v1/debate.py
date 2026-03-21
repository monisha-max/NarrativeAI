"""News Debate Arena — AI-powered bull vs bear live debate on any story."""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.services.claude import claude_service

router = APIRouter()


def _bull_instruction(round_num: int) -> str:
    if round_num == 1:
        return "Open strong with your thesis"
    elif round_num == 2:
        return "Address the bear's weaknesses and strengthen your case"
    return "Close with your strongest evidence and a clear verdict"


def _bear_instruction(round_num: int) -> str:
    if round_num == 1:
        return "Open with the biggest risk everyone is ignoring"
    elif round_num == 2:
        return "Dismantle the bull's strongest point"
    return "Close with your strongest warning and verdict"


@router.post("/start")
async def start_debate(topic: str, rounds: int = 3):
    """Start a bull vs bear AI debate on any market topic."""
    debate_rounds = []

    for round_num in range(1, rounds + 1):
        # Bull argument
        bull_context = "\n".join(
            f"Round {r['round']}: Bull said: {r['bull'][:200]}... Bear said: {r['bear'][:200]}..."
            for r in debate_rounds
        )

        bull_prompt = f"""You are the BULL in a market debate about: "{topic}"

{'Previous rounds:' + bull_context if bull_context else 'This is Round 1.'}

Round {round_num}/{rounds}. Make your BULLISH case:
- Use specific data points, company names, and numbers
- If later rounds, directly counter the bear's arguments
- Be passionate but evidence-based
- {_bull_instruction(round_num)}

Keep to 3-4 sentences. Be punchy."""

        try:
            bull_arg = await claude_service.complete(
                system_prompt="You are a confident bull market analyst. You see opportunity everywhere but back it with data. Indian market focus.",
                messages=[{"role": "user", "content": bull_prompt}],
                max_tokens=300,
            )
        except Exception:
            bull_arg = "Bull case unavailable — connect API key."

        # Bear argument
        bear_prompt = f"""You are the BEAR in a market debate about: "{topic}"

The bull just said: "{bull_arg}"

{'Previous rounds:' + bull_context if bull_context else ''}

Round {round_num}/{rounds}. Make your BEARISH counter-argument:
- Directly address the bull's points
- Use specific risk data, historical precedents, valuation concerns
- Be skeptical but intelligent — not doom-and-gloom
- {_bear_instruction(round_num)}

Keep to 3-4 sentences. Be sharp."""

        try:
            bear_arg = await claude_service.complete(
                system_prompt="You are a rigorous bear market analyst. You see risks others miss. Indian market focus. You're not pessimistic — you're realistic.",
                messages=[{"role": "user", "content": bear_prompt}],
                max_tokens=300,
            )
        except Exception:
            bear_arg = "Bear case unavailable — connect API key."

        debate_rounds.append({
            "round": round_num,
            "bull": bull_arg,
            "bear": bear_arg,
        })

    # Final verdict
    all_arguments = "\n\n".join(
        f"Round {r['round']}:\nBull: {r['bull']}\nBear: {r['bear']}" for r in debate_rounds
    )

    try:
        verdict = await claude_service.complete(
            system_prompt="You are a neutral market judge. Evaluate both sides fairly based on evidence quality.",
            messages=[{"role": "user", "content": f"""After this debate on "{topic}":

{all_arguments}

Deliver your verdict in exactly this format:
1. **Winner**: Bull or Bear (and by how much: narrow/clear/decisive)
2. **Strongest argument**: Which single point was most compelling
3. **Weakest argument**: Which point was least supported
4. **The truth**: Your balanced 2-sentence assessment
5. **What to do**: One actionable sentence for investors"""}],
            max_tokens=400,
        )
    except Exception:
        verdict = "Verdict unavailable — connect API key."

    return {
        "topic": topic,
        "rounds": debate_rounds,
        "verdict": verdict,
    }


@router.post("/quick-take")
async def quick_take(topic: str):
    """Get a quick bull vs bear one-liner on any topic."""
    prompt = f"""Topic: "{topic}"

Give me exactly:
BULL (1 sentence): [bullish take with one key data point]
BEAR (1 sentence): [bearish take with one key risk]
VERDICT (1 sentence): [which side has stronger evidence right now]"""

    try:
        result = await claude_service.complete(
            system_prompt="You are a balanced market analyst. Be extremely concise. Indian market focus.",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
        return {"topic": topic, "take": result}
    except Exception:
        return {"topic": topic, "take": "Connect API key for quick takes."}
