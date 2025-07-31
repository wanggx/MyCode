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


def saturday(date):
    """
    给定一个日期，返回该日期所在周的周六日期。

    参数:
        date (datetime.date): 输入的日期对象。

    返回:
        datetime.date: 该日期所在周的周六日期。
    """
    # 计算距离周六的天数差
    # 周六是weekday()返回值为5 (周一为0)
    days_to_saturday = 5 - date.weekday()
    return date + datetime.timedelta(days=days_to_saturday)


def saturdayline(datestr):
    """
    给定一个日期字符串，返回该日期所在周的周六日期字符串。

    参数:
        datestr (str): 输入的日期字符串，格式为 'YYYYMMDD'。

    返回:
        str: 该日期所在周的周六日期，格式为 'YYYYMMDD'。
    """
    # 将输入的日期字符串转换为日期对象
    date = datetime.datetime.strptime(datestr, '%Y%m%d').date()

    # 调用saturday函数获取周六日期
    saturday_date = saturday(date)

    # 返回格式化后的日期字符串
    return saturday_date.strftime('%Y%m%d')


def get_month_range(date):
    """
    给定一个日期，返回该日期所在月的第一天和最后一天。

    参数:
        date (datetime.date): 输入的日期对象。

    返回:
        tuple: 包含两个datetime.date对象的元组，分别表示该月的第一天和最后一天。
    """
    # 获取该月的第一天（总是1号）
    first_day = datetime.date(date.year, date.month, 1)

    # 获取该月的最后一天
    _, last_day_num = calendar.monthrange(date.year, date.month)
    last_day = datetime.date(date.year, date.month, last_day_num)

    return first_day, last_day


def get_month_range_str(datestr):
    """
    给定一个日期字符串，返回该日期所在月的第一天和最后一天的字符串格式。

    参数:
        datestr (str): 输入的日期字符串，格式为 'YYYYMMDD'。

    返回:
        tuple: 包含两个字符串的元组，分别表示该月的第一天和最后一天，格式为 'YYYYMMDD'。
    """
    # 将输入的日期字符串转换为日期对象
    date = datetime.datetime.strptime(datestr, '%Y%m%d').date()

    # 获取该月的第一天和最后一天
    first_day, last_day = get_month_range(date)

    # 返回格式化后的日期字符串
    return first_day.strftime('%Y%m%d'), last_day.strftime('%Y%m%d')


def get_current_saturday_and_month_start(current_date):
    """
    获取当前日期所在的周六时间和本月的1号时间

    Returns:
        tuple: 包含两个元素的元组
            - saturday_date (str): 当前日期所在周的周六，格式为 'YYYYMMDD'
            - month_start_date (str): 当前日期所在月的1号，格式为 'YYYYMMDD'
    """

    # 获取当前日期所在周的周六
    saturday_date = saturday(current_date)

    # 获取当前日期所在月的1号
    month_start_date = datetime.date(current_date.year, current_date.month, 1)

    # 格式化为字符串并返回
    return (
        (saturday_date + datetime.timedelta(days=-7)).strftime('%Y%m%d'),
        month_start_date.strftime('%Y%m%d')
    )

def calculate_date(date_input, n):
    """
    计算给定日期前后n天的日期

    Args:
        date_input (str or datetime): 输入日期，可以是字符串格式'YYYYMMDD'或datetime对象
        n (int): 天数偏移量，正数表示往后推n天，负数表示往前推n天

    Returns:
        datetime: 计算后的日期对象

    Examples:
        >>> calculate_date('20231001', 5)
        datetime.datetime(2023, 10, 6, 0, 0)

        >>> calculate_date(datetime(2023, 10, 1), -3)
        datetime.datetime(2023, 9, 28, 0, 0)
    """
    # 如果输入是字符串，则转换为datetime对象
    if isinstance(date_input, str):
        date = datetime.datetime.strptime(date_input, '%Y%m%d')
    else:
        date = date_input

    # 计算前后n天的日期
    result_date = date + datetime.timedelta(days=n)

    return result_date