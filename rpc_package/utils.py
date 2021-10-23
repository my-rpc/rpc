import json
import os
import re
from flask import jsonify
import os
import jdatetime, datetime
from rpc_package import user_access
from flask_login import current_user
import pandas as pd
import numpy as np
from flask import url_for, redirect, request

class EmployeeValidator:

    @staticmethod
    def emp_id_validator(emp_id):
        return bool(re.match(r"RPC-\d{3}", emp_id))

    @staticmethod
    def number_validator(number):
        return bool(re.match(r"\d+", number))

    @staticmethod
    def email_validator(email):
        return bool(re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email))

    @staticmethod
    def phone_validator(phone):
        return bool(re.match(r'(\d{3}[-\.\s]\d{3}[-\.\s]\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]\d{4}|\d{3}[-\.\s]\d{4})', phone))


def message_to_client_403(message):
    return jsonify({'success': False, 'message': message}), \
    403, {'ContentType': 'application/json'}


def message_to_client_200(message):
    return jsonify({'success': True, 'message': message}), \
                   200, {'ContentType': 'application/json'}


def check_language(input_sentence):
    for ch in input_sentence:
        if ('\u0600' <= ch <= '\u06FF' or
                '\u0750' <= ch <= '\u077F' or
                '\u08A0' <= ch <= '\u08FF' or
                '\uFB50' <= ch <= '\uFDFF' or
                '\uFE70' <= ch <= '\uFEFF' or
                '\U00010E60' <= ch <= '\U00010E7F' or
                ch == ' ' or
                '\U0001EE00' <= ch <= '\U0001EEFF'):
            continue
        else:
            return False
    return True

def datetime_validation(self, value):
    try:
        date_format = '%Y-%m-%d %H:%M:%S'
        if value == None:
            return True
        str_value = value
        if (isinstance(value, datetime.datetime) or isinstance(value, datetime.date)):
            str_value = value.strftime(date_format)
        jdatetime.datetime.strptime(str_value, date_format)
        return True
    except ValueError:
        return False

def date_validation(self, value):
    try:
        date_format = '%Y-%m-%d'
        if value == None:
            return True
        str_value = value
        if (isinstance(value, datetime.datetime) or isinstance(value, datetime.date)):
            str_value = value.strftime(date_format)
        jdatetime.datetime.strptime(str_value, date_format)
        return True
    except ValueError:
        return False

def to_gregorian(value, date_format='%Y-%m-%d'):
    if value == None:
        return ''
    str_value = value
    if (isinstance(value, jdatetime.datetime) or isinstance(value, jdatetime.date)):
        str_value = value.strftime(date_format)
    value = jdatetime.datetime.strptime(str_value, date_format)
    date_value = value.togregorian()
    return date_value.strftime(date_format)

def to_jalali(value, date_format='%Y-%m-%d', type='str'):
    if value == None:
        return ''
    str_value = value
    if (isinstance(value, datetime.datetime) or isinstance(value, datetime.date)):
        str_value = value.strftime(date_format)
    value = datetime.datetime.strptime(str_value, date_format)
    year = value.year
    month = value.month
    day = value.day
    hour = value.hour
    minute = value.minute
    second = value.second
    jvalue = jdatetime.datetime.fromgregorian(day=day, month=month, year=year, hour=hour, minute=minute, second=second)
    if type == 'date':
        return jvalue
    return jvalue.strftime(date_format)

def check_access(route_name=''):
    if current_user and current_user.user_role :
        roles = getattr(user_access, current_user.user_role.name_english)
        employees = getattr(user_access, "Employee")
        if isinstance(roles, list) :
            return (route_name in roles or route_name in employees)
    return False

def get_months():
    return [
        (1, "حمل"),
        (2, "ثور"),
        (3, "جوزا"),
        (4, "سرطان"),
        (5, "اسد"),
        (6, "سنبله"),
        (7, "میزان"),
        (8, "عقرب"),
        (9, "قوس"),
        (10, "جدی"),
        (11, "دلو"),
        (12, "حوت")
    ]

def get_month_name(month):
    months = get_months()
    return months[month-1][1]

def convert_to_shamsi(dates):
    result_dates = []
    for date in dates:
        sdate = date.split('/')
        date = jdatetime.datetime.fromgregorian(day=int(sdate[1]), month=int(sdate[0]), year=int(sdate[2]))
        result_dates.append(date.strftime('%Y-%m-%d'))
    return result_dates

def get_last_day_of_month(month=1):
    day = 31
    if month <= 6:
        day = 31
    elif month < 12:
        day = 30
    elif month == 12:
        day = 30 if jdatetime.date.today().isleap() else 29
    return day