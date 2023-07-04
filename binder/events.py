from __future__ import annotations

from pyBinder.keys import KeyCombination


class BaseEvent:
    def handle_event(self, event: BaseEvent):
        pass

    def get_listener_type(self) -> str:
        pass


class ShortcutEvent(BaseEvent):
    def __init__(self, shortcut: KeyCombination):
        self.shortcut = shortcut

    def handle_event(self, event: ShortcutEvent):
        pass


class BaseChatEvent(BaseEvent):
    pass
