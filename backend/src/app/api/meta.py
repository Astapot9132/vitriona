from fastapi import APIRouter, Depends

from src.app.core.dependencies import maybe_user_context


router = APIRouter()


@router.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/api/meta/bootstrap", tags=["meta"])
async def bootstrap(context: dict = Depends(maybe_user_context)) -> dict:
    user = context["user"]
    return {
        "auth": {
            "user": (
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "affise_password": user.affise_password,
                    "affise_country": user.affise_country,
                    "affise_id": user.affise_id,
                }
                if user
                else None
            ),
            "is_admin": context["is_admin"],
            "impersonating": context["impersonating"],
            "csrf_token": context["csrf_token"],
        }
    }
