from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi.responses import RedirectResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend


from redis import asyncio as aioredis

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


from settings.config import settings


from web.router import router as main_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


# Создаём FastAPI приложение
app = FastAPI(lifespan=lifespan)

@app.get('/')
async def redirect_to_docs():
    # Т.к. разработка идет только под апи то сразу сделаем редирект на документацию
    return RedirectResponse('/docs')

app.include_router(main_router)



# Создаем обработчики лимитеров
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
