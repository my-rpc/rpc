from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import pymysql
from flask_login import LoginManager
import os
import json
import datetime
from sqlalchemy import or_

pymysql.install_as_MySQLdb()

from rpc_package.read_tran_message import Translation, MessagePull, UserAccess, NotificationMessage

app = Flask(__name__)
config_path = os.path.dirname(__file__)
CONFIG = json.load(open(os.path.join(config_path, 'config/config.json'), 'rb'))
app.config["SECRET_KEY"] = CONFIG['secret_key']
app.config["SQLALCHEMY_DATABASE_URI"] = CONFIG['db_url']
db = SQLAlchemy(app)
# TODO check why we need this

# create translation object
translation_obj = Translation(os.path.join(config_path, 'config/english_dari_translation.json'))
message_obj = MessagePull(os.path.join(config_path, 'config/messages.json'))
user_access = UserAccess(os.path.join(config_path, 'config/user_access.json'))
notification_msg = NotificationMessage(os.path.join(config_path, 'config/notifications_message.json'))
pass_crypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = translation_obj.login_message['en']

from rpc_package.utils import to_gregorian, to_jalali, check_access, get_month_name

app.jinja_env.globals.update(to_jalali=to_jalali, to_gregorian=to_gregorian, or_=or_, \
    sum=sum, translation=translation_obj, message_obj=message_obj, check_access=check_access, \
    date=datetime.date, get_month_name=get_month_name)

from rpc_package import app_routes