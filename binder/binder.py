import importlib
import inspect
import logging
import os
import pkgutil
import sys
from functools import partial
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Union

from pynput.keyboard import GlobalHotKeys

from pyBinder.keys import KeyCombination


class Binder:
    _bind_map: Dict[KeyCombination, Callable] = {}

    def __init__(self):
        self.is_active = True
        self.listener: Optional[GlobalHotKeys] = None

    @classmethod
    def bind(
            cls,
            key_combination: Union[KeyCombination, str]
    ):
        pass

    @classmethod
    def on(
            cls,
            event,
    ):
        pass

    @property
    def is_listening(self) -> bool:
        return self.listener is not None and self.listener.running

    def start(self):
        self.listener = GlobalHotKeys({
            combination.as_bindable_string(): partial(self._handle_shortcut,
                                                      combination)
            for combination, handlers in self._bind_map.items()
        })

        self.resume()

    def stop(self):
        self.pause()

    def pause(self):
        self.is_active = False

    def resume(self):
        self.is_active = True

    def autodiscover(self):
        main_module_path = sys.modules['__main__'].__file__

        modules = (
            module_info
            for module_info in pkgutil.iter_modules(['.'])
            if not module_info.ispkg
        )
        for module in modules:
            module_full_path = os.path.abspath(os.path.join(
                module.module_finder.path,
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

    def _handle_shortcut(self, combination: KeyCombination):
        print(f'Combination: {combination}')
