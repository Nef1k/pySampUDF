import importlib
import logging
import os
import pkgutil
import sys
from collections import defaultdict
from multiprocessing import Queue
from queue import Empty
from typing import Callable, Type, List, Collection
from typing import Dict
from typing import Optional
from typing import Union

from pynput import keyboard, mouse
from pynput.keyboard import Key

from samp.gta import GtaInstance
from samp.samp import SampAPI
from .events import ShortcutEvent, BaseEvent
from .keys import KeyCombination
from .listeners.base import BaseListener
from .rp_line import RPLine
from .utils import classproperty, sleep_ms


class Binder:
    __EVENT_RETRIEVE_TIMEOUT = 0.005

    DEFAULT_RP_DELAY = 2300

    listeners: Dict[Type[BaseListener], BaseListener] = {}
    handlers: Dict[BaseEvent, List[Callable]] = defaultdict(list)
    samp_instances: Dict[str, SampAPI] = {}

    kb_controller = keyboard.Controller()
    mouse_controller = mouse.Controller()

    _event_queue: Queue = Queue()

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

        cls._update_samp_instances()

        cls._event_loop()

    @classmethod
    def stop(cls):
        for listener in cls.listeners.values():
            listener.stop()

        cls._dispose_samp_instances()

    @classmethod
    def pause(cls):
        for listener in cls.listeners.values():
            listener.pause()

    @classmethod
    def resume(cls):
        for listener in cls.listeners.values():
            listener.resume()

    @classmethod
    def join(cls):
        for listener in cls.listeners.values():
            listener.join()

    @classproperty
    def active_samp(cls) -> Optional[SampAPI]:  # noqa
        active_samp = list(filter(lambda i: i.gta.is_active, cls.samp_instances.values()))
        if not active_samp:
            return None

        return active_samp[0]
    active_samp: SampAPI

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
    def touch_key(cls, key: Union[Key, str]):
        cls.kb_controller.press(key)
        sleep_ms(100)
        cls.kb_controller.release(key)

    @classmethod
    def do_rp(cls, lines: Collection[RPLine], *, samp: SampAPI = None):
        active_samp = samp
        if active_samp:
            active_samp = cls.active_samp
            if not active_samp:
                logging.info(f'No active SAMP found.')
                return

        for idx, line in enumerate(lines):
            active_samp.send_message(line.line)
            if line.press_time:
                sleep_ms(500)
                active_samp.send_message('.время')
            if line.press_screenshot:
                sleep_ms(200)
                Binder.touch_key(Key.f8)

            is_last = idx == len(lines) - 1
            if is_last:
                continue

            delay = line.delay if line.delay is not None else cls.DEFAULT_RP_DELAY
            sleep_ms(delay)

    @classmethod
    def _event_loop(cls):
        while True:
            try:
                raw_event = cls._event_queue.get(block=True, timeout=cls.__EVENT_RETRIEVE_TIMEOUT)
            except Empty:
                continue

            event_class = list(filter(lambda e: e.__class__.__name__ == raw_event.type_, cls.handlers.keys()))
            if not event_class:
                return
            event_class = event_class[0].__class__
            event = event_class.from_raw(raw_event)

            cls._dispatch_event(event)

    @classmethod
    def _ensure_event_listener(cls, event: BaseEvent):
        listener_class = event.listener_class
        if not listener_class:
            logging.warning(f'Event of type {event.__class__.__name__} has not listener attached')
            return

        listener: BaseListener
        if listener_class not in cls.listeners:
            cls.listeners[listener_class] = listener = listener_class(cls._event_queue)  # noqa
            logging.info(f'Registered new listener: {listener_class.__name__}')
        else:
            listener = cls.listeners[listener_class]

        listener.subscribe_event(event)

    @classmethod
    def _dispatch_event(cls, event):
        handlers = cls.handlers[event]
        for handler in handlers:
            try:
                handler(cls)
            except Exception as e:  # noqa
                logging.error(f'Error while executing handler {handler.__name__}: {str(e)}')

    @classmethod
    def _update_samp_instances(cls):
        gta_instances = GtaInstance.discover_instances()
        samp_instances = [SampAPI(gta_instance) for gta_instance in gta_instances]
        for samp_instance in samp_instances:
            samp_instance.gta.open()
            username = samp_instance.get_samp_username()
            logging.info(f'Discovered SAMP instance with username {username}')
            cls.samp_instances[username] = samp_instance

    @classmethod
    def _dispose_samp_instances(cls):
        for samp in cls.samp_instances.values():
            samp.gta.close()
        cls.samp_instances = {}
