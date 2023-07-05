from .binder import Binder
from .samp import SAMP


class BaseDuty:
    def __init__(self, binder: Binder, samp: SAMP):
        self.binder = binder
        self.samp = samp
