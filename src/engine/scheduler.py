import asyncio
from asyncio import Future
import time
from typing import Any, Optional, List
from .request import Request
from .exceptions import QueueFullError
from src.model.base import BaseModel


class BatchScheduler:
    def __init__(self, model: BaseModel, max_batch_size: int,max_delay_ms: float, max_queue_size: int):
        self.model = model
        self.max_batch_size = max_batch_size
        self.max_delay_ms = max_delay_ms
        self.max_queue_size = max_queue_size
        self._queue = asyncio.Queue()
        self._shutting_down = False
        self._stop_event = asyncio.Event()

    async def submit(self, input_data: Any) -> Future[Any]:
        if self._shutting_down:
            raise RuntimeError("Server is shutting down")

        fut = asyncio.get_running_loop().create_future()
        req = Request(input_data=input_data, future=fut, created_at=time.monotonic())
        
        if self._queue.qsize() >= self.max_queue_size:
            raise QueueFullError("Queue is full")

        await self._queue.put(req)
        return fut

    async def _collect_batch(self) -> List[Request]:
        batch = [] 

        first = await self._queue.get()
        if first is None:
            return batch
        batch.append(first)


        start_time = time.monotonic()
        wait_for = start_time + self.max_delay_ms / 1000

   
        while len(batch) < self.max_batch_size and time.monotonic() < wait_for:
            try:
                remaining = wait_for - time.monotonic()
                if remaining <= 0:
                    break
                next_req = await asyncio.wait_for(self._queue.get(), timeout=remaining)
                if next_req is None:
                    break
                batch.append(next_req)
            except asyncio.TimeoutError:
                break

        return batch

    async def run(self) -> None:
        while not self._stop_event.is_set():
            batch = await self._collect_batch()

            if not batch:
                continue

            batch_inputs = [req.input_data for req in batch]

            try:
                batch_outputs = await asyncio.to_thread(self.model.batch_inference, batch_inputs)

                assert len(batch_outputs) == len(batch_inputs), "mismatched results length"

                for req, res in zip(batch, batch_outputs):
                    if not req.future.done():
                        req.future.set_result(res)

            except Exception as e:
                for req in batch:
                    req.future.set_exception(e)
                continue    

    async def shutdown(self):
        self._shutting_down = True
        
        while not self._queue.empty():
            await asyncio.sleep(1)
            
        self._stop_event.set()
        
        try:
            self._queue.put_nowait(None)
        except asyncio.QueueFull:
            pass
