from pydantic import BaseModel, Field, model_validator
import yaml
from typing import Optional, List, Dict, Any
from pathlib import Path


class ModelConfig(BaseModel):
    class_path: Optional[str] = None
    init_kwargs: Dict[str, Any] = Field(default_factory=dict)
    type: Optional[str] = None
    path: Optional[str] = None
    device: str = "cpu"
    input_shape: Optional[List[int]] = None
    framework_kwargs: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode='after')
    def check_model_source(self):
        if not self.class_path and not (self.type and self.path):
            raise ValueError(
                "Must provide either 'class_path' (custom code) "
                "or both 'type' and 'path' (no-code model)."
            )
        return self

class SchedulerConfig(BaseModel):
    max_batch_size: int = Field(..., gt=0)
    max_delay_ms: float = Field(..., gt=0)
    adaptive: bool = False
    target_latency_ms: float = Field(100.0, gt=0)
    min_delay_ms: float = Field(5.0, gt=0)
    max_delay_ms_cap: float = Field(500.0, gt=0)
    pid_kp: float = 0.1
    pid_ki: float = 0.01
    pid_kd: float = 0.05
    max_queue_size: int = Field(1000, gt=0)

class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    request_timeout: int = 30

class Config(BaseModel):
    model: ModelConfig
    scheduler: SchedulerConfig
    server: ServerConfig

def load_config(file_path: str | Path) -> Config:
    path = Path(file_path).resolve()
    
    if not path.is_file():
        raise FileNotFoundError(f"Config file not found: {path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        config_dict = yaml.safe_load(f)
        
    return Config.model_validate(config_dict)


if __name__ == '__main__':
    from src.utils.logger import get_logger, setup_logger
    setup_logger(debug=True)
    logger = get_logger(__name__)
    config = load_config("./src/config/default.yaml")
    logger.info(f"Loaded config: {config}")
    
