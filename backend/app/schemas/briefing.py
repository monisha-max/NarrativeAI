from pydantic import BaseModel


class BriefingRequest(BaseModel):
    prompt_key: str | None = None  # from guided prompts
    custom_query: str | None = None  # free-form
    user_type: str = "retail_investor"
    language: str = "en"
    perspective: dict | None = None


class BriefingResponse(BaseModel):
    prompt_used: str
    response_text: str
    sources: list[dict] = []
    follow_up_prompts: list[str] = []
