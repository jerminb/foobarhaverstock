from typing import Dict


class Match:
    def __init__(self, match_result: Dict):
        self.raw_result = match_result
        self.date = match_result["date"]
        self.opposition = match_result["opposition"]
        self.players = match_result["players"]
        self.keepers = match_result["keepers"]
        self.score = match_result["score"]
        self.GF = match_result["GF"]
        self.GA = match_result["GA"]
        self.goalscorers = match_result["goalscorers"]
        self.assists = match_result["assists"] if "assists" in match_result.keys() else None
        self.points = match_result["points"]
        self.league_position = match_result["league_position"]
        self.match_cancellation = match_result["match_cancellation"] == "True"

    def get_points(self):
        return self.points

    def get_GF(self):
        return self.GF

    def get_GA(self):
        return self.GA

    def get_goalscorers(self):
        return self.goalscorers

    def get_assisters(self):
        return self.assists

    def get_keepers(self):
        return self.keepers
    
    
class Matches:
    def __init__(self):
        self.matches = {}

    def append_match(self, match: Match):
        self.matches[match.date] = match