from pathlib import Path

import aioredis

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter

from geoip_api.config import REDIS_URL
from geoip_api.routes import router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    debug=False,
    title="GeoIP API",
    description="A restful GeoIP API powered by MaxMind GeoLite2.",
    version="1.0",
    license_info={
        "name": "MIT License",
        "url": "https://github.com/divadsn/geoip-api/blob/master/LICENSE",
    },
    docs_url="/docs/",
    redoc_url=None,
    openapi_url="/api/openapi.json",
)

app.include_router(router)
app.mount("/", StaticFiles(directory=Path(BASE_DIR, "static"), html=True))

redis = aioredis.from_url(REDIS_URL, encoding="utf8", decode_responses=True)


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
