"""Multi-dimensional sentiment scoring for NarrativeAI."""

from app.services.claude import claude_service
import structlog

logger = structlog.get_logger()


def compute_sentiment(text: str) -> dict:
    """Compute basic multi-dimensional sentiment scores using heuristics.

    This is a fast, synchronous fallback. For more accurate scoring,
    use compute_sentiment_llm() which uses Claude.
    """
    if not text:
        return {
            "market_confidence": 0.0,
            "regulatory_heat": 0.0,
            "media_tone": 0.0,
            "stakeholder_sentiment": 0.0,
        }

    text_lower = text.lower()

    # Market confidence keywords
    positive_market = ["growth", "profit", "revenue", "beat expectations", "rally", "upgrade", "bullish", "recovery", "expansion"]
    negative_market = ["loss", "crash", "downgrade", "bearish", "default", "crisis", "insolvency", "bankruptcy", "write-down"]

    market_score = 0.0
    for word in positive_market:
        if word in text_lower:
            market_score += 0.15
    for word in negative_market:
        if word in text_lower:
            market_score -= 0.15
    market_score = max(-1.0, min(1.0, market_score))

    # Regulatory heat
    regulatory_words = ["sebi", "rbi", "nclt", "enforcement", "penalty", "probe", "investigation", "compliance", "violation", "moratorium", "ed ", "cbi"]
    reg_score = 0.0
    for word in regulatory_words:
        if word in text_lower:
            reg_score += 0.15
    reg_score = min(1.0, reg_score)

    # Media tone
    positive_tone = ["success", "innovation", "milestone", "record", "breakthrough", "strong", "impressive"]
    negative_tone = ["scandal", "fraud", "controversy", "crisis", "collapse", "failure", "concern", "worrying"]

    tone_score = 0.0
    for word in positive_tone:
        if word in text_lower:
            tone_score += 0.15
    for word in negative_tone:
        if word in text_lower:
            tone_score -= 0.15
    tone_score = max(-1.0, min(1.0, tone_score))

    # Stakeholder sentiment (similar to media tone but with different signals)
    stakeholder_score = (market_score + tone_score) / 2.0

    return {
        "market_confidence": round(market_score, 3),
        "regulatory_heat": round(reg_score, 3),
        "media_tone": round(tone_score, 3),
        "stakeholder_sentiment": round(stakeholder_score, 3),
    }


async def compute_sentiment_llm(text: str, context: str = "") -> dict:
    """Compute multi-dimensional sentiment using Claude for high accuracy."""
    prompt = f"""Analyze the sentiment of this business news text along four dimensions.

Context: {context}
Text: {text[:2000]}

Score each dimension:
- market_confidence: -1 (extreme fear/negative outlook) to 1 (extreme greed/positive outlook)
- regulatory_heat: 0 (no regulatory concern) to 1 (active enforcement/intervention)
- media_tone: -1 (very negative coverage) to 1 (very positive coverage)
- stakeholder_sentiment: -1 (hostile stakeholders) to 1 (supportive stakeholders)

Return JSON only: {{"market_confidence": float, "regulatory_heat": float, "media_tone": float, "stakeholder_sentiment": float}}"""

    try:
        return await claude_service.complete_json(
            system_prompt="You are a financial sentiment analyzer specialized in Indian markets. Return precise numerical scores.",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
    except Exception as e:
        logger.warning("sentiment.llm.error", error=str(e))
        return compute_sentiment(text)
