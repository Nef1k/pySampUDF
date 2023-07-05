from typing import Type

from binder.binder import Binder
from binder.keys import LAlt, RCtrl
from binder.rp_line import RPLine


@Binder.bind(RCtrl + '1')
def test_cmd_1(binder: Type[Binder]):
    print(f'test_cmd_1')
    # binder.run_rp([
    #     RPLine('Привет мир!'),
    #     RPLine('Я новый биндер на движке pyBinder!'),
    #     RPLine('*Я могу писать как в ooc-чат'),
    #     RPLine('Так и в ic-чат', delay=1500),
    #     RPLine('А ещё я могу проставить .время и сделать скриншот!', press_time=True, press_screenshot=True)
    # ])
