from dateutil.relativedelta import MO, TU, WE, TH, FR, SA, SU


def int_to_dateutil_weekday(day_int):
    int_to_weekday = {
        0: MO,
        1: TU,
        2: WE,
        3: TH,
        4: FR,
        5: SA,
        6: SU
    }
    return int_to_weekday[day_int]
