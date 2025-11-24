import os
import random
import string

import redis
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.urls import URL
from app.schemas.urls import ShortenURLRequest, ShortenURLResponse

router = APIRouter(tags=["Shorten URLs"])

# Load domain from environment
SHORT_URL_DOMAIN = os.getenv("SHORT_URL_DOMAIN", "http://localhost:8000")

# Rate limiting settings
REDIS_HOST = os.getenv("REDIS_HOST", "redis")  # Docker service name
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
RATE_LIMIT = int(os.getenv("RATE_LIMIT", 5))  # requests per RATE_PERIOD
RATE_PERIOD = int(os.getenv("RATE_PERIOD", 60))  # seconds

# Redis connection
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)


def generate_short_code(length: int = 6) -> str:
    """Generate a random alphanumeric short code."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def check_rate_limit(client_ip: str):
    """Check and enforce fixed-window rate limit per client IP."""
    key = f"rate_limit:{client_ip}"
    current = r.get(key)
    if current:
        current = int(current)
        if current >= RATE_LIMIT:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded ({RATE_LIMIT}/{RATE_PERIOD}s)",
            )
        else:
            r.incr(key)
    else:
        r.set(key, 1, ex=RATE_PERIOD)


@router.post("/shorten", response_model=ShortenURLResponse)
def create_short_url(
    url_in: ShortenURLRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    # Rate limiting
    client_ip = request.client.host
    check_rate_limit(client_ip)

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
