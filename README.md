# NFL Game Predictor

A full-stack machine learning app that predicts NFL game outcomes. Pick two teams and get a win probability, predicted margin, and confidence rating.




**🏈 [Try it live](https://nfl-predictor-1.onrender.com)**

IF TESTING PLEASE GIVE 30-60 SECONDS TO WAKE UP DUE TO IT BEING ON THE FREE RENDER TIER


## What it does

Pick a home and away team, and the app predicts the home team's win probability, a rough predicted margin, a confidence rating, and shows each team's Elo rating. Predictions come from a machine learning model trained on four seasons of NFL data.

## Results

Evaluated on the held-out 2025 season:
- **Accuracy:** 66%
- **vs "always pick home" baseline:** 53%
- **vs Elo baseline:** ~63%
- **Log loss:** 0.63

## How it works

- **Elo rating engine**  built from scratch to rate team strength, updated game-by-game with a margin-of-victory adjustment.
- **Features**  each team's Elo going into the game (elo_diff), rest days, and whether it's a divisional matchup.
- **Model** logistic regression trained on 2021–2024, tested on 2025. Uses the Elo rating as its strongest feature.
- **Backend**  FastAPI serving predictions, with input validation.
- **Frontend** React (Vite).
- **Deployment** backend and frontend deployed as two separate services on Render.

## Key decisions

- **Elo as a baseline**  a simple, interpretable benchmark the ML model had to beat.
- **Temporal train/test split**  trained on past seasons, tested on a later one, to avoid leaking future information.
- **No Vegas odds as inputs**  the goal was to beat the betting market, so using it as a feature would be circular.
- **Rejected XGBoost**  it underperformed logistic regression; the signal is largely linear and the dataset is modest, so the simpler model generalised better.
- **Margin of victory** improved probability calibration (log loss) even though it didn't change raw accuracy.

## Tech stack

Python · scikit-learn · pandas · FastAPI · React · Vite · Render · nflreadpy

## Running locally

**Backend:**
```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn api:app --reload
```

**Frontend:**
```
cd frontend
npm install
npm run dev
```
