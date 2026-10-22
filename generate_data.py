"""Generate a SIMULATED emergency department visit dataset (one year, ~20k visits).
No real patients, hospitals, or protected health information are used."""
import numpy as np, pandas as pd

rng = np.random.default_rng(7)
sig = lambda x: 1 / (1 + np.exp(-x))
hour_w = np.array([2.0, 1.6, 1.3, 1.1, 1.0, 1.1, 1.5, 2.4, 3.4, 4.2, 4.8, 5.0, 5.0, 4.8, 4.6, 4.6, 4.8, 5.0, 5.0, 4.6, 4.0, 3.4, 2.8, 2.3])
hour_p = hour_w / hour_w.sum()
dow_f = [1.15, 1.0, .97, .97, 1.0, .98, .93]   # Monday busiest (assumption)

times = []
for d in pd.date_range("2025-01-01", "2025-12-31"):
    n = rng.poisson(55 * dow_f[d.dayofweek])
    for h, m in zip(rng.choice(24, n, p=hour_p), rng.integers(0, 60, n)):
        times.append(d + pd.Timedelta(hours=int(h), minutes=int(m)))
df = pd.DataFrame({"arrival_time": times})
n = len(df)
df["arrival_hour"] = df.arrival_time.dt.hour
df["weekday"] = df.arrival_time.dt.day_name()
df["month"] = df.arrival_time.dt.month
df["esi_level"] = rng.choice([1, 2, 3, 4, 5], n, p=[.01, .12, .40, .35, .12])   # 1 = most urgent
df["age_group"] = rng.choice(["0-17", "18-39", "40-64", "65+"], n, p=[.17, .31, .29, .23])

# Assumed staffing (providers on shift): fewer overnight, 3 midday, 4 afternoon/evening
df["providers_on_shift"] = np.select([df.arrival_hour < 7, df.arrival_hour < 15, df.arrival_hour < 23], [2, 3, 4], default=3)
df["arrivals_that_hour"] = df.groupby(df.arrival_time.dt.floor("h"))["arrival_time"].transform("count")
load = df.arrivals_that_hour / df.providers_on_shift
base_wait = df.esi_level.map({1: 1, 2: 8, 3: 20, 4: 22, 5: 20})
wait = base_wait * (0.5 + 0.7 * load ** 2) * rng.lognormal(0, .45, n)
wait = np.where(df.esi_level == 1, rng.uniform(0, 3, n), wait)
df["wait_minutes"] = np.round(wait).astype(int)

p_lwbs = np.where(df.esi_level >= 3, sig(-5 + .035 * df.wait_minutes - .4 * (df.esi_level == 3)), 0)
df["left_without_being_seen"] = (rng.random(n) < p_lwbs).astype(int)
los = df.esi_level.map({1: 300, 2: 280, 3: 220, 4: 130, 5: 100}) * rng.lognormal(0, .35, n) + .5 * df.wait_minutes
df["length_of_stay_min"] = np.round(np.where(df.left_without_being_seen == 1, df.wait_minutes, los)).astype(int)
p_adm = df.esi_level.map({1: .75, 2: .45, 3: .18, 4: .04, 5: .01})
df["disposition"] = np.where(df.left_without_being_seen == 1, "LWBS", np.where(rng.random(n) < p_adm, "Admitted", "Discharged"))
df.drop(columns=["arrivals_that_hour"]).to_csv("data/ed_visits.csv", index=False)
print(f"Wrote data/ed_visits.csv ({n} simulated visits)")
