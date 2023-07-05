import logging
from functools import partial
from multiprocessing import Queue, Process
from queue import Full
from threading import Thread
from typing import Set, Iterable, Optional

from pynput import keyboard

from binder.keys import KeyCombination
from binder.listeners.base import BaseListener
from binder.raw_event import RawEvent


class ShortcutListener(BaseListener):
    def __init__(self, event_queue: Queue):
        super().__init__(event_queue)
        self.registered_shortcuts: Set[KeyCombination] = set()
        self.listener_thread = None
        self.listener_process: Optional[Process] = None

    def subscribe_event(self, event):
        super().subscribe_event(event)
        self.registered_shortcuts.add(event.shortcut)  # noqa

    def start(self):
        shortcuts_str = ', '.join([str(comb) for comb in self.registered_shortcuts])
        logging.info(f'{self.__class__.__name__} started listening shortcuts: {shortcuts_str}')

        self.listener_process = Process(
            target=self._process_loop,
            args=(self.event_queue, self.registered_shortcuts)
        )
        self.listener_process.start()

    def stop(self):
        logging.info(f'{self.__class__.__name__} stopped listening')
        if self.listener_thread:
            self.listener_thread.stop()
        if self.listener_process:
            self.listener_process.kill()

    def join(self):
        if self.listener_thread:
            self.listener_thread.join()
        if self.listener_process:
            self.listener_process.join()

    def pause(self):
        pass

    def resume(self):
        pass

    @staticmethod
    def _process_loop(queue: Queue, shortcuts: Iterable[KeyCombination]):
        def handle_shortcut(shortcut: KeyCombination):
            try:
                queue.put_nowait(RawEvent(type_='ShortcutEvent', args=[shortcut]))
            except Full:
                return

        print(f'Started listening process')
        listener_thread: Thread = keyboard.GlobalHotKeys({
            shortcut.as_bindable_string(): partial(handle_shortcut, shortcut=shortcut)
            for shortcut in shortcuts
        })
        listener_thread.start()
        listener_thread.join()
