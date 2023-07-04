from dataclasses import dataclass


@dataclass
class RPLine:
    line: str
    delay: int = 200
    press_f6: bool = True
    press_enter: bool = True
    press_time: bool = False
    press_screenshot: bool = False
