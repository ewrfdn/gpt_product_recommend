import asyncio
import time
import logging
import inspect

logger = logging.getLogger(__name__)


def wrapper_sync(call):
    async def f(*args):
        loop = asyncio.get_running_loop()
        future = loop.run_in_executor(None, call, *args)
        return await asyncio.wait_for(future, timeout=60 * 60)

    return f


class Concurrency:
    def __init__(self, call, limit, kwargs_list, try_count=1, throw_error=False):
        self.limit = limit

        if inspect.iscoroutinefunction(call):
            self.call = wrapper_sync(call)
        else:
            self.call = call
        self.kwargs_list = kwargs_list
        self.max_try_count = try_count
        self.sem = asyncio.Semaphore(self.limit)
        self.throw_error = throw_error
        self.call_datas = []
        self.retry_list = []
        self.tasks = []
        count = 0
        for kwargs in kwargs_list:
            self.call_datas.append(
                {
                    "order": count,
                    "kwargs": kwargs,
                    "try_count": 0,
                    "result": None,
                    "error": None,
                }
            )
            count += 1

    async def call_wrapper(self, count):
        call_data = self.call_datas[count]
        kwargs = call_data["kwargs"]
        async with self.sem:
            try:
                call_data["try_count"] += 1
                res = await self.call(**kwargs)
                call_data["result"] = res
                return
            except Exception as e:
                try_count = call_data["try_count"]
                call_data["error"] = e
                if try_count >= self.max_try_count:
                    if self.throw_error:
                        raise e
                    return
                else:
                    self.retry_list.append(call_data)

    async def run(self):
        start_time = time.time()
        for count in range(len(self.call_datas)):
            self.tasks.append(self.call_wrapper(count))
        await asyncio.gather(*self.tasks)
        count = 1
        while len(self.retry_list):
            await asyncio.sleep(count * 3)
            self.tasks = []
            while len(self.retry_list):
                data = self.retry_list.pop()
                self.tasks.append(self.call_wrapper(data["order"]))
            await asyncio.gather(*self.tasks)
            count += 1
        process_time = time.time() - start_time
        logger.info(f"并发处理{len(self.call_datas)} 次 用时{process_time},")
        return [item["result"] for item in self.call_datas]

    def sync_run(self):
        return asyncio.run(self.run())
