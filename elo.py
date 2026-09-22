import pandas as pd
import math

K = 20              # how much each game moves the ratings
STARTING_ELO = 1500  # everyone starts here

# make a dict of every team starting at 1500
def create_initial_ratings(schedule):
    all_teams = pd.concat([schedule['home_team'], schedule['away_team']])
    teams = all_teams.unique()
    return {team: STARTING_ELO for team in teams}

# work out the home team's chance of winning from the rating gap
# same formula as the social network lol
def expected_score(rating_home, rating_away):
    exponent = (rating_away - rating_home) / 400
    pre_output = 10 ** (exponent)
    output = 1 / (1 + pre_output)
    return output

# nudge a rating up or down based on how the game went vs what we expected
def update_rating(rating, expected, actual, k):
    new_rating = rating + k * (actual - expected)
    return new_rating

# do both teams at once for a single game
def update_game(home_rating, away_rating, home_won, k):
    # each side's expected score (swap the order for away)
    home_expected = expected_score(home_rating, away_rating)
    away_expected = expected_score(away_rating, home_rating)

    # turn win/lose into 1 or 0
    home_actual = 1 if home_won else 0
    away_actual = 1 - home_actual  # opposite of home, keeps it balanced

    new_home = update_rating(home_rating, home_expected, home_actual, k)
    new_away = update_rating(away_rating, away_expected, away_actual, k)

    return new_home, new_away

# pull ratings partway back to 1500 between seasons
# last year matters but teams change, so don't trust it 100%
def regress_to_mean(ratings, regression_amount):
    regressed = {}
    for team, rating in ratings.items():
        regressed[team] = STARTING_ELO + (rating - STARTING_ELO) * (1 - regression_amount)
    return regressed

# run a whole season, update ratings game by game, and track how good the predictions were
def run_season(schedule, k, ratings=None):
    if ratings is None:                       # start fresh unless we're handed ratings to carry on from
        ratings = create_initial_ratings(schedule)
    schedule = schedule.sort_values('gameday')  # gotta go in date order or elo makes no sense
    correct = 0
    total = 0
    total_log_loss = 0

    for i, game in schedule.iterrows():
        home = game['home_team']
        away = game['away_team']
        home_won = game['home_score'] > game['away_score']
        margin = abs(game['home_score'] - game['away_score'])
        mov_multiplier = math.log(margin + 1)  # blowouts count more but flattens off

        p = expected_score(ratings[home], ratings[away])  # predict BEFORE updating (no cheating)

        # accuracy - did we call the winner right
        prediction = p > 0.5
        if prediction == home_won:
            correct = correct + 1
        total = total + 1

        # log loss - punishes being confident and wrong
        y = 1 if home_won else 0
        game_log_loss = -(y * math.log(p) + (1 - y) * math.log(1 - p))
        total_log_loss = total_log_loss + game_log_loss

        # NOW update the ratings with what actually happened
        ratings[home], ratings[away] = update_game(ratings[home], ratings[away], home_won, k * mov_multiplier)

    accuracy = correct / total
    avg_log_loss = total_log_loss / total
    print("Accuracy:", accuracy)
    print("Log loss:", avg_log_loss)

    return ratings