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