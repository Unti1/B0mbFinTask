import uvicorn

from settings.config import settings


if __name__ == "__main__":
    uvicorn.run("web.app:app", host=settings.HOST, port=settings.PORT, reload=True)
