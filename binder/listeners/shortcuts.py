import logging
from functools import partial
from typing import Set

from pynput import keyboard

from binder.keys import KeyCombination
from binder.listeners.base import BaseListener


class ShortcutListener(BaseListener):
    def __init__(self, handler):
        super().__init__(handler)
        self.registered_shortcuts: Set[KeyCombination] = set()

    def subscribe_event(self, event):
        super().subscribe_event(event)
        self.registered_shortcuts.add(event.shortcut)  # noqa

    def start(self):
        shortcuts_str = ', '.join([str(comb) for comb in self.registered_shortcuts])
        logging.info(f'{self.__class__.__name__} started listening shortcuts: {shortcuts_str}')
        with keyboard.GlobalHotKeys({
            comb.as_bindable_string(): partial(self._handle_shortcut, shortcut=comb)
            for comb in self.registered_shortcuts
        }) as h:
            h.join()

    def pause(self):
        logging.info(f'{self.__class__.__name__} paused listening')

    def stop(self):
        logging.info(f'{self.__class__.__name__} stopped listening')

    def resume(self):
        logging.info(f'{self.__class__.__name__} resumed listening')

    def _handle_shortcut(self, shortcut):
        # print(f'Shortcut pressed: {str(shortcut)}')
        self.handler('ShortcutEvent', shortcut=shortcut)
