from fastapi import APIRouter, HTTPException, FastAPI
from .schemas import InferenceRequest, InferenceResponse
import asyncio

def create_routes(app: FastAPI, scheduler):
    router = APIRouter()

    @router.post("/inference", response_model=InferenceResponse)
    async def inference_handler(request: InferenceRequest):
        future = await scheduler.submit(request.data)

        try:
            result = await asyncio.wait_for(future, timeout=10.0)
            return InferenceResponse(results=result)
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Inference timeout")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @router.get("/health")
    async def health_check():
        return {"status": "ok"}

    app.include_router(router)