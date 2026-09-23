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
    # make sure both teams actually exist in our ratings before doing anything
    if home_team not in ratings:
        return {"error": f"unknown home team: {home_team}"}
    if away_team not in ratings:
        return {"error": f"unknown away team: {away_team}"}

    prob = predict_game(home_team, away_team, ratings, model, scaler)
    return {
        "home_team": home_team,
        "away_team": away_team,
        "home_win_probability": prob
    }

# lets the frontend (or anyone) get the list of valid team codes
@app.get("/teams")
def teams():
    return {"teams": sorted(ratings.keys())}