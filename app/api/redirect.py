from fastapi import APIRouter

router = APIRouter(tags=["Redirect"])


@router.get("/{short_code}")
def redirect_short_url(short_code: str):
    return {"message": f"This would redirect short code {short_code}"}
