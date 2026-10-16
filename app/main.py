from fastapi import FastAPI

from app.models.processed_message import ProcessedMessage  # noqa: F401
from app.routes.webhook import router

app = FastAPI()

app.include_router(router)


@app.get("/")
def read_root():
    return {"status": "Application running"}
