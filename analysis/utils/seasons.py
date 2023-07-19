import pandas as pd
from utils.matches import Match, Matches
from utils.players import Players
from typing import List, Dict
from pprint import pprint
import matplotlib.pyplot as plt
import seaborn as sns
import copy
import matplotlib.ticker as mticker


class Season:
    def __init__(self, season: str, matches: List[Match], squad: Players):
        self.season = season
        self.matches = sorted(matches, key=lambda x: x.date, reverse=False)
        self.match_dates = self.get_match_dates()
        self.season_summary = self.create_season_summary()
        self.season_summary_excluding_cancellations = self.create_season_summary(include_cancellations=False)
        self.player_summaries = self.create_player_summaries(squad=squad)
        self.rolling_summaries = self.rolling_summaries()

    def rolling_summaries(self, include_cancellations=False, n=10) -> Dict:
        last_n_games_pnts = self.pnts_rolling(n=n, include_cancellations=include_cancellations)
        last_n_games_GF = self.GF_rolling(n=n, include_cancellations=include_cancellations)
        last_n_games_GA = self.GA_rolling(n=n, include_cancellations=include_cancellations)

        return {
            "pnts_rolling": last_n_games_pnts,
            "pnts_per_game_rolling": [pnts/n for pnts in last_n_games_pnts],
            "GF_rolling": last_n_games_GF,
            "GA_rolling": last_n_games_GA,
            "GF_per_game_rolling": [GF/n for GF in last_n_games_GF],
            "GA_per_game_rolling": [GA/n for GA in last_n_games_GA],
        }

    def pnts_rolling(self, n=10, include_cancellations=True) -> List[float]:
        pnts_roll = []
        num_matches = len(self.matches)
        for i in range(0, 1+num_matches-n):
            pnts_roll.append(self.points_cnt(matches=self.matches[i:(n+i)], include_cancellations=include_cancellations))

        return pnts_roll

    def GA_rolling(self, n=10, include_cancellations=True) -> List[float]:
        GA_roll = []
        num_matches = len(self.matches)
        for i in range(0, 1+num_matches-n):
            GA_roll.append(self.GA_cnt(matches=self.matches[i:(n+i)], include_cancellations=include_cancellations))

        return GA_roll

    def GF_rolling(self, n=10, include_cancellations=True) -> List[float]:
        GF_roll = []
        num_matches = len(self.matches)
        for i in range(0,1+num_matches-n):
            GF_roll.append(self.GF_cnt(matches=self.matches[i:(n+i)], include_cancellations=include_cancellations))

        return GF_roll

    def create_player_summaries(self, squad: Players):
        season_players = self.season_summary_excluding_cancellations["squad"]
        player_sums_dict = {}
        for a_player in season_players:
            if not squad.is_existing_player(a_player):
                squad.create_player(a_player)
            player_sums_dict[a_player] = squad.players[a_player].create_player_summary(self.season, n=10, matches=self.matches)
        return player_sums_dict

    def get_match(self, date: "str", all_matches: Matches):
        return all_matches.matches[date]

    def get_match_dates(self):
        match_dates = []
        for match_instance in self.matches:
            match_dates.append(match_instance.date)

        return match_dates

    def points_cnt(self, matches: List[Matches], include_cancellations=True):
        point_cnt = 0
        for match in matches:
            if include_cancellations or not match.match_cancellation:
                point_cnt += match.get_points()
        return point_cnt

    def GF_cnt(self, matches: List[Matches], include_cancellations=True):
        GF_tally = 0
        for match in matches:
            if include_cancellations or not match.match_cancellation:
                GF_tally += match.get_GF()
        return GF_tally

    def GA_cnt(self, matches: List[Matches], include_cancellations=True):
        GA_tally = 0
        for match in matches:
            if include_cancellations or not match.match_cancellation:
                GA_tally += match.get_GA()
        return GA_tally

    def matches_cnt(self, include_cancellations=True):
        matches_tally = 0
        for match in self.matches:
            if include_cancellations or not match.match_cancellation:
                matches_tally += 1
        return matches_tally

    def get_season_players(self):
        squad_players = []
        for match in self.matches:
            squad_players.extend(match.players)
        return list(set(squad_players))

    def season_had_cancelled_matches_check(self) -> bool:
        for match in self.matches:
            if match.match_cancellation:
                return True
        return False

    def league_position(self, include_cancellations=True):
        final_league_position = self.matches[-1].league_position
        if include_cancellations:
            return final_league_position
        else:
            season_had_cancelled_matches = self.season_had_cancelled_matches_check()
            if season_had_cancelled_matches:
                return None
            else:
                return season_had_cancelled_matches

    def create_season_summary(self, include_cancellations=True, include_league_position=True):
        points_tally = self.points_cnt(matches=self.matches, include_cancellations=include_cancellations)
        GF_tally = self.GF_cnt(matches=self.matches, include_cancellations=include_cancellations)
        GA_tally = self.GA_cnt(matches=self.matches, include_cancellations=include_cancellations)
        match_tally = self.matches_cnt(include_cancellations=include_cancellations)

        return {
            "num_matches": match_tally,
            "points": points_tally,
            "league_position": self.league_position(include_cancellations) if include_league_position else None,
            "GF": GF_tally,
            "GA": GA_tally,
            "GD": GF_tally-GA_tally,
            "GD/match": (GF_tally-GA_tally)/match_tally,
            "points/match": points_tally/match_tally,
            "squad": self.get_season_players(),
        }

    def print_season(self, exclude_cancellations=True):
        print(f"season:{self.season}")
        if exclude_cancellations:
            pprint(self.season_summary_excluding_cancellations.sort(by="season"), ascending=False)
            print("\n")
        else:
            pprint(self.season_summary)
            print("\n")
            

class Seasons:
    def __init__(self, seasons=Dict[str, Season]):
        self.seasons = seasons
        self.all_matches = self.get_all_matches()

    def get_all_matches(self) -> List[Matches]:
        total_matches =[]
        for season_name, season in self.seasons.items():
            for match in season.matches:
                total_matches.append(match)
        return total_matches

    def append_season(self, season: Season):
        self.seasons[season.season] = season

    def print_seasons(self):
        for _, season in self.season.items():
            season.print_season()

    def aggregate_season_summaries(self) -> pd.DataFrame:
        season_summaries_df = pd.DataFrame()
        for season_name, season in self.seasons.items():
            season_summary = copy.copy(season.season_summary_excluding_cancellations)
            season_summary.pop("squad")
            season_summary["season"] = season_name
            summary_df = pd.DataFrame(season_summary, index=[0])
            season_summaries_df = pd.concat([season_summaries_df, summary_df])
        return season_summaries_df

    def barplot_season_stat(self, statistic: str, large_plot=True) -> None:
        aggregated_summary = self.aggregate_season_summaries()
        if large_plot:
            plt.figure(figsize=(8,8),)
        else:
            plt.figure(figsize=(9,7),)
        sns.set(font_scale=2)
        aggregated_summary_all_season_filtered=copy.copy(aggregated_summary.query("season != 'all time'").sort_values(by="season", ascending=True))
        num_seasons = aggregated_summary_all_season_filtered.shape[0]
        fig = sns.barplot(
            x="season",
            y=statistic,
            data=aggregated_summary_all_season_filtered,
        )
        ths = [str(i)+"th" for i in range(1, num_seasons+1)]
        fig.xaxis.set_major_locator(mticker.FixedLocator(list(fig.get_xticks())))
        fig.set_xticklabels(ths)
        plt.title(f"{statistic} over season")
        plt.tight_layout()
        plt.show()

    def lineplot_season_stat(self, statistic: str) -> None:
        aggregated_summary = copy.copy(self.aggregate_season_summaries())
        plt.figure(figsize=(8, 8),)
        sns.set(font_scale=2)
        aggregated_summary_all_season_filtered = copy.copy(aggregated_summary.query("season != 'all time'").sort_values(by="season", ascending=True))
        num_seasons = aggregated_summary_all_season_filtered.shape[0]
        ths = [str(i) + "th" for i in range(1, num_seasons + 1)]
        fig = sns.lineplot(
            x="season",
            y=statistic,
            data=aggregated_summary_all_season_filtered.reset_index(),
        )
        fig.xaxis.set_major_locator(mticker.FixedLocator(list(fig.get_xticks())))
        fig.set_xticklabels(ths)
        plt.title(f"{statistic} per season")
        plt.tight_layout()
        plt.show()

    def multilineplot_season_stat(self, large_plot=True, normalise=False) -> None:
        aggregated_summary = self.aggregate_season_summaries()
        num_seasons = aggregated_summary.query("season != 'all time'").shape[0] ### Should probably change this for a method that gets all seasons number
        aggregated_summary_GF = aggregated_summary[["season", "num_matches", "GF"]].rename(columns={"GF": "Goals"})
        if not normalise:
            aggregated_summary_GF["Goal type"] = "GF"
        else:
            aggregated_summary_GF["Goal type"] = "GF/match"

        aggregated_summary_GA = aggregated_summary[["season", "num_matches", "GA"]].rename(columns={"GA": "Goals"})
        if not normalise:
            aggregated_summary_GA["Goal type"] = "GA"
        else:
            aggregated_summary_GA["Goal type"] = "GA/match"

        aggregated_summary_union = pd.concat([aggregated_summary_GA, aggregated_summary_GF])
        aggregated_summary_union['Goals/per game'] = aggregated_summary_union.Goals/aggregated_summary_union.num_matches


        if large_plot:
            plt.figure(figsize=(12, 8),)
        else:
            plt.figure(figsize=(9, 7),)

        aggregated_summary_all_season_filtered = copy.copy(aggregated_summary_union.query("season != 'all time'").sort_values(by="season", ascending=True))
        sns.set(font_scale=2)
        if not normalise:
            fig = sns.barplot(
                x="season",
                y="Goals",
                data=aggregated_summary_all_season_filtered,
                hue="Goal type",
            )
            title_str='goals over season'
        else:
            fig = sns.barplot(
                x="season",
                y="Goals/per game",
                data=aggregated_summary_all_season_filtered,
                hue="Goal type",
            )
            title_str = 'goals/match over seasons'
        ths = [str(i) + "th" for i in range(1, num_seasons + 1)]
        fig.legend(loc="upper right", bbox_to_anchor=(0.95, -0.07))
        fig.set_xticklabels(ths)
        plt.title(title_str)
        plt.tight_layout()
        plt.show()