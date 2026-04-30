from fastapi import FastAPI
import asyncio
from src.model.dummy import DummyModel
from src.engine.scheduler import BatchScheduler
from .routes import create_routes

app = FastAPI()



@app.on_event("startup")
async def startup():
    model = DummyModel()
    scheduler = BatchScheduler(
        model=model,
        max_batch_size=4,
        max_delay_ms=100,
    )
    asyncio.create_task(scheduler.run()) 
    app.state.scheduler = scheduler
    create_routes(app, app.state.scheduler)

    
    