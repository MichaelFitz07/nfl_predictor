# NFL Predictor  Decisions & Findings

A running log of design decisions, experiments, and reasoning behind them.

## Model: Elo baseline

- **Chose Elo as the baseline model.** Simple, interpretable, industry-recognised
  (FiveThirtyEight, chess, LLM leaderboards). Serves as the bar the future ML
  model must beat. Built from scratch rather than a library to demonstrate
  understanding.
- **Everyone starts at 1500** (flat baseline). Known limitation  a smarter start
  carries prior-season ratings forward (see below).
- **Did NOT seed ratings from Vegas odds.** Deliberate: the goal is to *beat* Vegas,
  so contaminating the model with the betting line would make that comparison
  meaningless (circular). Vegas stays on the evaluation side only.

## Evaluation

- **Temporal split, never random.** Train on 2024, test on held-out 2025. Random
  splits would leak future games into training.
- **Predict *before* updating ratings each game**  otherwise the prediction sees
  the result (data leakage). Hit this bug twice; caught both by being suspicious
  of too-good accuracy (100%, then 77%).
- **Baselines:** coin flip = 50%; "always pick home" (naive) = ~53% on 2025.
  Elo must beat these to be worth anything.
- **Current honest result: 63.2% on held-out 2025** (vs 53% naive).

## Carry-over between seasons

- **Regress prior-season ratings toward the mean between seasons** rather than full
  carry-over or full reset. Reasoning: last season is part skill (persists) + part
  luck (resets)  regression to the mean discounts the luck.
- **Tuned the regression amount:** tried 0.0–1.0. Effect was small (~1.4% spread,
  within noise of a 285-game metric). Locked in 0.5 as a sensible middle.

## Margin of victory

- **Added MOV scaling** using `k * log(margin + 1)`  blowouts move ratings more,
  but with a plateau (log flattens) so freak scores don't dominate and diminishing
  info in big margins is respected.
- **Finding:** helped 2024 (train, 64.9% → 67.0%) but neutral/slightly down on 2025
  (held-out, 63.2% → 62.8%). Kept as a principled feature; effect may be invisible
  to accuracy and show up under log loss instead.

## To do / ideas
- Add log loss as a second metric (accuracy is too coarse to see confidence gains).
- Build feature table → logistic regression (Elo rating as a feature).
- Predict live 2026 games.
- split elo.py into elo.py / features.py / model.py  one job per file. Do once ML experiment is settled.

## ML LOGIC REGRESSIONS FIRST RESULTS 
"First ML model (logistic regression) vs Elo baseline on 2025: ML better on accuracy (66% vs 63%) but slightly worse on log loss (0.641 vs 0.633). Split result  ML picks winners better, Elo slightly better calibrated. NOTE: features unscaled (elo_diff in hundreds, div_game 0/1)  likely hurting ML; scaling is next."

## trying different models 
"tried xgboost (n_est=100, depth=3) vs logistic regression. xgboost did WORSE  63.2%/0.642 vs 66.3%/0.631. why: signal is basically linear (elo_diff dominates), no real interactions to exploit, and 1100 games isnt enough to stop it overfitting. logistic regression wins. lesson: match model complexity to data + signal, dont default to the fancy one."

## steps towards full stack 
"security plan: match effort to the app (portfolio predictor, no users/payments). priorities: 1) secrets out of repo (.gitignore/.env - already doing), 2) input validation on endpoints, 3) dont leak stack traces, 4) https/rate-limit/CORS at deploy. NOT doing: auth, encryption-at-rest, full audit - no users/sensitive data. apply each in context as we build."

## SECURITY 
"Secured appropriately for a public, no-auth demo: secrets kept out of the repo, input validation on endpoints, CORS restricted to the frontend origin, no stack-trace leaks. Not implemented (not needed for this scope): auth, rate limiting, encryption. Production improvements: rate limiting, and caching the trained model to disk instead of retraining on boot."