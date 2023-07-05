from typing import Type

from binder.binder import Binder
from binder.binder_utils import require_active_samp
from binder.rp_line import RPLine
from samp.samp import SampAPI


# @Binder.bind(Alt + '1')
# @require_active_samp
# def pills(binder: Type[Binder], active_samp: SampAPI):
#     binder.do_rp([
#         RPLine('.фд Сейчас я окажу Вам медицинскую помощь*осматривая пациента'),
#         RPLine('.я записывает данные о симптомах в медкарту пациента и достает медикамент из сумки'),
#         RPLine('.фд Вам поможет "Полиспектрин"*передавая препарат и бутылку воды пациенту'),
#         RPLine('.фд Стоимость медикаментов составила 60$*выписывая счёт за лечение'),
#         RPLine('.фд Всего вам доброго, не болейте*передавая счёт за лечение пациенту', press_time=True),
#     ], samp=active_samp)


@Binder.bind('-')
@require_active_samp
def adrenaline(binder: Type[Binder], active_samp: SampAPI):
    binder.do_rp([
        RPLine('.я ввёл инъекцию адреналина пациенту.', press_time=True)
    ], samp=active_samp)


@Binder.bind('=')
@require_active_samp
def adrenaline(binder: Type[Binder], active_samp: SampAPI):
    binder.do_rp([
        RPLine('.я ввёл инъекцию адреналина пациенту', press_time=True)
    ], samp=active_samp)
