import importlib
import logging
import os
import pkgutil
import sys
from collections import defaultdict
from functools import partial
from typing import Callable, Type, List
from typing import Dict
from typing import Optional
from typing import Union

from pynput.keyboard import GlobalHotKeys

from .events import ShortcutEvent, BaseEvent
from .keys import KeyCombination
from .listeners.base import BaseListener


class Binder:
    _bind_map: Dict[KeyCombination, Callable] = {}
    listeners: Dict[
        Type[BaseListener],
        BaseListener] = {}
    handlers: Dict[BaseEvent, List[Callable]] = defaultdict(list)

    @classmethod
    def bind(
            cls,
            key_combination: Union[KeyCombination, str]
    ):
        if isinstance(key_combination, str):
            event = ShortcutEvent(KeyCombination(key=key_combination))
        else:
            event = ShortcutEvent(key_combination)
        return cls.on(event)

    @classmethod
    def on(
            cls,
            event,
    ):
        def decorator(func):
            cls.raw_bind(event, func)
            return func

        return decorator

    @classmethod
    def raw_bind(cls, event: BaseEvent, handler: Callable):
        logging.info(f'Registered event "{str(event)}" with handler {handler.__name__}')
        cls.handlers[event].append(handler)
        cls._ensure_event_listener(event)

    @classmethod
    def start(cls):
        if not cls.listeners:
            logging.critical(f'No listeners registered. Try subscribing on some events')
            return

        for listener in cls.listeners.values():
            listener.start()

    @classmethod
    def stop(cls):
        # TODO: implement Ctrl+C stop

    @classmethod
    def pause(cls):
        pass

    @classmethod
    def resume(cls):
        pass

    @classmethod
    def autodiscover(cls):
        main_module_path = sys.modules['__main__'].__file__

        modules = (
            module_info
            for module_info in pkgutil.iter_modules(['.'])
            if not module_info.ispkg
        )
        for module in modules:
            module_full_path = os.path.abspath(os.path.join(
                module.module_finder.path,  # noqa
                f'{module.name}.py'
            ))
            if module_full_path == main_module_path:
                continue

            try:
                importlib.import_module(module.name)
            except Exception as e:
                logging.error(f'Could not import profile {module.name}: {str(e)}')
                continue
            logging.info(f'Loaded profile {module.name}')

    @classmethod
    def _ensure_event_listener(cls, event: BaseEvent):
        listener_class = event.listener_class
        if not listener_class:
            logging.warning(f'Event of type {event.__class__.__name__} has not listener attached')
            return

        listener: BaseListener
        if listener_class not in cls.listeners:
            cls.listeners[listener_class] = listener = listener_class(cls._handle_event)  # noqa
            logging.info(f'Registered new listener: {listener_class.__name__}')
        else:
            listener = cls.listeners[listener_class]

        listener.subscribe_event(event)

    @classmethod
    def _handle_event(cls, type_, *args, **kwargs):
        event_class = list(filter(lambda e: e.__class__.__name__ == type_, cls.handlers.keys()))
        if not event_class:
            return
        event_class = event_class[0].__class__
        event = event_class(*args, **kwargs)
        handlers = cls.handlers[event]
        for handler in handlers:
            handler(cls)
