from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True)
    players = db.relationship(
        'Player', backref='user')


class Player(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    games = db.relationship('Game', backref='player')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Game(db.Model):
    id = db.Column(db.String, primary_key=True)
    elo = db.Column(db.Integer)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    base_game_id = db.Column(db.Integer)
