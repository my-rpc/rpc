import json


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


def check_language(input_sentence):
    for ch in input_sentence:
        if ('\u0600' <= ch <= '\u06FF' or
                '\u0750' <= ch <= '\u077F' or
                '\u08A0' <= ch <= '\u08FF' or
                '\uFB50' <= ch <= '\uFDFF' or
                '\uFE70' <= ch <= '\uFEFF' or
                '\U00010E60' <= ch <= '\U00010E7F' or
                '\U0001EE00' <= ch <= '\U0001EEFF'):
            continue
        else:
            return False
    return True
