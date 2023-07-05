from dataclasses import dataclass


@dataclass
class RawEvent:
    type_: str
    args: list = None
    kwargs: dict = None
