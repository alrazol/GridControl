import uvicorn
from fastapi import FastAPI
from src.core.application.api.routers import router as network_router

app = FastAPI(
    title="Network API",
    description="An API for managing and simulating networks.",
    version="1.0.0",
)

app.include_router(network_router, tags=["Network"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
