import aioredis

from fastapi import FastAPI, Request
from fastapi_limiter import FastAPILimiter

from geoip_api.config import REDIS_URL
from geoip_api.routes import router

app = FastAPI(
    debug=False,
    title="GeoIP API",
    description="A restful GeoIP API powered by MaxMind GeoLite2.",
    version="1.0",
    docs_url="/",
    redoc_url=None,
    openapi_url="/api/openapi.json",
)

app.include_router(router)

redis = aioredis.from_url(REDIS_URL, encoding="utf8", decode_responses=True)


async def limiter_identifier(request: Request):
    forwarded = request.headers.get("X-Forwarded-For")

    if forwarded:
        ip = forwarded.split(",")[0]
    else:
        ip = request.client.host

    return ip


@app.on_event("startup")
async def startup_event():
    await FastAPILimiter.init(redis, identifier=limiter_identifier)


@app.on_event("shutdown")
async def shutdown_event():
    await redis.close()