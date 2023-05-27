from flask import Blueprint, request, abort
from util import auth_guard
from database import db, Player
from util import (
    base_games_with_images,
    generate_teams_by_elo
)
import random

base_game_router = Blueprint("base_game_router", __name__)


@base_game_router.route("/base-game", methods=["GET"])
@auth_guard()
def get_players():
    return base_games_with_images(request.host_url)


@base_game_router.route("/base-game/random-map", methods=["POST"])
@auth_guard()
def random_map():
    body = request.get_json()
    maps = body["maps"]
    if len(maps) <= 0:
        abort(400)
        
    return random.choice(maps)


@base_game_router.route("/base-game/generate-teams", methods=["POST"])
@auth_guard()
def generate_teams():
    body = request.get_json()
    base_game_id = body["baseGameId"]
    player_ids = body["playerIds"]
    players = db.session.query(Player).filter(Player.id.in_(player_ids)).all()
    return generate_teams_by_elo(players, base_game_id)
