from .base import BaseModel
from src.config.loader import ModelConfig
from src.utils.importing import import_class

MODEL_WRAPPERS = {
    "pytorch": "PytorchModel",
}

def create_model(config: ModelConfig) -> BaseModel:
    if config.class_path:
        model_cls = import_class(config.class_path)
        return model_cls(**config.init_kwargs)
    
    if config.type and config.type in MODEL_WRAPPERS:
        wrapper_name = MODEL_WRAPPERS[config.type]
        
        module = __import__(f"src.model.{config.type}_model", fromlist=[wrapper_name])
        wrapper_cls = getattr(module, wrapper_name)

        return wrapper_cls(
            model_path=config.path,
            device=config.device,
            **config.framework_kwargs
        )    
    raise ValueError(f"Unsupported model type: {config.type}")
