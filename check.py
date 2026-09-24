import nflreadpy as nfl
sched = nfl.load_schedules([2026]).to_pandas()

# find weeks where games are NOT yet played (blank scores)
unplayed = sched[sched['home_score'].isna()]
print("weeks with unplayed games:", sorted(unplayed['week'].unique()))

# and how many games per week overall
print(sched['week'].value_counts().sort_index())