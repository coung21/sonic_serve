import asyncio
from fastapi import APIRouter, HTTPException, FastAPI
from .schemas import InferenceRequest, InferenceResponse
from src.engine.exceptions import QueueFullError

def create_routes(app: FastAPI, scheduler):
    router = APIRouter()

    @router.post("/inference", response_model=InferenceResponse)
    async def inference_handler(request: InferenceRequest):
        try:
            future = await scheduler.submit(request.data)
            result = await asyncio.wait_for(future, timeout=10.0)
            return InferenceResponse(results=result)
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Inference timeout")
        except QueueFullError:
            raise HTTPException(status_code=503, detail="Queue is full")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @router.get("/ready")
    async def ready_check(app: FastAPI):
        if app.state.scheduler.is_ready():
            return {"status": "ready"}
        raise HTTPException(status_code=503, detail="Server is not ready")

    @router.get("/health")
    async def health_check():
        return {"status": "ok"}

    app.include_router(router)