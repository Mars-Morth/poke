import uvicorn
from fastapi import APIRouter, FastAPI

from logic.context import DaemonContext
from routers import daemon, server

app = FastAPI()
router = APIRouter()

app.state.context = DaemonContext()

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
    uvicorn.run(app, host="0.0.0.0", port=9876, log_level="info")
