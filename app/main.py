from fastapi import FastAPI

from app.api.analytics import router as analytics_router
from app.api.redirect import router as redirect_router
from app.api.shorten import router as shorten_router

app = FastAPI(title="URL Shortener Service")

app.include_router(shorten_router)
app.include_router(redirect_router)
app.include_router(analytics_router)
