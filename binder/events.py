from __future__ import annotations

import inspect

from .keys import KeyCombination
from .listeners.shortcuts import ShortcutListener
from .raw_event import RawEvent
from .utils import classproperty


class BaseEvent:
    _event_type = None
    _listener_class = None

    @classmethod
    def from_raw(cls, event: RawEvent):
        if event.type_ != cls.__name__:
            raise TypeError(f'Cannot construct event object from raw event of type {event.type_}')

        args = event.args or []
        kwargs = event.kwargs or {}
        return cls(*args, **kwargs)  # noqa

    @classproperty
    def event_type(cls) -> str:  # noqa
        return cls.__dict__['_event_type']

    @classproperty
    def listener_class(cls) -> str:  # noqa
        return cls.__dict__['_listener_class']

    def __hash__(self) -> int:
        raise NotImplementedError()

    def __eq__(self, other: BaseEvent) -> bool:
        raise NotImplementedError()

    def __str__(self) -> str:
        if '__str__' in self.__dict__:
            return str(self)
        else:
            return self.__class__.__name__


class ShortcutEvent(BaseEvent):
    _event_type = 'shortcut_event'
    _listener_class = ShortcutListener

    def __init__(self, shortcut: KeyCombination):
        self.__shortcut: KeyCombination = shortcut

    @property
    def shortcut(self) -> KeyCombination:
        return self.__shortcut

    def __hash__(self) -> int:
        return hash(f'{self.event_type}{str(self._event_type)}')

    def __eq__(self, other: ShortcutEvent) -> bool:
        if not issubclass(type(other), ShortcutEvent):
            return False

        return other.shortcut.as_bindable_string() == self.shortcut.as_bindable_string()

    def __str__(self) -> str:
        return f'ShortcutEvent({str(self.shortcut)})'


class BaseChatEvent(BaseEvent):
    _event_type = 'base_chat_event'

    def __hash__(self) -> int:
        return hash(self._event_type)

    def __eq__(self, other: BaseEvent) -> bool:
        return True
