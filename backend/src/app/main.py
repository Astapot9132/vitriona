from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse

from di_container import container
import src.app.api.auth as auth_api
from src.app.api.admin import router as admin_router
from src.app.api.auth import router as auth_router
from src.app.api.client import router as client_router
from src.app.api.meta import router as meta_router
from src.app.core.config import get_settings


settings = get_settings()
storage_public_dir = Path(settings.storage_dir).joinpath("public")
storage_public_dir.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    container.wire(modules=[auth_api])
    yield
    await container.api_engine().dispose()
    container.unwire()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, settings.app_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def csrf_middleware(request: Request, call_next):
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        try:
            container.security_service().require_csrf(request)
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return await call_next(request)


app.include_router(meta_router)
app.include_router(auth_router, prefix="/api")
app.include_router(client_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.mount("/storage", StaticFiles(directory=str(storage_public_dir), html=True), name="storage")
