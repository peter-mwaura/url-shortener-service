import os

from fastapi import FastAPI

from app.api.analytics import router as analytics_router
from app.api.redirect import router as redirect_router
from app.api.shorten import router as shorten_router
from app.db import Base, engine
from app.models.urls import URL  # noqa: F401: register models with SQLAlchemy

app = FastAPI(title="URL Shortener Service")

# Include API routers
app.include_router(shorten_router)
app.include_router(redirect_router)
app.include_router(analytics_router)

# Read env vars for app config
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
APP_ENV = os.getenv("APP_ENV", "dev")  # default to 'dev'

# Only create tables automatically in development
if APP_ENV == "dev":
    Base.metadata.create_all(bind=engine)
