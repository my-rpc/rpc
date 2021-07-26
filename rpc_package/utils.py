import json
import os
import re
from flask import jsonify


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


