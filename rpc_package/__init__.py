from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from flask_login import LoginManager
import os
import json

from rpc_package.utils import Translation

app = Flask(__name__)
config_path = os.path.dirname(__file__)
CONFIG = json.load(open(os.path.join(config_path, 'config/config.json'), 'rb'))
app.config["SECRET_KEY"] = CONFIG['secret_key']

# create translation object
translation_obj = Translation(os.path.join(config_path, 'config/english_dari_translation.json'))

# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = '0650c9411b66221d947b0ea065d18008'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# db = SQLAlchemy(app)
# db.session.execute('pragma foreign_keys=on')
# pass_crypt = Bcrypt(app)
# login_manager = LoginManager(app)
# login_manager.login_view = 'login'
# login_manager.login_message_category = 'info'
# login_manager.login_message = 'برای وارد شدن به صفحه مورد نظر لطفا اطلاعات خود را وارد کنید'

from rpc_package import app_routes