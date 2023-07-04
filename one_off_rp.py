from pyBinder.binder import Binder
from pyBinder.rp_line import RPLine


@Binder.bind(LAlt + '1')
def test_cmd_1(binder: Binder):
    binder.run_rp([
        RPLine('Привет мир!'),
        RPLine('Я новый биндер на движке pyBinder!'),
        RPLine('*Я могу писать как в ooc-чат'),
        RPLine('Так и в ic-чат', delay=1500),
        RPLine('А ещё я могу проставить .время и сделать скриншот!', press_time=True, press_screenshot=True)
    ])
