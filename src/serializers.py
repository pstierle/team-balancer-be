from constants import base_games

def serialize_player(self):
    games = []
    if self.games:
        games = list(map(serialize_game, self.games))
    return {
        "id": self.id,
        "name": self.name,
        "games": games
    }
    
def serialize_game(self):
    return {
        "id": self.id,
        "elo": self.elo,
        "player_id": self.player_id,
        "base_game_id": self.base_game_id,
    }
    
def serialize_game(self):
    return {
        "id": self.id,
        "elo": self.elo,
        "baseGame": next(filter(lambda x: x['id'] == self.base_game_id, base_games), None),
    }
    