import nflreadpy as nfl
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, log_loss

from elo import run_season, regress_to_mean, K
from features import build_feature_table

# --- train on 2024, carry over, test on 2025 ---
schedule_2024 = nfl.load_schedules([2024]).to_pandas()
schedule_2025 = nfl.load_schedules([2025]).to_pandas()

ratings_after_2024 = run_season(schedule_2024, K)
ratings_start_2025 = regress_to_mean(ratings_after_2024, 0.5)

train_table = build_feature_table(schedule_2024)
test_table = build_feature_table(schedule_2025, ratings=ratings_start_2025)

feature_cols = ['elo_diff', 'home_rest', 'away_rest', 'div_game']
X_train = train_table[feature_cols]
y_train = train_table['home_won']
X_test = test_table[feature_cols]
y_test = test_table['home_won']

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = LogisticRegression()
model.fit(X_train_scaled, y_train)

predictions = model.predict(X_test_scaled)
probabilities = model.predict_proba(X_test_scaled)[:, 1]

ml_accuracy = accuracy_score(y_test, predictions)
ml_log_loss = log_loss(y_test, probabilities)

print("ML Accuracy:", ml_accuracy)
print("ML Log loss:", ml_log_loss)