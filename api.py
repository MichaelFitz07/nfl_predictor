from fastapi import FastAPI
from model import train_everything, predict_game

app = FastAPI()

# train ONCE when the server boots, keep it all in memory
# (dont wanna retrain on every request, that'd be dead slow)
print("training model on startup...")
model, scaler, ratings = train_everything()
print("done, ready to predict")


# test endpoint - just checks the server's alive
@app.get("/")
def home():
    return {"message": "nfl predictor api is running"}


# the real one - give it two teams, get back a win prob
@app.get("/predict")
def predict(home_team: str, away_team: str):
    prob = predict_game(home_team, away_team, ratings, model, scaler)
    return {
        "home_team": home_team,
        "away_team": away_team,
        "home_win_probability": prob
    }