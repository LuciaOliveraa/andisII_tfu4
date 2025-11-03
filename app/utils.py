from tenacity import retry, wait_fixed, stop_after_attempt
from functools import wraps

def retry_on_exception(attempts=3, wait=1):
    def deco(fn):
        @retry(wait=wait_fixed(wait), stop=stop_after_attempt(attempts))
        @wraps(fn)
        def wrapped(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapped
    return deco