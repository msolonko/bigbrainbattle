from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os
#db connection
application = Flask(__name__)
application.config['SECRET_KEY'] = '\xef$y\xd8\x0cJ\xd1\xc2\x84p\xe0\x17\x97\xe6\xeb\xf7J&\x1c\xf3\xffa\x82\xc0'
application.config['SQLALCHEMY_DATABASE_URI']='sqlite:///' + os.path.join('C:/Users/mykyt/Desktop/mithack', 'app.db')
db = SQLAlchemy(application)
bcrypt = Bcrypt(application)
login_manager = LoginManager(application)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from project import routes