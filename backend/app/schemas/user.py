from uuid import UUID

from pydantic import BaseModel


class UserOut(BaseModel):
    id: UUID
    username: str
    display_name: str | None = None
    user_type: str
    language: str
    perspective_settings: dict | None = None

    model_config = {"from_attributes": True}


class UserCreateIn(BaseModel):
    username: str
    display_name: str | None = None
    user_type: str = "retail_investor"
    language: str = "en"


class PerspectiveUpdateIn(BaseModel):
    risk: float = 0.5          # 0=conservative, 1=aggressive
    stakeholder: str = "investor"  # investor, founder, employee, regulator
    sentiment: float = 0.5     # 0=bear, 1=bull
    geography: float = 0.5     # 0=india-first, 1=global
    depth: float = 0.5         # 0=quick-take, 1=deep-evidence
