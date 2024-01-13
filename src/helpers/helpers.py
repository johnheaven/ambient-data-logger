import asyncio
import functools
from typing import Callable, Iterator, Iterable, Tuple

### WORKER DECORATOR TO TURN FUNCTION INTO ASYNC WORKER ###

def worker(func, add_none=True, flatten=False):
    async def worker_wrapper(func, queue_in: asyncio.Queue | Iterator, queue_out: asyncio.Queue, *args, add_none, flatten, test_inner=False, **kwargs):
        # for testing the inner function only
        if test_inner: return func(*args, **kwargs)

        while True:
            try:
                input = await queue_in.get() if isinstance(queue_in, asyncio.Queue) else next(queue_in)
            except StopIteration:
                # this only applies if we are using an Iterator as once it's exhausted, there's no way it's going to be refilled
                break
            result = await func(input, *args, **kwargs)
            # only add the result if add_none is True or the result is non-None. Dunno why the .get is necessary... otherwise it breaks during testing.
            if (result is not None) or kwargs.get("add_none", add_none):
                # if the function returns an iterable, this allows the option of adding the items in the iterable (not the whole iterable itself) to the queue
                if not kwargs.get("flatten", flatten):
                    results = [result]
                else:
                    results = result
                for result in results:
                    await queue_out.put(result)
            if isinstance(queue_in, asyncio.Queue):
                queue_in.task_done()

    worker = functools.partial(worker_wrapper, func, add_none=add_none, flatten=flatten)
    functools.update_wrapper(worker, func)
    return worker

### ASYNC CHAIN FOR EASILY CHAINING WORKERS TOGETHER ###

async def async_chain(*functions: Callable | Tuple[Tuple[Callable, int]], queue_in: asyncio.Queue | Iterable, queue_out: asyncio.Queue, tg: asyncio.TaskGroup) -> Iterable[asyncio.Task]:
    # chain a series of async tasks with queues, so the first function consumes the input queue and the last one feeds the output queue
    queues = [queue_in] + [asyncio.Queue() for _ in range(len(functions) - 1)] + [queue_out]
    # create a task for each functions, passing in queue 1 and queue 2 to function 1, queue 2 and queue 3 to function 2 etc.
    tasks = []
    for i in range(len(functions)):
        # unpack the function depending on whether it's a tuple or function. if it's a tuple, the first item is the function, the second the number of workers/instances
        if isinstance(functions[i], Tuple):
            f, n_workers = functions[i]
        else:
            f, n_workers = functions[i], 1
        q_in = queues[i]
        q_out = queues[i+1]
        tasks = [tg.create_task(f(queue_in=q_in, queue_out=q_out)) for _ in range(n_workers)]
    return tasks

### SHOW OUTPUT WORKER ###

async def show_output(result):
    # print output without consuming
    print(result)
    return result
show_outputs = worker(show_output)

### GET ENV VARS ###

def get_env_vars(env_vars: Iterable, return_type: str='dict') -> Iterable | dict:
    """Returns a dictionary or tuple of the specified environment variables
    Args:
        env_vars (list or SupportsIndex): The names of env vars to return.
        return_type: whether to return a generator or dict
    Returns:
        dict or Iterable: The env vars
    """
    from dotenv import load_dotenv
    import os

    load_dotenv()
    
    if return_type == 'dict':
        return {env_var: os.environ[env_var] for env_var in env_vars}
    else:
        return (os.environ[env_var] for env_var in env_vars)

### GET SQL ENGINE FROM ENVVARS ###

def get_sql_engine():
    from sqlalchemy import create_engine
    from sqlalchemy.engine import URL
    from helpers.general import get_env_vars
    from urllib.parse import quote_plus as urlquote
    
    DB_DRIVER, DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME = get_env_vars(
        ['DB_DRIVER',
        'DB_USER',
        'DB_PASS',
        'DB_HOST',
        'DB_PORT',
        'DB_NAME'],
        return_type='tuple')

    DB_STRING = URL.create(
        drivername=DB_DRIVER,
        username=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        database=DB_NAME,
        port=DB_PORT
    )

    engine = create_engine(DB_STRING)
    return engine