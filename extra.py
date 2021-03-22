import datetime
import re


def check_time_string(string: str) -> bool:
    """Проверяет строку времени в соответствии с форматом "HH:MM-HH:MM" """
    # noinspection RegExpAnonymousGroup
    return bool(re.match(r'^([01]\d)|(2[0-3]):([0-5]\d)-([01]\d)|(2[0-3]):[0-5]\d$', string))


def split_time_string(string: check_time_string):
    (hours_a, minutes_a), (hours_b, minutes_b) = tuple(map(lambda x: tuple(map(int, x.split(':'))), string.split('-')))

    return datetime.time(hours_a, minutes_a), datetime.time(hours_b, minutes_b)


def collide_time(time: datetime.time, range_time: tuple) -> bool:
    if range_time[0] <= range_time[1]:
        return range_time[0] <= time <= range_time[1]
    return range_time[1] <= time <= range_time[0]
