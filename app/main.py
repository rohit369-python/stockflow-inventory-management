"""FastAPI application factory and health endpoints."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api.v1.router import router

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0", description="StockFlow ERP API")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list,
                   allow_credentials=True, allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
                   allow_headers=["Authorization", "Content-Type", "Idempotency-Key"])
app.include_router(router, prefix=settings.api_v1_prefix)

@app.get("/health", tags=["operations"])
def health():
    """Liveness endpoint; dependency health is checked separately in deployment probes."""
    return {"status": "ok", "service": settings.app_name, "version": "0.1.0"}
