from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import pymysql
from flask_login import LoginManager
import os
import json
import datetime
from rpc_package.utils import to_gregorian, to_jalali

pymysql.install_as_MySQLdb()

from rpc_package.read_tran_message import Translation, MessagePull

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
pass_crypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = translation_obj.login_message['en']

app.jinja_env.globals.update(to_jalali=to_jalali, to_gregorian=to_gregorian, timedelta=datetime.timedelta(0), sum=sum)

from rpc_package import app_routes