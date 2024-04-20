import time
from typing import Tuple

def get_time(timefmt:str='%Y-%m-%d_%H-%M-%S') -> str:
    return time.strftime(timefmt, time.localtime(time.time()))

def addr_to_str(addr:Tuple[str, int]):
    return f"{addr[0]}_{addr[1]}"