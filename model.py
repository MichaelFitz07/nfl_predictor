import nflreadpy as nfl
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, log_loss

from elo import run_season, regress_to_mean, K, create_initial_ratings
from features import build_feature_table

# grab a few seasons to train on, keep 2025 for testing
train_seasons = [2021, 2022, 2023, 2024]

ratings = None
train_tables = []
for season in train_seasons:
    sched = nfl.load_schedules([season]).to_pandas()
    if ratings is not None:
        ratings = regress_to_mean(ratings, 0.5)   # pull last season back a bit before carrying on
    else:
        ratings = create_initial_ratings(sched)   # first season, everyone starts at 1500
    table = build_feature_table(sched, ratings=ratings)  # heads up: this also leaves ratings at end of season values
    train_tables.append(table)

# stack all the training seasons into one big table
train_table = pd.concat(train_tables, ignore_index=True)

# carry the final ratings into 2025 (the test season)
ratings_start_2025 = regress_to_mean(ratings, 0.5)
schedule_2025 = nfl.load_schedules([2025]).to_pandas()
test_table = build_feature_table(schedule_2025, ratings=ratings_start_2025)

# split the features from the thing we're actually predicting
feature_cols = ['elo_diff', 'home_rest', 'away_rest', 'div_game']
X_train = train_table[feature_cols]
y_train = train_table['home_won']
X_test = test_table[feature_cols]
y_test = test_table['home_won']

# scale it all, learn the scaling from train only so we're not peeking at test
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# train the model
model = LogisticRegression()
model.fit(X_train_scaled, y_train)

# predict on 2025 and see how we did
predictions = model.predict(X_test_scaled)
probabilities = model.predict_proba(X_test_scaled)[:, 1]

ml_accuracy = accuracy_score(y_test, predictions)
ml_log_loss = log_loss(y_test, probabilities)

def predict_game(home_team, away_team, ratings, model, scaler):
    # build the same features the model was trained on
    elo_diff = ratings[home_team] - ratings[away_team]

    # rest + div_game we dont know for a hypothetical game, so just use sensible defaults
    # (7 days rest is the normal week, 0 = not a divisional game)
    home_rest = 7
    away_rest = 7
    div_game = 0

    # has to be the same column order as feature_cols when we trained
    game_features = pd.DataFrame([{
        'elo_diff': elo_diff,
        'home_rest': home_rest,
        'away_rest': away_rest,
        'div_game': div_game
    }])

    # scale it the SAME way as training (scaler already learned the scaling, just transform)
    game_scaled = scaler.transform(game_features)

    # get the probability home wins
    prob = model.predict_proba(game_scaled)[0][1]
    return prob



print("ML Accuracy:", ml_accuracy)
print("ML Log loss:", ml_log_loss)

# quick test - predict a game
prob = predict_game('KC', 'BUF', ratings_start_2025, model, scaler)
print("KC rating:", ratings_start_2025['KC'])
print("BUF rating:", ratings_start_2025['BUF'])