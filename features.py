import pandas as pd
import math
from elo import create_initial_ratings, update_game, K

def build_feature_table(schedule, ratings=None):
    if ratings is None:
        ratings = create_initial_ratings(schedule)
    schedule = schedule.sort_values('gameday')
    rows = []
    recent_form = {}   # team  list of recent results, lives OUTSIDE the loop so it persists

    for i, game in schedule.iterrows():
        home = game['home_team']
        away = game['away_team']
        home_won = game['home_score'] > game['away_score']

        # make sure both teams have a form list (first time we see them)
        if home not in recent_form:
            recent_form[home] = []
        if away not in recent_form:
            recent_form[away] = []

        # READ form BEFORE recording (only past games are in the lists = no leakage)
        home_form = sum(recent_form[home][-5:]) / len(recent_form[home][-5:]) if recent_form[home] else 0.5
        away_form = sum(recent_form[away][-5:]) / len(recent_form[away][-5:]) if recent_form[away] else 0.5

        elo_diff = ratings[home] - ratings[away]

        # record the row with the form features in it
        rows.append({
            'elo_diff': elo_diff,
            'home_rest': game['home_rest'],
            'away_rest': game['away_rest'],
            'div_game': game['div_game'],
            'home_form': home_form,
            'away_form': away_form,
            'home_won': 1 if home_won else 0
        })

        # update elo AND append this game's result to the form lists
        margin = abs(game['home_score'] - game['away_score'])
        mov_multiplier = math.log(margin + 1)
        ratings[home], ratings[away] = update_game(ratings[home], ratings[away], home_won, K * mov_multiplier)

        recent_form[home].append(1 if home_won else 0)
        recent_form[away].append(0 if home_won else 1)

    return pd.DataFrame(rows)