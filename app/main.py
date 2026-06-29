from fastapi import FastAPI
from app.db.database import Base, engine
from app.routes.webhook import router

app = FastAPI()

app.include_router(router)

Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"status": "Application running"}
