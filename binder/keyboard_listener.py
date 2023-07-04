from collections import defaultdict
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from pynput.keyboard import Key
from pynput.keyboard import Listener


class KeyboardListener:
    ON_KEY_PRESS = 0
    ON_KEY_PRESS_SINGLE = 1
    ON_KEY_RELEASE = 2
    ON_KEY_CHANGE = 3

    def __init__(self):
        self.listener: Optional[Listener] = None
        self.events: Dict[int, List[Callable]] = defaultdict(list)
        self.key_pressed_map: Dict[Union[str, Key], bool] = defaultdict(lambda: False)

    @property
    def is_listening(self):
        return self.listener is not None

    def register_handler(self, event: int, handler: Callable):
        self.events[event].append(handler)

    def start_listening(self, blocking: bool = True):
        if blocking:
            self._start_listening_blocking()
        else:
            self._start_listening_non_blocking()

    def stop_listening(self):
        if not self.is_listening:
            return

        self.listener.stop()
        self.listener = None

    def _start_listening_blocking(self):
        with Listener(
                on_press=self._handle_listener_key_press,
                on_release=self._handle_listener_key_release
        ) as listener:
            self.listener = listener
            listener.join()

    def _start_listening_non_blocking(self):
        self.listener = Listener(
            on_press=self._handle_listener_key_press,
            on_release=self._handle_listener_key_release,
        )
        self.listener.start()

    def _handle_listener_key_press(self, key: Key):
        current_state = self.key_pressed_map[key]
        self._dispatch_event(self.ON_KEY_CHANGE, key)
        self._dispatch_event(self.ON_KEY_PRESS, key)
        if not current_state:
            self._dispatch_event(self.ON_KEY_PRESS_SINGLE, key)
        self.key_pressed_map[key] = True

    def _handle_listener_key_release(self, key: Key):
        self._dispatch_event(self.ON_KEY_CHANGE, key)
        self._dispatch_event(self.ON_KEY_RELEASE, key)
        self.key_pressed_map[key] = False

    def _dispatch_event(self, event: int, *args, **kwargs):
        handlers = self.events[event]
        for handler in handlers:
            handler(*args, **kwargs)
