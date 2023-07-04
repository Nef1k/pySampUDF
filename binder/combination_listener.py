from collections import defaultdict
from typing import Callable
from typing import Dict
from typing import List

from pynput.keyboard import Key

from pyBinder.keyboard_listener import KeyboardListener
from pyBinder.keys import KeyCombination


class CombinationListener:
    MODIFIERS = {
        Key.ctrl, Key.ctrl_l, Key.ctrl_r,
        Key.alt, Key.alt_l, Key.alt_r, Key.alt_gr,
        Key.shift, Key.shift_l, Key.shift_r,
    }

    def __init__(self, keyboard_listener: KeyboardListener):
        if keyboard_listener.is_listening:
            raise ValueError("Keyboard listener is already listening!")

        self.keyboard_listener = keyboard_listener
        self.handlers: Dict[KeyCombination, List[Callable]] = defaultdict(list)

        self.modifiers_map: Dict[Key, bool] = {
            modifier: False
            for modifier in self.MODIFIERS
        }

        self.keyboard_listener.register_handler(
            KeyboardListener.ON_KEY_RELEASE,
            self._handle_key_release
        )

    @property
    def is_listening(self):
        return self.keyboard_listener.is_listening

    def start_listening(self, blocking: bool = True):
        self.keyboard_listener.start_listening(blocking)

    def stop_listening(self):
        self.keyboard_listener.stop_listening()

    def register_handler(self, combination: KeyCombination, handler: Callable):
        self.handlers[combination].append(handler)

    def _emit_combination_event(self, combination: KeyCombination):
        pass

    def _handle_key_release(self, key: Key):
        if key in self.MODIFIERS:
            self.modifiers_map[key] = False
            return

        combination = self._get_current_combination(key)
        print(combination)

    def _handle_key_press_once(self, key: Key):
        if key in self.MODIFIERS:
            self.modifiers_map[key] = True

    def _get_current_combination(self, key: Key) -> KeyCombination:
        active_modifiers = list(filter(
            lambda k: self.modifiers_map[k],
            self.modifiers_map.keys()
        ))
        return KeyCombination(modifiers=active_modifiers, key=key)
