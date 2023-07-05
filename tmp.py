import logging
from time import sleep

from pynput import keyboard
from pynput.keyboard import Key

from binder.binder import Binder
from binder.combination_listener import CombinationListener
from binder.keyboard_listener import KeyboardListener
from binder.keys import LAlt
from binder.keys import LCtrl
from binder.keys import RShift


def handle_key_press(key):
    print(f'Key pressed: {key}')


def handle_key_release(key):
    print(f'Key released: {key}')


def handle_key_change(key: Key):
    print(f'Key changed: {key}')


def main():
    logging.basicConfig(level=logging.INFO)

    a = LCtrl + LAlt + RShift + 'g' + 'a'

    # print(a)

    binder = Binder()
    binder.autodiscover()

    # keyboard_listener = KeyboardListener()
    # listener = CombinationListener(keyboard_listener)
    # # listener.register_handler(listener.ON_KEY_CHANGE, handle_key_change)
    #
    # listener.start_listening(blocking=False)
    # # print(f'Listening started for 10 seconds')
    # sleep(10)
    # listener.stop_listening()
    # print(f'Listening ended!')
    # input(f'Press [Enter] to exit')


if __name__ == '__main__':
    main()
