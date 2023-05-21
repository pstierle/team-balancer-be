import uuid
from flask import Blueprint
from database import Player, Game, db
from serializers import serialize_player
from flask import request, Response
from util import auth_guard
from constants import base_games

player_router = Blueprint("player_router", __name__)


@player_router.route("/player", methods=["GET"])
@auth_guard()
def get_players():
    players = (
        db.session.query(Player)
        .join(Game)
        .filter(Player.user_id == request.environ["user_id"])
        .all()
    )
    return list(map(serialize_player, players))


@player_router.route("/player", methods=["DELETE"])
@auth_guard()
def delete_player():
    body = request.get_json()
    Player.query.filter(Player.id == body["id"]).delete()
    Game.query.filter(Game.player_id == body["id"]).delete()
    db.session.commit()
    return Response(status=200)


@player_router.route("/player", methods=["PUT"])
@auth_guard()
def update_player():
    body = request.get_json()
    player = Player.query.filter(Player.id == body["id"]).join(Game).first()
    player.name = body["name"]
    db.session.add(player)

    for game in player.games:
        updated_game = next(filter(lambda n: n["id"] == game.id, body["games"]), None)
        game.elo = updated_game["elo"]
        db.session.add(game)

    db.session.commit()

    return serialize_player(player)


@player_router.route("/player", methods=["POST"])
@auth_guard()
def create_player():
    print(request.environ.get("user_id"))
    if request.environ.get("user_id"):
        player = Player(
            name=request.json["name"],
            user_id=request.environ.get("user_id"),
            id=str(uuid.uuid4()),
        )
        db.session.add(player)
        db.session.commit()

        for base_game in base_games:
            game = Game(
                elo=0,
                player_id=player.id,
                base_game_id=base_game["id"],
                id=str(uuid.uuid4()),
            )
            db.session.add(game)

        db.session.commit()
        return serialize_player(
            Player.query.filter(Player.id == player.id).join(Game).first()
        )
