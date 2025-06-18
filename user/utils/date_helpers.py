import calendar
from datetime import date

def get_last_day_of_month(year, month):
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, last_day)
