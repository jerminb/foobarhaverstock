import glob
import json
from os.path import basename
from pathlib import Path
from utils.matches import Match, Matches
from utils.players import Players
from utils.seasons import Season, Seasons

BASE_DIR = Path(__file__).absolute().parent.parent
LEAGUE_DATA_DIR = Path.joinpath(BASE_DIR, "data/league-results/")


def load_json(filename: str):
    """Return a dictionary from a json file"""
    with open(filename) as json_data:
        return json.load(json_data)


if __name__ == "__main__":
    seasons = {}
    all_Matches_class = Matches()
    Squad = Players()
    total_seasons = []
    season_paths = glob.glob(f"{LEAGUE_DATA_DIR}/*")
    
    for season_path in season_paths:
        season_name = basename(season_path)
        season_matches = []
        match_paths = glob.glob(f"{season_path}/*.json")
        for match_path in match_paths:
            match = load_json(match_path)
            Match_instance = Match(match_result=match)
            season_matches.append(Match_instance)
            all_Matches_class.append_match(Match_instance)
            
            if season_name != match["season"]:
                raise ValueError("Matches of season path belongs to multiple seasons")
        
        if season_name in total_seasons:
            raise ValueError("Matches belongs to a pre-existing season")
        else:
            total_seasons.append(season_name)
        
        seasons[season_name] = Season(season=season_name, matches=season_matches, squad=Squad)
    
    FoobarSeasons = Seasons(seasons=seasons)
    matches_list = [match for _, match in all_Matches_class.matches.items()]
    FoobarSeasons.append_season(season=Season(season="all time", matches=matches_list, squad=Squad))
    
    # Squad plots
    FoobarSeasons.multilineplot_season_stat(normalise=True, large_plot=False)
    FoobarSeasons.barplot_season_stat(statistic="points/match", large_plot=False)
    
    # Player plots
    Squad.barplot_player_stat(
        large_plot=False,
        aggregation_season="ending 2022-12-15",
        statistic="goals",
        minimum_matches_played=1)
    Squad.barplot_player_stat(
        large_plot=False,
        aggregation_season="ending 2022-12-15",
        statistic="assists",
        minimum_matches_played=1)
    Squad.barplot_player_stat(
        large_plot=False,
        aggregation_season="ending 2022-12-15",
        statistic="GA/match played",
        sort_ascending=True,
        minimum_matches_played=1)
