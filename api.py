from fastapi import FastAPI
from model import train_everything, predict_game
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


# let the react frontend (on port 5173) call this api
# without this the browser blocks it for security (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # only allow our frontend, not just anyone
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