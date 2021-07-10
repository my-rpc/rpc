from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import pymysql
from flask_login import LoginManager
import os
import json

pymysql.install_as_MySQLdb()

from rpc_package.utils import Translation, MessagePull

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
# login_manager = LoginManager(app)
# login_manager.login_view = 'login'
# login_manager.login_message_category = 'info'
# login_manager.login_message = 'برای وارد شدن به صفحه مورد نظر لطفا اطلاعات خود را وارد کنید'

from rpc_package import app_routes