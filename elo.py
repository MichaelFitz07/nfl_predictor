import nflreadpy as nfl
import pandas as pd
import math

K = 20
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


def update_game(home_rating, away_rating, home_won, k):
    # 1. each team's expected score (note the reversed argument order)
    home_expected = expected_score(home_rating, away_rating)
    away_expected = expected_score(away_rating, home_rating)

    # 2. turn "did home win?" into actual scores for both
    home_actual = 1 if home_won else 0
    away_actual = 1 - home_actual

    # 3. update each team with your existing function
    new_home = update_rating(home_rating, home_expected, home_actual, k)
    new_away = update_rating(away_rating, away_expected, away_actual, k)

    # 4. hand both back
    return new_home, new_away


def regress_to_mean(ratings, regression_amount):
    regressed = {}
    for team, rating in ratings.items():
        regressed[team] = STARTING_ELO + (rating - STARTING_ELO) * (1 - regression_amount)
    return regressed



def run_season(schedule, k, ratings=None):
    if ratings is None:
        ratings = create_initial_ratings(schedule)
    schedule = schedule.sort_values('gameday')
    correct = 0
    total = 0


    for i, game in schedule.iterrows():
        home = game['home_team']
        away = game['away_team']
        home_won = game['home_score'] > game['away_score']
        margin = abs(game['home_score'] - game['away_score'])
        mov_multiplier = math.log(margin + 1)   
        


        predection = expected_score(ratings[home], ratings[away]) > 0.5
        if predection == home_won:
            correct = correct + 1
        total = total + 1


        ratings[home], ratings[away] = update_game(ratings[home], ratings[away], home_won, k * mov_multiplier)

    accuracy = correct/total 
    print("Accuracy:", accuracy)    

    return ratings

# --- train on 2024, carry over, test on 2025 ---
schedule_2024 = nfl.load_schedules([2024]).to_pandas()
schedule_2025 = nfl.load_schedules([2025]).to_pandas()

ratings_after_2024 = run_season(schedule_2024, K)
ratings_start_2025 = regress_to_mean(ratings_after_2024, 0.5)
final_ratings = run_season(schedule_2025, K, ratings=ratings_start_2025)
