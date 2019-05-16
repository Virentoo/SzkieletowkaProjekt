import datetime


def convert_datetime(date, time):
    if date:
        if time:
            return datetime.datetime.combine(date, time)
        else:
            return date
    else:
        if time:
            return time
        else:
            return None

