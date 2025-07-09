import datetime
import calendar

def friday(date):
    days_since_monday = (date.weekday()) % 7
    return date - datetime.timedelta(days=days_since_monday) + datetime.timedelta(4)

def last_day_of_monday(date):
    month = date.month
    year = date.year
    _, last_day_num = calendar.monthrange(year, month)
    return datetime.date(year, month, last_day_num)

def date_equal(date1, date2):
    return date1 == date2.strftime('%Y%m%d')
