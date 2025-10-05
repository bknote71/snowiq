import threading
from typing import Callable
from utils.logger import logger


def start_daemon(target: Callable, *args, **kwargs) -> threading.Thread:
    t = threading.Thread(target=target, args=args, kwargs=kwargs, daemon=True)
    t.start()
    return t
