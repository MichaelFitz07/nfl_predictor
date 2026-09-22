import pandas as pd
import math
from elo import create_initial_ratings, update_game, K

def build_feature_table(schedule, ratings=None):
    if ratings is None:
        ratings = create_initial_ratings(schedule)
    schedule = schedule.sort_values('gameday')
    rows = []

    for i, game in schedule.iterrows():
        home = game['home_team']
        away = game['away_team']
        home_won = game['home_score'] > game['away_score']

        elo_diff = ratings[home] - ratings[away]

        rows.append({
            'elo_diff': elo_diff,
            'home_rest': game['home_rest'],
            'away_rest': game['away_rest'],
            'div_game': game['div_game'],
            'home_won': 1 if home_won else 0
        })

        margin = abs(game['home_score'] - game['away_score'])
        mov_multiplier = math.log(margin + 1)
        ratings[home], ratings[away] = update_game(ratings[home], ratings[away], home_won, K * mov_multiplier)

    return pd.DataFrame(rows)