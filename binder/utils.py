from time import sleep
from typing import Callable
from typing import Iterable


def execute_multiple(funcs: Iterable[Callable], *args, **kwargs):
    for func in funcs:
        func(*args, **kwargs)


class classproperty(object):  # noqa
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


def sleep_ms(ms: int):
    sleep(ms / 1000)
