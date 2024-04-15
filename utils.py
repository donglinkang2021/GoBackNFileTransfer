import time

def get_time(timefmt:str='%Y-%m-%d_%H-%M-%S') -> str:
    return time.strftime(timefmt, time.localtime(time.time()))