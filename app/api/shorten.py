from fastapi import APIRouter

router = APIRouter(tags=["Shorten URLs"])


@router.post("/shorten")
def create_short_url():
    return {"message": "This is the shorten URL endpoint"}
