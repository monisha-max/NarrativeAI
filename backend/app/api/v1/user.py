from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import FollowedDossier, User
from app.schemas.user import PerspectiveUpdateIn, UserCreateIn, UserOut

router = APIRouter()


@router.post("/", response_model=UserOut, status_code=201)
async def create_user(data: UserCreateIn, db: AsyncSession = Depends(get_db)):
    """Create a new user."""
    user = User(
        username=data.username,
        display_name=data.display_name,
        user_type=data.user_type,
        language=data.language,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.get("/{username}", response_model=UserOut)
async def get_user(username: str, db: AsyncSession = Depends(get_db)):
    """Get user by username."""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{username}/perspective")
async def update_perspective(
    username: str,
    data: PerspectiveUpdateIn,
    db: AsyncSession = Depends(get_db),
):
    """Update user's perspective dial settings."""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.perspective_settings = data.model_dump()
    return {"status": "updated", "perspective": user.perspective_settings}


@router.post("/{username}/follow/{dossier_slug}")
async def follow_dossier(
    username: str,
    dossier_slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Follow a dossier."""
    from app.models.dossier import Dossier

    user_result = await db.execute(select(User).where(User.username == username))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    dossier_result = await db.execute(select(Dossier).where(Dossier.slug == dossier_slug))
    dossier = dossier_result.scalar_one_or_none()
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier not found")

    follow = FollowedDossier(user_id=user.id, dossier_id=dossier.id)
    db.add(follow)
    return {"status": "following", "dossier": dossier_slug}
