from flask import Blueprint, request
from util import auth_guard
from database import db, Player
from util import players_to_games_by_base_game, sum_split, players_from_games, base_games_with_images
import random

base_game_router = Blueprint('base_game_router', __name__)


@base_game_router.route('/base-game', methods=["GET"])
@auth_guard()
def get_players():
    return base_games_with_images(request.host_url)


@base_game_router.route('/base-game/random-map', methods=["POST"])
@auth_guard()
def random_map():
    body = request.get_json()
    maps = body['maps']
    return random.choice(maps)


@base_game_router.route('/base-game/generate-teams', methods=["POST"])
@auth_guard()
def generate_teams():
    body = request.get_json()
    base_game_id = body['baseGameId']
    player_ids = body['playerIds']
    players = db.session.query(Player).filter(Player.id.in_(player_ids)).all()
    games = players_to_games_by_base_game(players, base_game_id)
    first_team_games, second_team_games = sum_split(games)
    first_team = players_from_games(players, first_team_games)
    second_team = players_from_games(players, second_team_games)
    return {
        "firstTeamPlayers": first_team,
        "secondTeamPlayers": second_team,
    }
