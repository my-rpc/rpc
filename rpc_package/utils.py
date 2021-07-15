import json
import re
from flask import jsonify


class Translation:
    def __init__(self, file_path=""):
        try:
            self.translations = json.load(open(file_path, 'rb'))
        except IOError as exc:
            raise RuntimeError('Failed to open translation json fle') from exc

        for key, item in self.translations.items():
            if isinstance(item, dict):
                setattr(self, key, item)


class MessagePull:
    def __init__(self, file_path=""):
        try:
            self.messages = json.load(open(file_path, 'rb'))
        except IOError as exc:
            raise RuntimeError('Failed to open translation json fle') from exc

        for key, item in self.messages.items():
            if isinstance(item, dict):
                setattr(self, key, item)


class EmployeeValidator:

    @staticmethod
    def emp_id_validator(emp_id):
        return bool(re.match(r"RPC-\d{3}", emp_id))

    @staticmethod
    def number_validator(number):
        return bool(re.match(r"\d+", number))


def message_to_client_403(message):
    return jsonify({'success': False, 'message': message}), \
    403, {'ContentType': 'application/json'}


def message_to_client_200(message):
    return jsonify({'success': True, 'message': message}), \
                   200, {'ContentType': 'application/json'}
