import time
from functools import wraps

import psutil


def timing(f):

    def timed(*args, **kw):

        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        print(f'func:{f.__name__} args:{args} took: {te-ts:.8f} sec')
        return result

    return timed


def measure_memory_usage(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        pid = psutil.Process()
        initial_memory = pid.memory_info().rss

        result = func(*args, **kwargs)

        final_memory = pid.memory_info().rss
        memory_used = final_memory - initial_memory
        memory_used_mb = memory_used / (1024 ** 2)

        print(f"Memory used by {func.__name__}: {memory_used_mb:.6f} MB")

        return result

    return wrapper