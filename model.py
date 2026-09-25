import nflreadpy as nfl
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from elo import regress_to_mean, create_initial_ratings
from features import build_feature_table

def train_everything():
    # train on all completed seasons
    train_seasons = [2022, 2023, 2024, 2025]

    ratings = None
    train_tables = []
    for season in train_seasons:
        sched = nfl.load_schedules([season]).to_pandas()
        if ratings is not None:
            ratings = regress_to_mean(ratings, 0.5)
        else:
            ratings = create_initial_ratings(sched)
        table = build_feature_table(sched, ratings=ratings)
        train_tables.append(table)

    train_table = pd.concat(train_tables, ignore_index=True)

    feature_cols = ['elo_diff', 'home_rest', 'away_rest', 'div_game']
    X_train = train_table[feature_cols]
    y_train = train_table['home_won']

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    model = LogisticRegression()
    model.fit(X_train_scaled, y_train)

    # carry ratings through 2026's played games only (2026 is partly played)
    sched_2026 = nfl.load_schedules([2026]).to_pandas()
    played_2026 = sched_2026[sched_2026['home_score'].notna()]
    ratings = regress_to_mean(ratings, 0.5)
    build_feature_table(played_2026, ratings=ratings)

    return model, scaler, ratings


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

