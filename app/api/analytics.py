from fastapi import APIRouter

router = APIRouter(tags=["Analytics"])


@router.get("/analytics/{short_code}")
def get_analytics(short_code: str):
    return {"message": f"This would return analytics for short code {short_code}"}
