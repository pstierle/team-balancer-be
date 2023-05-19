from flask import Flask
from flask_cors import CORS
from os import environ
from dotenv import load_dotenv
from database import db
from routes.player import player_router
from routes.auth import auth_router
from routes.base_game import base_game_router
from flask_admin import Admin
from database import User, Player, Game
from flask_basicauth import BasicAuth
import flask_admin.contrib.sqla

load_dotenv()

app = Flask(__name__)
app.secret_key = "auto-team-balancer"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config['BASIC_AUTH_USERNAME'] = environ['basic_auth_username']
app.config['BASIC_AUTH_PASSWORD'] = environ['basic_auth_password']

app.register_blueprint(player_router)
app.register_blueprint(auth_router)
app.register_blueprint(base_game_router)
basic_auth = BasicAuth(app)

db.init_app(app)


class ModelView(flask_admin.contrib.sqla.ModelView):
    def is_accessible(self):
        if not basic_auth.authenticate():
            return False
        else:
            return True


admin = Admin(app, name="Team Balancer", endpoint="/admin")
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Player, db.session))
admin.add_view(ModelView(Game, db.session))

cors = CORS(app)


with app.app_context():
    db.create_all()
