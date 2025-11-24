from typing import Optional

from pydantic import BaseModel, HttpUrl


class ShortenURLRequest(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None
    ttl_seconds: Optional[int] = None


class ShortenURLResponse(BaseModel):
    short_url: str
