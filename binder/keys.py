from __future__ import annotations

import inspect
from typing import Iterable
from typing import Optional
from typing import Set
from typing import Type
from typing import Union

from pynput.keyboard import Key

from .utils import classproperty


class KeyCombination:
    named_keys = set((key.name for key in Key))

    def __init__(
            self, *,
            key: Optional[Union[str, Key]] = None,
            modifiers: Optional[Iterable[Type[BaseModifier]]] = None
    ):
        self.key: Optional[Key] = key
        self.modifiers: Set[Type[BaseModifier]] = set(modifiers) or set()

    def as_bindable_string(self):
        if not self.key:
            return ''

        result = '+'.join((
            f'<{modifier.key}>'
            for modifier in self.modifiers
        ))
        result += f'+{self.key}'
        return result

    def __add__(self, other: Union[str, int, Key, Type[BaseModifier], KeyCombination]) -> KeyCombination:
        if isinstance(other, str):
            self.key = other
            return self

        if isinstance(other, int) and 0 <= other <= 9:
            self.key = str(other)
            return self

        if isinstance(other, Key):
            self.key = other.name
            return self

        if inspect.isclass(other) and issubclass(other, BaseModifier):
            self.modifiers.add(other)
            return self

        if isinstance(other, KeyCombination):
            self.modifiers += other.modifiers
            self.key = other.key

            return self

        raise TypeError(f'Cannot add KeyCombination and {type(other).__name__}')

    def __str__(self):
        return self.as_bindable_string()


class ModifierMeta(type):
    def __add__(
            cls: Type[BaseModifier],
            other: Union[int, str, Key, KeyCombination, Type[BaseModifier]]
    ) -> KeyCombination:
        own_modifier = cls

        if isinstance(other, str):
            return KeyCombination(modifiers=[own_modifier], key=other)

        if isinstance(other, int) and 0 <= other <= 9:
            return KeyCombination(modifiers=[own_modifier], key=str(other))

        if isinstance(other, Key):
            return KeyCombination(modifiers=[own_modifier], key=other.name)

        if isinstance(other, KeyCombination):
            other.modifiers.add(own_modifier)
            return other

        if inspect.isclass(other) and issubclass(other, BaseModifier):
            return KeyCombination(modifiers=[own_modifier, other])

        raise TypeError(f"Cannot add Modifier and {type(other).__name__}")

    def __str__(cls: Type[BaseModifier]):
        return cls.key

    def __repr__(cls: Type[BaseModifier]):
        return f'<modifier {cls.key}>'


class BaseModifier(metaclass=ModifierMeta):
    _key = None

    @classproperty
    def key(cls) -> str:  # noqa
        return cls.__dict__['_key']

    def __str__(self):
        return self.key


class Ctrl(BaseModifier):
    _key = 'ctrl'


class LCtrl(BaseModifier):
    _key = 'lctrl'


class RCtrl(BaseModifier):
    _key = 'ctrl'


class LAlt(BaseModifier):
    _key = 'lalt'


class RAlt(BaseModifier):
    _key = 'ralt'


class LShift(BaseModifier):
    _key = 'lshift'


class RShift(BaseModifier):
    _key = 'rshift'
