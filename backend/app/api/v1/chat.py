"""Conversational News Assistant — WhatsApp-style AI chat for ET."""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.claude import claude_service

router = APIRouter()


class ChatMessage(BaseModel):
    message: str
    user_type: str = "retail_investor"
    context: str = ""  # optional dossier/topic context


CHAT_SYSTEM_PROMPT = """You are NarrativeAI's conversational news assistant — think of yourself as a brilliant financial journalist friend who happens to have perfect memory of all Indian business news.

Your personality:
- Sharp, concise, never boring
- Uses data and specific numbers, not vague generalities
- Explains complex topics simply when needed
- Has opinions backed by evidence (not wishy-washy)
- Knows Indian markets, regulations, companies deeply
- Can switch between casual chat and deep analysis

Rules:
- Always cite specific companies, numbers, dates when possible
- If you don't know something, say so — never hallucinate financial data
- Adapt your depth to the user type: student gets more explanation, CFO gets straight numbers
- Keep responses concise — this is a chat, not an essay (2-4 paragraphs max)
- Use bullet points for lists
- End with a follow-up question or "want me to go deeper?" when appropriate

You have access to knowledge about Indian markets, companies, regulations, and recent business events up to your training date."""


@router.post("/message")
async def chat_message(msg: ChatMessage):
    """Send a message to the AI chat assistant."""
    user_context = f"\nUser type: {msg.user_type}"
    if msg.context:
        user_context += f"\nCurrent context: {msg.context}"

    system = CHAT_SYSTEM_PROMPT + user_context

    try:
        response = await claude_service.complete(
            system_prompt=system,
            messages=[{"role": "user", "content": msg.message}],
            max_tokens=1000,
        )
        return {"response": response}
    except Exception:
        return {"response": "I need an API key to chat. Add your Anthropic key to the .env file!"}


@router.post("/stream")
async def chat_stream(msg: ChatMessage):
    """Stream a chat response for real-time feel."""
    user_context = f"\nUser type: {msg.user_type}"
    if msg.context:
        user_context += f"\nCurrent context: {msg.context}"

    system = CHAT_SYSTEM_PROMPT + user_context

    async def generate():
        try:
            async for chunk in claude_service.stream(
                system_prompt=system,
                messages=[{"role": "user", "content": msg.message}],
            ):
                yield chunk
        except Exception:
            yield "Connect API key to chat with me!"

    return StreamingResponse(generate(), media_type="text/plain")


# Quick command handlers
QUICK_COMMANDS = {
    "/market": "What's happening in the Indian market right now? Give me the key moves, top gainers/losers, and FII/DII data.",
    "/sectors": "Which sectors are hot and which are cold today? Give me the sector rotation story.",
    "/earnings": "What are the most important earnings results this week? Summarize the key numbers.",
    "/ipo": "What IPOs are coming up or currently open? Are any worth subscribing to?",
    "/rbi": "What's the latest on RBI monetary policy? When's the next meeting and what's expected?",
    "/budget": "Summarize the key budget proposals and their market impact.",
    "/global": "What global events are affecting Indian markets today?",
}


@router.get("/commands")
async def list_commands():
    """List available quick commands."""
    return {"commands": [{"command": k, "description": v[:80] + "..."} for k, v in QUICK_COMMANDS.items()]}
