import os
import random
import string

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.urls import URL
from app.schemas.urls import ShortenURLRequest, ShortenURLResponse

router = APIRouter(tags=["Shorten URLs"])

# Load domain from environment
SHORT_URL_DOMAIN = os.getenv("SHORT_URL_DOMAIN", "http://localhost:8000")


def generate_short_code(length: int = 6) -> str:
    """Generate a random alphanumeric short code."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


@router.post("/shorten", response_model=ShortenURLResponse)
def create_short_url(url_in: ShortenURLRequest, db: Session = Depends(get_db)):
    # Handle custom alias if provided
    if url_in.custom_alias:
        exists = db.query(URL).filter(URL.short_code == url_in.custom_alias).first()
        if exists:
            raise HTTPException(status_code=400, detail="Custom alias already in use")
        short_code = url_in.custom_alias
    else:
        # Generate unique short code, try 5 times
        for _ in range(5):
            short_code = generate_short_code()
            if not db.query(URL).filter(URL.short_code == short_code).first():
                break
        else:
            raise HTTPException(
                status_code=500, detail="Failed to generate unique short code"
            )

    # Create URL record
    db_url = URL(
        original_url=str(url_in.original_url),
        short_code=short_code,
        custom_alias=url_in.custom_alias,
        ttl_seconds=url_in.ttl_seconds,
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    # Return full short URL
    return ShortenURLResponse(short_url=f"{SHORT_URL_DOMAIN}/{short_code}")
