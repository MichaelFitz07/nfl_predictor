import pandas as pd
import nflreadpy as nfl
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from model import train_everything, predict_game



app = FastAPI()


# let the react frontend (on port 5173) call this api
# without this the browser blocks it for security (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",              # local dev
        "https://nfl-predictor-1.onrender.com",   # deployed frontend
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# train ONCE when the server boots, keep it all in memory
# (dont wanna retrain on every request, that'd be dead slow)
print("training model on startup...")
model, scaler, ratings = train_everything()
print("done, ready to predict")


# test endpoint - just checks the server's alive
@app.get("/")
def home():
    return {"message": "nfl predictor api is running"}


@app.get("/predict")
def predict(home_team: str, away_team: str):
    if home_team not in ratings:
        return {"error": f"unknown home team: {home_team}"}
    if away_team not in ratings:
        return {"error": f"unknown away team: {away_team}"}
    if home_team == away_team:
        return {"error": "a team can't play itself"}

    home_prob = predict_game(home_team, away_team, ratings, model, scaler)

    margin = estimate_margin(ratings[home_team], ratings[away_team])

    return {
        "home_team": home_team,
        "away_team": away_team,
       
        "predicted_margin": margin,
        "home_win_probability": home_prob,
        "away_win_probability": 1 - home_prob,          # away is just the flip side
        "home_rating": round(ratings[home_team]),        # send the elo ratings too
        "away_rating": round(ratings[away_team]),
    }

# rough predicted score from the elo gap - not exact, just a plausible-looking estimate
# rough predicted margin from the elo gap - just the gap expressed as points
def estimate_margin(home_rating, away_rating):
    margin = (home_rating - away_rating) / 25   # gap -> points
    return round(margin)


# lets the frontend (or anyone) get the list of valid team codes
@app.get("/teams")
def teams():
    return {"teams": sorted(ratings.keys())}



# re-pull data and rebuild the model/ratings - called on a schedule to stay current
@app.get("/refresh")
def refresh():
    global model, scaler, ratings
    model, scaler, ratings = train_everything()
    return {"status": "refreshed"}


# returns all games for a given week, each with a prediction
@app.get("/week")
def week(week_number: int):
    # load this season's schedule
    sched = nfl.load_schedules([2026]).to_pandas()

    # just the games for the requested week
    games = sched[sched["week"] == week_number]

    results = []
    for _, game in games.iterrows():
        home = game["home_team"]
        away = game["away_team"]

        # skip if we somehow dont have ratings for a team
        if home not in ratings or away not in ratings:
            continue

        home_prob = predict_game(home, away, ratings, model, scaler)
        margin = estimate_margin(ratings[home], ratings[away])

        # was it already played? (blank score = not yet)
        played = pd.notna(game["home_score"])

        results.append({
            "home_team": home,
            "away_team": away,
            "home_win_probability": home_prob,
            "away_win_probability": 1 - home_prob,
            "predicted_margin": margin,
            "played": bool(played),
            "home_score": int(game["home_score"]) if played else None,
            "away_score": int(game["away_score"]) if played else None,
        })

    return {"week": week_number, "games": results}

from elo import create_initial_ratings, regress_to_mean, update_game, expected_score, K
import math


@app.get("/record")
def record():
    # rebuild ratings through 2025 (start point for 2026)
    start_ratings = create_initial_ratings(nfl.load_schedules([2021]).to_pandas())
    for season in [2021, 2022, 2023, 2024, 2025]:
        sched = nfl.load_schedules([season]).to_pandas()
        start_ratings = regress_to_mean(start_ratings, 0.5)
        played = sched[sched["home_score"].notna()].sort_values("gameday")
        for _, g in played.iterrows():
            h, a = g["home_team"], g["away_team"]
            if h not in start_ratings or a not in start_ratings:
                continue
            home_won = g["home_score"] > g["away_score"]
            margin = abs(g["home_score"] - g["away_score"])
            mult = math.log(margin + 1)
            start_ratings[h], start_ratings[a] = update_game(start_ratings[h], start_ratings[a], home_won, K * mult)

    # walk 2026 forward: PREDICT with the ML model before updating
    start_ratings = regress_to_mean(start_ratings, 0.5)
    sched_2026 = nfl.load_schedules([2026]).to_pandas()
    played_2026 = sched_2026[sched_2026["home_score"].notna()].sort_values("gameday")

    correct = 0
    total = 0
    for _, g in played_2026.iterrows():
        h, a = g["home_team"], g["away_team"]
        if h not in start_ratings or a not in start_ratings:
            continue
        # PREDICT with the ML model using ratings BEFORE this game
        home_prob = predict_game(h, a, start_ratings, model, scaler)
        model_picks_home = home_prob > 0.5
        home_won = g["home_score"] > g["away_score"]
        if model_picks_home == home_won:
            correct += 1
        total += 1
        # THEN update ratings with the result
        margin = abs(g["home_score"] - g["away_score"])
        mult = math.log(margin + 1)
        start_ratings[h], start_ratings[a] = update_game(start_ratings[h], start_ratings[a], home_won, K * mult)

    accuracy = round(correct / total * 100, 1) if total > 0 else 0
    return {"correct": correct, "total": total, "accuracy": accuracy}