import logging

from binder.binder import Binder
from samp.samp import SampAPI


def print_info(samp: SampAPI):
    print(f'Attached to SAMP instance:')
    print(f'  Server host: {samp.get_server_ip()}:{samp.get_server_port()}')
    print(f'  Server name: {samp.get_server_name()}')
    print(f'  Username: {samp.get_samp_username()}')
    print(f'  Health: {samp.get_lplayer_health()}')
    print(f'  Armor: {samp.get_lplayer_armor()}')
    print(f'  Money: {samp.get_lplayer_money()}')
    print(f'  Coordinates: {samp.get_lplayer_coordinates()}')


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s][%(levelname)s] %(message)s',
    )

    Binder.autodiscover()

    try:
        Binder.start()
    except KeyboardInterrupt:
        logging.info(f'Terminating...')
        Binder.stop()
    finally:
        Binder.stop()


if __name__ == '__main__':
    main()
