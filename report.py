import csv
import glob
import statistics as st

path = sorted(glob.glob("results/games*.csv"))[-1]
rows = [r for r in csv.DictReader(open(path)) if int(r["seed"]) >= 1001]
print(path, len(rows), "games")
cols = ["game_time", "cup_refusals", "locks", "unlocks", "confiscations", "destroys", "spoils", "digs",
        "servant_replans", "royal_replans", "servant_no_plan", "royal_no_plan", "servant_failures",
        "royal_failures", "servant_actions", "royal_actions", "servant_skipped", "royal_skipped", "servant_plan_s", "royal_plan_s"]
for c in cols:
    v=[float(r[c]) for r in rows]
    print(f"{c:18}  mean  {st.mean(v):8.2f}   sd {st.stdev(v):7.2f}   max  {max(v):8.2f}   min  {min(v):8.2f}")
count={}
for r in rows:
    key = (r["winner"], r["how"])
    count[key] = count.get(key, 0) + 1
print(count)