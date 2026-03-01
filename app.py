from flask import Flask
from flask_login import LoginManager
from models import db, User
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

db.init_app(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

from routes import *

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
