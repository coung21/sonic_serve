from fastapi import FastAPI
import os
from pathlib import Path
import asyncio
from src.model.dummy import DummyModel
from src.engine.scheduler import BatchScheduler
from .routes import create_routes
from src.utils.importing import import_class
from src.model.factory import create_model



# @app.on_event("startup")
# async def startup():
#     default_config_path = Path(__file__).parent.parent / "config" / "default.yaml"
#     config_path = os.getenv("ZONIC_CONFIG", str(default_config_path))
#     config = load_config(config_path)

#     model_class = import_class(config.model.class_path)
#     model = model_class(**config.model.init_kwargs)
#     scheduler = BatchScheduler(
#         model=model,
#         max_batch_size=config.scheduler.max_batch_size,
#         max_delay_ms=config.scheduler.max_delay_ms,
#     )
#     asyncio.create_task(scheduler.run()) 
#     app.state.scheduler = scheduler
#     create_routes(app, app.state.scheduler)

from contextlib import asynccontextmanager

def create_app(config):
    model = create_model(config.model)
        
    scheduler = BatchScheduler(
        model=model,
        max_batch_size=config.scheduler.max_batch_size,
        max_delay_ms=config.scheduler.max_delay_ms,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        task = asyncio.create_task(scheduler.run())
        yield
        task.cancel()

    app = FastAPI(lifespan=lifespan)
    app.state.scheduler = scheduler
    create_routes(app, app.state.scheduler)
    
    return app