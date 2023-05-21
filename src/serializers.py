from constants import base_games
from database import Player, Game

def serialize_player(self: Player) -> Player:
    games = []
    if self.games:
        games = list(map(serialize_game, self.games))
    return {
        "id": self.id,
        "name": self.name,
        "games": games
    }
    
def serialize_game(self: Game) -> Game:
    return {
        "id": self.id,
        "elo": self.elo,
        "player_id": self.player_id,
        "base_game_id": self.base_game_id,
        "baseGame": next(filter(lambda x: x['id'] == self.base_game_id, base_games), None),
    }
    