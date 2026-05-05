import torch
import numpy as np
from typing import List, Any
from .base import BaseModel

class PytorchModel(BaseModel):
    def __init__(self, model_path: str, device: str = "cpu", **kwargs):
        self.device = torch.device(device)
        try:
            self.model = torch.jit.load(model_path, map_location=self.device)
        except Exception as e:
            raise ValueError(f"Failed to load TorchScript model from {model_path}. Error: {e}")

        self.model.eval()

    def batch_inference(self, inputs: List[Any]) -> List[Any]:
        batch = []
        for inp in inputs:
            if isinstance(inp, torch.Tensor):
                tensor = inp.to(self.device)
            elif isinstance(inp, np.ndarray):
                tensor = torch.from_numpy(inp).to(self.device)
            elif isinstance(inp, list):
                tensor = torch.tensor(inp, dtype=torch.float32).to(self.device)
            else:
                raise ValueError(f"Unsupported input type: {type(inp)}")
            batch.append(tensor)
        
        batch = torch.stack(batch, dim=0)

        with torch.no_grad():
            output = self.model(batch)

        if isinstance(output, torch.Tensor):
            return output.detach().cpu().numpy().tolist()
        # In case it's a tuple of tensors (though dummy model returns single tensor)
        # Assuming single output tensor for now
        return output.detach().cpu().numpy().tolist()