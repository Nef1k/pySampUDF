from time import sleep

from dummy import execute_dummy
from samp.gta import GtaInstance
from samp.samp import SampAPI


def print_info(samp: SampAPI):
    print(f'Info we got so far:')
    print(f'  Server host: {samp.get_server_ip()}:{samp.get_server_port()}')
    print(f'  Server name: {samp.get_server_name()}')
    print(f'  Username: {samp.get_samp_username()}')
    print(f'  Health: {samp.get_lplayer_health()}')
    print(f'  Armor: {samp.get_lplayer_armor()}')
    print(f'  Money: {samp.get_lplayer_money()}')
    print(f'  Coordinates: {samp.get_lplayer_coordinates()}')


def main():
    instances = GtaInstance.discover_instances()
    if not instances:
        raise RuntimeError(f'GTA is not running')

    instance = instances[0]

    try:
        instance.open()

        samp = SampAPI(instance)
        print_info(samp)
        samp.send_message('.флекс')

    finally:
        instance.close()


if __name__ == '__main__':
    main()
