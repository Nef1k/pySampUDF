from datetime import datetime
from datetime import timedelta

from pyBinder.binder import Binder
from pyBinder.samp import SAMP

from pyBinder.base_duty import BaseDuty


@Binder.duty('land_smp')
class SMPDuty(BaseDuty):
    def __init__(self, binder: Binder, samp: SAMP):
        super().__init__(binder, samp)
        self.healed_count = 0

    @Binder.duty.start()
    def duty_start(self):
        self.binder.run_rp(
            RPLine('!Начинаю дежурство', press_time=True, press_screenshot=True)
        )

    @Binder.duty.on(EveryGivenInterval and PlayerInVechicle)
    def duty_in_progress(self):
        self.binder.run_rp(
            RPLine(f'!Продолжаю дежурство. Вылечено: {self.healed_count}', press_time=True, press_screenshot=True)
        )

    @Binder.duty.on(
        EveryGivenInterval - timedelta(seconds=30),
        EveryGivenInterval - timedelta(seconds=10),
        EveryGivenInterval - timedelta(seconds=5),
        EveryGivenInterval - timedelta(seconds=2),
    )
    def duty_in_progress_alert(self):
        seconds_till_report: timedelta = self.get_next_report_time() - datetime.now()
        self.samp.add_to_chat(f'Внимание: до следующего доклада {seconds_till_report} секунд!')

    @Binder.duty.complete()
    def duty_over(self):
        self.binder.run_rp(
            RPLine(f'Закончил дежурство. Вылечено: {self.healed_count}')
        )

    @Binder.duty.on(PatientHealed or KeyCombination(LAlt + '+'))
    def increase_healed_count(self):
        self.samp.add_to_chat(f'+1. Кол-во вылеченных: {self.healed_count}')
        self.healed_count += 1

    @Binder.duty.on(KeyCombination(LAlt + '-'))
    def decrease_healed_count(self):
        self.samp.add_to_chat(f'-1. Кол-во вылеченных: {self.healed_count}')
        if self.healed_count > 0:
            self.healed_count -= 1


@Binder.bind(LCtrl + LShift + '1')
def run_half_hour_duty(binder: Binder):
    binder.run_duty(
        'land_smp',
        interval=timedelta(minutes=10),
        duty_length=timedelta(hours=1)
    )
