import jwt
import datetime
import flask
import itertools
from functools import wraps
from os import environ, listdir, path
from serializers import serialize_player
from constants import base_games
from database import User
from database import Player, Game


def base_games_with_images(host_url):
    base_games_with_maps = base_games
    static_folder_path = path.abspath(
        path.join(path.dirname(__file__), "..", "src", "static")
    )
    for base_game in base_games:
        maps = []
        base_game["icon"] = f"{host_url}/static/icons/{base_game['name']}.png"
        mapImageFiles = listdir(path.join(static_folder_path, base_game["name"]))
        idx = 0

        for map in mapImageFiles:
            maps.append(
                {
                    "id": idx,
                    "name": map.rsplit(".", 1)[0],
                    "image": f"{host_url}/static/{base_game['name']}/{map}",
                }
            )
            idx += 1

        base_game["maps"] = maps
    return base_games_with_maps


def sum_split(objects):
    total_sum = sum(obj.elo for obj in objects)
    min_difference = float("inf")
    divided_lists = None

    for r in range(1, len(objects) // 2 + 1):
        for combo in itertools.combinations(objects, r):
            sum1 = sum(obj.elo for obj in combo)
            sum2 = total_sum - sum1
            difference = abs(sum1 - sum2)

            if difference < min_difference and len(combo) == len(objects) // 2:
                min_difference = difference
                divided_lists = (
                    list(combo),
                    [obj for obj in objects if obj not in combo],
                )

    return divided_lists


def players_to_games_by_base_game(players, base_game_id=0):
    games = [
        item for sublist in list(map(lambda x: x.games, players)) for item in sublist
    ]
    games_by_base_game = list(
        filter(lambda game: game.base_game_id == base_game_id, games)
    )

    return games_by_base_game


def players_from_games(players: list[Player], games: list[Game]) -> list[Player]:
    found_players: list[Player] = []

    for game in games:
        found_player = next(filter(lambda x: x.id == game.player_id, players))
        found_players.append(serialize_player(found_player))

    return found_players


def sum_players_elo(players, base_game_id):
    player_games = list(map(lambda x: x.games, players))
    player_games_by_base_game = [
        game
        for game in list(itertools.chain(*player_games))
        if game.base_game_id == base_game_id
    ]
    return sum(map(lambda x: x.elo, player_games_by_base_game))


def auth_guard():
    def _auth_guard(f):
        @wraps(f)
        def __auth_guard(*args, **kwargs):
            token = flask.request.headers.get("authorization")
            try:
                decoded = jwt.decode(token, environ["jwt_key"], algorithms=["HS256"])

                user = User.query.filter(User.id == decoded["user_id"]).first()

                if decoded["expires_at"] < get_date():
                    flask.abort(401)
                elif user == None:
                    flask.abort(401)
                else:
                    flask.request.environ["user_id"] = decoded["user_id"]
            except:
                flask.abort(401)
            return f(*args, **kwargs)

        return __auth_guard

    return _auth_guard


def create_if_not_exists(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance is None:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()


def get_date(addDays=0):
    timeNow = datetime.datetime.now()
    if addDays != 0:
        anotherTime = timeNow + datetime.timedelta(days=addDays)
    else:
        anotherTime = timeNow

    return anotherTime.strftime("%d-%m-%Y %H:%M:%S")
