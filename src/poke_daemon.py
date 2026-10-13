import uvicorn
from fastapi import APIRouter, FastAPI

from routers import daemon, server

app = FastAPI()
router = APIRouter()

app.include_router(
    daemon.router,
    prefix="/daemon",
    tags=["daemon"],
)

app.include_router(
    server.router,
    prefix="/server",
    tags=["server"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9876, log_level="info")
