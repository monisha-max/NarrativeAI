from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agents.prompts.briefing import GUIDED_PROMPTS
from app.schemas.briefing import BriefingRequest, BriefingResponse
from app.services.claude import claude_service
from app.agents.prompts.synthesis import BRIEFING_SYSTEM_PROMPT

router = APIRouter()


@router.get("/prompts")
async def list_guided_prompts():
    """List available guided prompts for the Briefing Room."""
    return {
        key: {"label": val["label"], "key": key}
        for key, val in GUIDED_PROMPTS.items()
    }


@router.post("/{slug}", response_model=BriefingResponse)
async def get_briefing(slug: str, request: BriefingRequest):
    """Get an AI briefing for a dossier."""
    # Determine the prompt
    if request.prompt_key and request.prompt_key in GUIDED_PROMPTS:
        prompt_text = GUIDED_PROMPTS[request.prompt_key]["prompt"]
        prompt_label = GUIDED_PROMPTS[request.prompt_key]["label"]
    elif request.custom_query:
        prompt_text = request.custom_query
        prompt_label = "Custom query"
    else:
        return BriefingResponse(
            prompt_used="none",
            response_text="Please provide a prompt key or custom query.",
        )

    # Build context-aware system prompt
    system = f"""{BRIEFING_SYSTEM_PROMPT}

User type: {request.user_type}
Language: {request.language}
Dossier: {slug}"""

    response = await claude_service.complete(
        system_prompt=system,
        messages=[{"role": "user", "content": prompt_text}],
    )

    return BriefingResponse(
        prompt_used=prompt_label,
        response_text=response,
        follow_up_prompts=["What changed today?", "Who is exposed?", "What if I'm wrong?"],
    )


@router.post("/{slug}/stream")
async def stream_briefing(slug: str, request: BriefingRequest):
    """Stream a briefing response for progressive rendering."""
    prompt_text = ""
    if request.prompt_key and request.prompt_key in GUIDED_PROMPTS:
        prompt_text = GUIDED_PROMPTS[request.prompt_key]["prompt"]
    elif request.custom_query:
        prompt_text = request.custom_query

    system = f"""{BRIEFING_SYSTEM_PROMPT}

User type: {request.user_type}
Language: {request.language}
Dossier: {slug}"""

    async def generate():
        async for chunk in claude_service.stream(
            system_prompt=system,
            messages=[{"role": "user", "content": prompt_text}],
        ):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")


VERNACULAR_SYSTEM_PROMPT = """You are a business news translator for NarrativeAI, specializing in culturally adapted Indian language translation.

Rules:
- Do NOT do literal word-for-word translation
- EXPLAIN financial jargon in the target language instead of transliterating English terms
- Use LOCAL analogies and references the target audience would understand
- Keep all NUMBERS, COMPANY NAMES, and DATES in their original form (don't translate "₹10,000 crore" or "Byju's")
- Adapt complexity: if the user is a student, use simpler language; if a CFO, use professional register
- Add brief parenthetical explanations for complex financial concepts
- Maintain the same structure and emphasis as the original
- The translation should feel like it was WRITTEN in that language by a native financial journalist, not translated"""

LANGUAGE_NAMES = {
    "hi": "Hindi (हिन्दी)",
    "te": "Telugu (తెలుగు)",
    "ta": "Tamil (தமிழ்)",
    "bn": "Bengali (বাংলা)",
    "mr": "Marathi (मराठी)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "gu": "Gujarati (ગુજરાતી)",
    "ml": "Malayalam (മലയാളം)",
}


class TranslateRequest(BaseModel):
    text: str
    target_lang: str = "hi"
    user_type: str = "retail_investor"


@router.post("/translate")
async def translate_content(request: TranslateRequest):
    """Culturally adapt business news content to Indian languages."""
    lang_name = LANGUAGE_NAMES.get(request.target_lang, request.target_lang)

    prompt = f"""Translate the following business news content into {lang_name}.

User profile: {request.user_type}

Content to translate:
---
{request.text}
---

Remember:
- Culturally adapt, don't literally translate
- Explain jargon in {lang_name} with parenthetical context
- Keep company names, numbers, and dates as-is
- Make it feel native to a {lang_name}-speaking business reader"""

    try:
        translated = await claude_service.complete(
            system_prompt=VERNACULAR_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
        )
        return {
            "original": request.text,
            "translated": translated,
            "target_lang": request.target_lang,
            "lang_name": lang_name,
        }
    except Exception as e:
        return {
            "original": request.text,
            "translated": "Translation unavailable — connect your Anthropic API key.",
            "target_lang": request.target_lang,
            "error": str(e),
        }
