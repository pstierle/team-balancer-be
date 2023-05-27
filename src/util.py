import jwt
import datetime
import flask
import random
from functools import wraps
from os import environ, listdir, path
from serializers import serialize_player
from constants import base_games
from database import User
from database import Player

def team_diff_by_base_game_id(first_team, second_team, base_game_id):
    first_sum = 0
    second_sum = 0
    for player in first_team:
        game = next(filter(lambda x: x['base_game_id'] == base_game_id, player['games']))
        first_sum += game['elo']
    
    for player in second_team:
        game = next(filter(lambda x: x['base_game_id'] == base_game_id, player['games']))
        second_sum += game['elo']
        
    return abs(first_sum - second_sum)
    

def generate_teams_by_elo(players, base_game_id):
    teams = []
    min_diff = 1000
    choice = None
    
    for i in range(20):
        random.shuffle(players)
        team = find_equal_partition_min_sum_dif(players, base_game_id)
        teams.append(team)
        diff = team_diff_by_base_game_id(team['firstTeamPlayers'], team['secondTeamPlayers'], base_game_id)
        if diff <= min_diff:
            choice = team
            min_diff = diff
    
    return choice
    

def find_equal_partition_min_sum_dif(players, base_game_id):
    one = []
    two = []
    
    for idx, player in enumerate(players):
        if idx <= 4:
            one.append(player)
        else:
            two.append(player)
    
    total_sum = 0
    
    for idx, player in enumerate(players):
        game = player_game_by_base_game_id(player, base_game_id)
        total_sum += game.elo
        if idx < len(one):
            one[idx] = players[idx]
        else: 
            two[idx - len(one)] = players[idx]

    
    goal = total_sum / 2

    swapped = False
      
    while swapped:
        for j, player in enumerate(one):
            curSum = 0
            for p in one:
                game = next(filter(lambda x: x.base_game_id == base_game_id, p.games))
                curSum += game.elo 
            
            cur_best_diff = abs(goal - curSum)
            cur_best_index = -1
            
            for i, player in enumerate(two):
                testSum = curSum - player_game_by_base_game_id(one[j]).elo + player_game_by_base_game_id(two[i]).elo
                diff = abs(goal - testSum)
                if diff < cur_best_diff:
                    cur_best_diff = diff
                    cur_best_index = i

            if cur_best_index >= 0:
                swapped = True
                tmp = one[j]
                one[j] = two[cur_best_index]
                two[cur_best_index] = tmp
          
    one.sort(key=lambda x: player_game_by_base_game_id(x, base_game_id).elo, reverse=True)      
    two.sort(key=lambda x: player_game_by_base_game_id(x, base_game_id).elo, reverse=True)      
             
    return {
        'firstTeamPlayers': list(map(serialize_player, one)),
        'secondTeamPlayers': list(map(serialize_player, two)),
    }
  

def players_with_bases_game_images(players: list[Player], host_url: str) -> list[Player]:
    parsed = list(map(serialize_player, players))
    
    for player in parsed:
        for game in player['games']:
            base_game = next(filter(lambda x: x['id'] == game['base_game_id'], base_games))
            game['baseGame'] = base_game_with_icon(base_game, host_url)
            
    return parsed     

def player_game_by_base_game_id(player, base_game_id):
    return next(filter(lambda x: x.base_game_id == base_game_id, player.games))


def base_game_with_icon(base_game, host_url):
    b = base_game
    b["icon"] = f"{host_url}/static/icons/{base_game['name']}.png"
    
    return b

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
