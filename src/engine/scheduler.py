import asyncio
from asyncio import Future
import time
from typing import Any, Optional, List
from .request import Request
from model.base import BaseModel


class BatchScheduler:
    def __init__(self, model: BaseModel, max_batch_size: int,max_delay_ms: float):
        self.model = model
        self.max_batch_size = max_batch_size
        self.max_delay_ms = max_delay_ms
        self._queue = asyncio.Queue()

    async def submit(self, input_data: Any) -> Future[Any]:
        fut = asyncio.get_running_loop().create_future()
        req = Request(input_data=input_data, future=fut, created_at=time.monotonic())

        await self._queue.put(req)
        return fut

    async def _collect_batch(self) -> List[Request]:
        batch = [] 

        first = await self._queue.get()
        batch.append(first)


        start_time = time.monotonic()
        wait_for = start_time + self.max_delay_ms / 1000

        while len(batch) < self.max_batch_size and time.monotonic() < wait_for:
            try:
                next_req = await asyncio.wait_for(self._queue.get(), timeout=wait_for - time.monotonic())
                batch.append(next_req)
            except asyncio.TimeoutError:
                break

        return batch

    async def run(self) -> None:
        while True:
            batch = await self._collect_batch()

            batch_inputs = [req.input_data for req in batch]

            try:
                batch_outputs = await asyncio.to_thread(self.model.batch_inference, batch_inputs)
            except Exception as e:
                for req in batch:
                    req.future.set_exception(e)
                continue

            for req, res in zip(batch, batch_outputs):
                req.future.set_result(res)