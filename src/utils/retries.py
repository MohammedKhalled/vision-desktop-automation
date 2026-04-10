import time

def retry(fn, attempts, delay):
    for _ in range(attempts):
        result = fn()
        if result:
            return result
        time.sleep(delay)
    return None
