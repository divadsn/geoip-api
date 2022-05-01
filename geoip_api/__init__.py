from datetime import datetime
from pathlib import Path

import aioredis

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_limiter import FastAPILimiter

from geoip_api.config import MMDB_PATH, REDIS_URL
from geoip_api.routes import router
from geoip_api.utils import get_metadata

BASE_DIR = Path(__file__).resolve().parent


def get_application() -> FastAPI:
    app = FastAPI(
        debug=False,
        title="GeoIP API",
        description="A restful GeoIP API powered by MaxMind GeoLite2.",
        version="1.2",
        license_info={
            "name": "MIT License",
            "url": "https://github.com/divadsn/geoip-api/blob/master/LICENSE",
        },
        docs_url="/docs/",
        redoc_url=None,
        openapi_url="/api/openapi.json",
    )

    redis = aioredis.from_url(REDIS_URL, encoding="utf8", decode_responses=True)

    templates = Jinja2Templates(directory=Path(BASE_DIR, "templates"))

    async def limiter_identifier(request: Request):
        forwarded = request.headers.get("X-Forwarded-For")

        if forwarded:
            ip_address = forwarded.split(",")[0]
        else:
            ip_address = request.client.host

        return ip_address

    @app.middleware("http")
    async def add_cache_control_header(request: Request, call_next):
        response = await call_next(request)

        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-cache"

        return response

    @app.on_event("startup")
    async def startup_event():
        await FastAPILimiter.init(redis, identifier=limiter_identifier)

    @app.on_event("shutdown")
    async def shutdown_event():
        await redis.close()

    @app.get("/healthcheck", include_in_schema=False)
    async def get_healthcheck():
        return {
            "success": True,
            "message": "healthy",
        }

    @app.get("/sitemap.xml", include_in_schema=False)
    async def get_sitemap() -> FileResponse:
        return FileResponse(Path(BASE_DIR, "static", "sitemap.xml"))
    
    @app.get("/", include_in_schema=False)
    async def get_index(request: Request) -> HTMLResponse:
        metadata = get_metadata(Path(MMDB_PATH, "GeoLite2-City.mmdb"))
        return templates.TemplateResponse(
            "index.html", {
                "request": request,
                "build_date": datetime.utcfromtimestamp(metadata.build_epoch),
            }
        )

    app.include_router(router)
    app.mount("/static", StaticFiles(directory=Path(BASE_DIR, "static")), name="static")

    return app


app = get_application()
