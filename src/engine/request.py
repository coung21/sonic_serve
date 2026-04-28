from dataclasses import dataclass
from typing import Any
from asyncio import Future


@dataclass
class Request:
    input_data: Any
    future: Future[Any]
    created_at: float