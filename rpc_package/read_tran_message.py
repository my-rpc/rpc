import json
import os


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

class UserAccess:
    def __init__(self, file_path=""):
        try:
            self.user_access = json.load(open(file_path, 'rb'))
        except IOError as exc:
            raise RuntimeError('Failed to open translation json fle') from exc

        for key, item in self.user_access.items():
            if isinstance(item, list):
                setattr(self, key, item)

class NotificationMessage:
    def __init__(self, file_path=""):
        # config_path = os.path.dirname(__file__)
        # file_path = os.path.join(config_path, 'config/notifications_message.json')
        try:
            self.notification_msg = json.load(open(file_path, 'rb'))
        except IOError as exc:
            raise RuntimeError('Failed to open translation json fle') from exc

        for key, item in self.notification_msg.items():
            if isinstance(item, dict):
                setattr(self, key, item)
