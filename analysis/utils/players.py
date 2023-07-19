import pandas as pd
from typing import List
from utils.matches import Match
from pprint import pprint
import matplotlib.pyplot as plt
import seaborn as sns
import copy


class Player:
    def __init__(self, name: str):
        self.name = name
        self.summaries = {}

    def create_player_summary(
        self,
        summary_name: str,
        matches: List[Match],
        n: int,
        update_summary: bool = True,
        ):
            matches_played = self.matches_played_cnt(matches, exclude_full_keeping_stints=False)
            points = self.points_cnt(matches)
            keeping_half_stints = self.keeping_half_cnt(matches)
            goals = self.goal_cnt(matches)
            GF_during_appearances = self.GF_in_matches_played(matches)
            GA_during_appearances = self.GA_in_matches_played(matches)
            total_outfield_40mins_cnt = self.total_outfield_40mins(matches)
            rolling_10_match_goals_per_outfield_40mins = self.get_player_rolling_n_match_goals_per_outfield_40mins(matches, n=n)

            player_summary = {
                "matches_played": matches_played,
                "points": points if matches_played > 0 else None,
                "GF in matches played": GF_during_appearances if matches_played > 0 else None,
                "GA in matches played": GA_during_appearances if matches_played > 0 else None,
                "GF/match played": GF_during_appearances/matches_played if matches_played > 0 else None,
                "GA/match played": GA_during_appearances / matches_played if matches_played > 0 else None,
                "points/match played": points/matches_played if matches_played > 0 else None,
                "goals": goals if matches_played > 0 else None,
                "assists": self.assist_cnt(matches) if matches_played > 0 else None,
                "goals/outfield 40mins": goals/total_outfield_40mins_cnt if total_outfield_40mins_cnt > 0 else None,
                "assists/outfield 40mins": self.assists_per_outfield_40mins(matches),
                "matches played/1/2 goal keeping stint": matches_played/keeping_half_stints if keeping_half_stints > 0 else -1,
                "number of 1/2 keeping stints/40mins": keeping_half_stints/matches_played if matches_played > 0 else None,
                "% of matches scored in": self.scored_during_matches_pct(matches, exclude_full_keeping_stints=True),
                "number of 1/2 keeping stints":keeping_half_stints if matches_played > 0 else None,
                "matches since last keeping stint": self.matches_since_last_keeping_stint(matches) if matches_played > 0 else None,
                "goals/outfield 40mins (last 10 matches)": rolling_10_match_goals_per_outfield_40mins if rolling_10_match_goals_per_outfield_40mins != "not enough matches" else 0,
            }

            if update_summary:
                self.summaries.update({summary_name: player_summary})
            return player_summary

    def get_player_rolling_n_match_goals_per_outfield_40mins(self, matches: List[Match], n: int, logging=False):
        player = self.name
        sorted_matches = sorted(matches, key=lambda x: x.date, reverse=True)
        goal_cnt = 0
        num_40mins_outfield_mins = 0
        for match in sorted_matches:
            if player in match.players:
                keepers = match.get_keepers()
                scorers = match.goalscorers
                num_keeping_halves_during_match = keepers.count(player)
                if num_keeping_halves_during_match < 2:
                    num_40mins_outfield_mins += 1-0.5*num_keeping_halves_during_match
                    if player in scorers.keys():
                        goal_cnt += scorers[player]

            if num_40mins_outfield_mins >= n:
                break

        if num_40mins_outfield_mins >= n:
            return goal_cnt/num_40mins_outfield_mins
        else:
            if logging:
                print(f"{player} has not played {n} matches to create rolling summary")

    def outfield_40mins(self, match: Match):
        match_players = match.players
        if self.name in match_players:
            num_player_half_keeping_stint = self.get_num_player_half_keeping_stint(match)
            return 1 - 0.5*num_player_half_keeping_stint
        else:
            return 0

    def total_outfield_40mins(self, matches: List[Match]):
        num_outfield_40mins_cnt = 0
        for match in matches:
            num_outfield_40mins_cnt += self.outfield_40mins(match)
        return num_outfield_40mins_cnt

    def matches_since_last_keeping_stint(self, matches: List[Match]):
        matches_since_keeping_stint = 0
        has_done_stint = False
        for match in reversed(matches):
            match_players = match.players
            if self.name in match_players:
                has_done_stint = True
                return matches_since_keeping_stint
            else:
                matches_since_keeping_stint += 1

        return matches_since_keeping_stint if has_done_stint else -1

    def get_num_player_half_keeping_stint(self, match: Match) -> float:
        keepers = match.get_keepers()
        num_keeping_halves_during_match = keepers.count(self.name)
        return num_keeping_halves_during_match

    def does_player_do_full_keeping_stint(self, match: Match) -> bool:
        if self.get_num_player_half_keeping_stint(match) == 2:
            return True
        else:
            return False

    def matches_played_cnt(self, matches: List[Match], exclude_full_keeping_stints: bool = False):
        player_cnt = 0
        for match in matches:
            match_players = match.players
            if self.name in match_players:
                did_player_do_full_keeping_stint = self.does_player_do_full_keeping_stint(match)
                if not did_player_do_full_keeping_stint or not exclude_full_keeping_stints:
                    player_cnt += 1
        return player_cnt

    def points_cnt(self, matches: List[Match]):
        point_cnt = 0
        for match in matches:
            match_players = match.players
            if self.name in match_players:
                point_cnt += match.get_points()
        return point_cnt

    def keeping_half_cnt(self, matches: List[Match]):
        keeping_cnt = 0
        for match in matches:
            match_players = match.players
            if self.name in match.players:
                keepers = match.get_keepers()
                keeping_cnt += keepers.count(self.name)
        return keeping_cnt

    def goal_cnt(self, matches: List[Match]):
        goals = 0
        for match in matches:
            match_players = match.players
            if self.name in match_players:
                scorers = match.get_goalscorers()
                if self.name in scorers.keys():
                    goals += scorers[self.name]
        return goals

    def assist_cnt(self, matches: List[Match]):
        assists = 0
        for match in matches:
            match_players = match.players
            if self.name in match_players:
                assisters = match.get_assisters()
                if assisters:
                    if self.name in assisters.keys():
                        assists += assisters[self.name]
        return assists

    def assists_per_outfield_40mins(self, matches: List[Match]):
        assists = 0
        num_outfield_40mins = 0
        for match in matches:
            match_players = match.players
            if self.name in match_players:
                assisters = match.get_assisters()
                if assisters:
                    num_outfield_40mins += self.outfield_40mins(match)
                    if self.name in assisters.keys():
                        assists += assisters[self.name]
        return assists/num_outfield_40mins if num_outfield_40mins > 0 else None

    def GF_in_matches_played(self, matches: List[Match]):
        total_GF = 0
        for match in matches:
            if self.name in match.players:
                total_GF += match.get_GF()
        return total_GF

    def GA_in_matches_played(self, matches: List[Match]):
        total_GA = 0
        for match in matches:
            if self.name in match.players:
                total_GA += match.get_GA()
        return total_GA

    def scored_during_matches_pct(self, matches: List[Match], exclude_full_keeping_stints:bool=False):
        num_matches_scored_in = 0
        num_matches_played = 0
        for match in matches:
            if self.name in match.players:
                if not exclude_full_keeping_stints or not self.does_player_do_full_keeping_stint(match):
                    scorers = match.get_goalscorers()
                    num_matches_played += 1
                    if self.name in scorers.keys():
                        num_matches_scored_in += 1
        return 100*num_matches_scored_in/num_matches_played if num_matches_played > 0 else None

    def print_players_summary(self):
        print(self.name)
        pprint(self.summaries)
        print("\n")
        

class Players:
    def __init__(self):
        self.players = {}

    def is_existing_player(self, player: str) -> bool:
        return player in self.players.keys()

    def create_player(self, player: str) -> None:
        self.players[player] = Player(name=player)

    def print_player_summaries(self) -> None:
        for name, player in self.players.items():
            player.print_players_summary()

    def aggregate_player_summaries(self, aggregation_season: str) -> pd.DataFrame:
        player_summaries_list = []
        for name, player in self.players.items():
            if aggregation_season in self.players[name].summaries.keys():
                player_summary = copy.copy(self.players[name].summaries[aggregation_season])
                player_summary["name"] = name
                player_summaries_list.append(player_summary)

        summary_df = pd.DataFrame(player_summaries_list)
        return summary_df

    def barplot_player_stat(
        self,
        aggregation_season: str,
        statistic: str,
        minimum_matches_played = 10,
        sort_ascending = False,
        plot_average = True,
        top_n_players = 100,
        large_plot = True,
    ) -> None:
        aggregated_summary = self.aggregate_player_summaries(aggregation_season)
        if large_plot:
            plt.figure(figsize=(12,8),)
        else:
            plt.figure(figsize=(9,7),)

        sns.set(font_scale=2)
        fig = sns.barplot(
            x="name",
            y=statistic,
            data=aggregated_summary,
            order=aggregated_summary.query(f"matches_played >= {minimum_matches_played}").sort_values(statistic, ascending=sort_ascending).name[0:(top_n_players-1)],
        )
        plt.title(f"Player's {statistic} (season: {aggregation_season})")
        fig.set_xticklabels(fig.get_xticklabels(), rotation=45)
        if plot_average:
            fig.axhline(aggregated_summary.query(f"matches_played >= {minimum_matches_played}")[statistic].mean(), linestyle="--", label=f"{statistic} avg")
            plt.legend()
        plt.tight_layout()
        plt.show()