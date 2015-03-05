import time

def timed_exec(method):
    start_time = time.time()
    result = method()
    return result, (time.time() - start_time)/60



