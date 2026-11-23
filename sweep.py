import sys
from batch import run_batch, summarize, print_summary

SWEEPS = {
    "court_time": [180,240,300,360,480],
    "evidence_bonus": [0,1,2],
    "lock_time": [20,45,90],
    "alert_shift": [-1.0,0.0,1.0,2.0],
    "patrol": [False,True]
}
def main(n=30, workers=1):
    table = []
    for param, values in SWEEPS.items():
        print(f"\n== {param} (all other settings at their defaults) ==")
        for v in values:
            rows = run_batch(f"{param}={v}", n, csv_path="results/sweep.csv", workers=workers, **{param:v})
            s = summarize(f"{param}={v}",rows)
            print_summary(s)
            table.append((param, v, s))
    print("\nInside the 40-60% target, closest to 50% first:")
    hits = sorted((abs(s["rate"] -0.5),p,v,s) for p,v,s in table if 0.4<=s["rate"]<=0.6)
    for _,p,v,s in hits:
        print(f"  {p}={v}:  {s['rate']:.0%}  (CI {s['lo']:.0%}-{s['hi']:.0%})")
    if not hits:
        print("  none: no single setting reaches the target, try other combinations.")

    off = next(s for p,v,s in table if p == "patrol" and v is False)
    on = next(s for p,v,s in table if p == "patrol" and v is True)
    overlap = not (on["hi"] < off["lo"] or off["hi"] < on["lo"])
    print(f"\nPatrol: off {off['rate']:.0%} -> on {on['rate']:.0%}; "
          f"{'confidence intervals overlap, difference is not shown' if overlap else 'difference is clear.'}")

if __name__ == "__main__":
    a=sys.argv[1:]
    main(int(a[0]) if a else 30, int(a[1]) if len(a) > 1 else 1)