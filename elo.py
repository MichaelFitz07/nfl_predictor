import nflreadpy as nfl
import pandas as pd

STARTING_ELO = 1500

def create_initial_ratings(schedule):
    all_teams = pd.concat([schedule['home_team'], schedule['away_team']])
    teams = all_teams.unique()
    return {team: STARTING_ELO for team in teams}

def expected_score(rating_home, rating_away):
    exponent =(rating_away - rating_home) / 400
    pre_output = 10 ** (exponent)
    output = 1 / (1+pre_output)
    return output


def update_rating(rating, expected, actual, k):
    new_rating = rating + k * (actual - expected)
    return new_rating 

# --- run it ---
schedule = nfl.load_schedules([2025]).to_pandas()
ratings = create_initial_ratings(schedule)
print(len(ratings))

# --- test update_rating: equal teams (1500 each), home wins ---
exp = expected_score(1500, 1500)      # expected = 0.5 for equal teams
home_new = update_rating(1500, exp, 1, 20)   # home won  → actual = 1
away_new = update_rating(1500, 1 - exp, 0, 20)  # away lost → actual = 0
print(home_new, away_new)