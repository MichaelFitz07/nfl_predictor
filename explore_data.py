import nflreadpy as nfl


schedule = nfl.load_schedules([2025]).to_pandas()

print(schedule.shape)
print(schedule.head())
print(schedule.columns.tolist())