"""ER patient flow analysis: where do waits pile up, and what do long waits cost?"""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("data/ed_visits.csv", parse_dates=["arrival_time"])
order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
low = df[df.esi_level >= 3]          # lower-acuity patients, the ones who can walk out

overall = {"visits": len(df), "median_wait": df.wait_minutes.median(), "lwbs_pct": df.left_without_being_seen.mean() * 100,
           "median_los_hr": df[df.left_without_being_seen == 0].length_of_stay_min.median() / 60}
by_esi = df.groupby("esi_level").agg(visits=("wait_minutes", "size"), median_wait=("wait_minutes", "median"),
                                      lwbs_pct=("left_without_being_seen", lambda s: s.mean() * 100)).round(1)
by_hour = low.groupby("arrival_hour").agg(median_wait=("wait_minutes", "median"), lwbs_pct=("left_without_being_seen", lambda s: s.mean() * 100)).round(1)
peak = by_hour.sort_values("median_wait", ascending=False).head(3)

bins = [-1, 30, 60, 90, 120, 10_000]; labels = ["0-30", "31-60", "61-90", "91-120", "120+"]
low = low.assign(bucket=pd.cut(low.wait_minutes, bins, labels=labels))
by_bucket = low.groupby("bucket", observed=True)["left_without_being_seen"].mean() * 100

# Illustration only: cap midday (11am-2pm) lower-acuity waits at 60 minutes
rate = low.groupby("bucket", observed=True)["left_without_being_seen"].mean()
mid = low[low.arrival_hour.isin([11, 12, 13])]
before = rate[pd.cut(mid.wait_minutes, bins, labels=labels)].sum()
after = rate[pd.cut(mid.wait_minutes.clip(upper=60), bins, labels=labels)].sum()

# Charts
heat = low.pivot_table(index="weekday", columns="arrival_hour", values="wait_minutes", aggfunc="median").reindex(order)
fig, ax = plt.subplots(figsize=(10, 3.6)); im = ax.imshow(heat.values, cmap="YlOrRd", aspect="auto")
ax.set_xticks(range(24)); ax.set_xticklabels(heat.columns); ax.set_yticks(range(7)); ax.set_yticklabels(order)
ax.set_xlabel("Arrival hour"); ax.set_title("Median wait (min), lower-acuity patients, by weekday and hour"); fig.colorbar(im); plt.tight_layout(); plt.savefig("charts/wait_heatmap.png", dpi=150); plt.close()
fig, ax = plt.subplots(figsize=(6, 3.6)); ax.bar(by_bucket.index.astype(str), by_bucket.values, color="#2B645D")
ax.set_xlabel("Wait to see a provider (min)"); ax.set_ylabel("% who left without being seen"); ax.set_title("Longer waits, more patients leave"); plt.tight_layout(); plt.savefig("charts/lwbs_by_wait.png", dpi=150); plt.close()
fig, ax = plt.subplots(figsize=(6, 3.6)); ax.bar(by_esi.index.astype(str), by_esi.median_wait, color="#E9A114")
ax.set_xlabel("Acuity level (ESI, 1 = most urgent)"); ax.set_ylabel("Median wait (min)"); ax.set_title("Median wait by acuity"); plt.tight_layout(); plt.savefig("charts/wait_by_acuity.png", dpi=150); plt.close()

lines = ["# Results (simulated data)", "", f"Visits: {overall['visits']:,} | median wait {overall['median_wait']:.0f} min | LWBS {overall['lwbs_pct']:.1f}% | median length of stay (seen patients) {overall['median_los_hr']:.1f} hr", "",
 "By acuity:", "```", by_esi.to_string(), "```", "Longest median waits by arrival hour (lower acuity):", "```", peak.to_string(), "```",
 "LWBS % by wait bucket (lower acuity):", "```", by_bucket.round(1).to_string(), "```", "",
 f"Illustration: capping 11am-2pm lower-acuity waits at 60 min -> expected LWBS visits {before:.0f} -> {after:.0f} ({(before-after)/before*100:.0f}% fewer in that window)"]
open("results.md", "w").write("\n".join(lines)); print("\n".join(lines))
