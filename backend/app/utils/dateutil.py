# -*- coding: utf-8 -*-
"""
日期工具函数
"""

import datetime
import calendar


def adjust_date(input_date):
    """
    根据输入的日期，如果日期大于当前天，则返回当前天；
    如果小于或等于当前天，则直接返回该日期。
    """
    current_date = datetime.date.today()
    if input_date > current_date:
        return current_date
    return input_date


def friday(date):
    """返回给定日期所在周的周五"""
    days_since_monday = (date.weekday()) % 7
    return date - datetime.timedelta(days=days_since_monday) + datetime.timedelta(4)


def last_day_of_monday(date):
    """返回给定日期所在月的最后一天"""
    month = date.month
    year = date.year
    _, last_day_num = calendar.monthrange(year, month)
    return datetime.date(year, month, last_day_num)


def date_equal(date1, date2):
    """比较 date 对象和 YYYYMMDD 字符串是否相等"""
    return date1 == date2.strftime("%Y%m%d")


def saturday(date):
    """返回给定日期所在周的周六"""
    days_to_saturday = 5 - date.weekday()
    return date + datetime.timedelta(days=days_to_saturday)


def saturdayline(datestr):
    """给定 YYYYMMDD 字符串，返回所在周的周六 YYYYMMDD 字符串"""
    date = datetime.datetime.strptime(datestr, "%Y%m%d").date()
    saturday_date = saturday(date)
    return saturday_date.strftime("%Y%m%d")


def get_month_range(date):
    """返回给定日期所在月的第一天和最后一天"""
    first_day = datetime.date(date.year, date.month, 1)
    _, last_day_num = calendar.monthrange(date.year, date.month)
    last_day = datetime.date(date.year, date.month, last_day_num)
    return first_day, last_day


def get_month_range_str(datestr):
    """YYYYMMDD 字符串版本 get_month_range"""
    date = datetime.datetime.strptime(datestr, "%Y%m%d").date()
    first_day, last_day = get_month_range(date)
    return first_day.strftime("%Y%m%d"), last_day.strftime("%Y%m%d")


def get_current_saturday_and_month_start(current_date):
    """
    返回当前日期的(上周六, 本月1号) YYYYMMDD 字符串
    注意：saturday 返回的是上周六（当前周六 - 7天）
    """
    saturday_date = saturday(current_date)
    month_start_date = datetime.date(current_date.year, current_date.month, 1)
    return (
        (saturday_date + datetime.timedelta(days=-7)).strftime("%Y%m%d"),
        month_start_date.strftime("%Y%m%d"),
    )


def calculate_date(date_input, n):
    """
    计算给定日期前后 n 天的日期

    Args:
        date_input: str (YYYYMMDD) 或 datetime 对象
        n: 天数偏移量（正数往后，负数往前）

    Returns:
        datetime: 计算后的日期对象
    """
    if isinstance(date_input, str):
        date = datetime.datetime.strptime(date_input, "%Y%m%d")
    else:
        date = date_input
    return date + datetime.timedelta(days=n)
