import logging
from typing import Type, Iterable

from binder.binder import Binder
from binder.rp_line import RPLine


def require_active_samp(func):
    def wrapper_func(binder: Type[Binder]):
        active_samp = binder.active_samp
        if not active_samp:
            logging.warning(f'No active SAMP found. {func.__name__} will not be executed!')
            return
        return func(binder, active_samp=active_samp)

    return wrapper_func
