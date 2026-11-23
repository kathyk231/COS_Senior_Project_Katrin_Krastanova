import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import ast
import csv
import math
import sys
import time
import pygame
from concurrent.futures import ProcessPoolExecutor
from player_state import PlayerState, Role
from character import Character
from settings import Settings, cfg
from world_setup import create_world
from world_actions import build_world_actions
from role_sabotage import sabotage_actions
from ai_controller import make_ai
from servant_quests import create_servant_quests
from royal_quests import create_royal_quests

STEP = 1.0/30.0
MAX_TIME = 900.0
R, S = Role.ROYAL, Role.SERVANT
SPAWNS = {R: (1068, 880), S:(900,1500)}
STAMP = time.strftime("%Y%m%d%H%M%S")

def quests_for(role):
    return create_servant_quests() if role == S else create_royal_quests()
def progress(ctrl):
    done = sum(q.current for q in ctrl.manager.quests)
    return round(done / sum(len(q.steps) for q in ctrl.manager.quests), 2)

def run_game(seed, label="base", max_time= MAX_TIME, **overrides):
    pygame.init()
    pygame.display.set_mode((1,1))
    cfg.reset(seed, **overrides)
    cfg.quiet = True
    cfg.step = STEP
    started = time.perf_counter()
    servant = Character("Servant AI", SPAWNS[S], PlayerState(S))
    royal = Character("Royal AI", SPAWNS[R], PlayerState(R))
    chars = [servant, royal]
    castle,navmesh, grid, anchors = create_world(royal)
    castle.characters = chars
    for c in chars:
        c.update_room(castle)
    actions = build_world_actions(castle, anchors) + sabotage_actions(castle)
    ctrls = {c.state.role:make_ai(c, castle, anchors, grid, actions, quests_for(c.state.role), chars) for c in chars}
    order = [ctrls[S], ctrls[R]]
    while castle.time < max_time and not castle.result:
        for ctrl in order:
            ctrl.update(STEP, navmesh)
            if castle.result:
                break
        castle.update(STEP)
        navmesh.update_doors(STEP, [(c.position, c.radius) for c in chars])
        for c in chars:
            c.update_room(castle)
    result = castle.result or {"winner": "none", "how": "timeout"}
    n = lambda key: len(castle.sabotage.get(key, []))
    row = {"label": label, "seed":seed, "winner": result["winner"], "how": result.get("how", ""), "game_time":round(castle.time,1), "servant_progress":progress(ctrls[S]), "royal_progress": progress(ctrls[R]), "cup_refusals":royal.suspicion, "locks":n("lock"), "unlocks":n("unlock"), "confiscations": n("confiscate"), "destroys": n("destroy"), "spoils":n("spoil"), "digs":n("dig")}
    for name, role in (("servant", S), ("royal", R)):
        st = ctrls[role].agent.stats
        row.update({f"{name}_replans":st["replans"], f"{name}_no_plan":st["no_plan"], f"{name}_failures":st["action_failures"], f"{name}_actions": st["actions_done"], f"{name}_skipped": st["steps_skipped"], f"{name}_plan_s": round(st["plan_seconds"], 3)})
    row.update({f"cfg_{k}": getattr(cfg, k) for k in Settings.DEFAULTS})
    row["wall_s"] = round(time.perf_counter() - started, 2)
    return row

def _job(args):
    seed, label, overrides = args
    return run_game(seed, label, **overrides)

def write_csv(rows, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    new = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        if new:
            w.writeheader()
        w.writerows(rows)

def run_batch(label, n, seed0=1, csv_path=None, workers=1, **overrides):
    csv_path = csv_path or f"results/games_{STAMP}.csv"
    jobs = [(seed0 + i, label, overrides) for i in range(n)]
    if workers > 1:
        with ProcessPoolExecutor(workers) as ex:
            rows = list(ex.map(_job, jobs))
    else:
        rows = [_job(j) for j in jobs]
    write_csv(rows, csv_path)
    return rows

def wilson(k,n,z=1.96):
    if n == 0:
        return 0.0,0.0
    p = k/n
    d = 1 +z *z/n
    center = (p+z*z/(2*n))/d
    half = z* math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return center - half, center + half

def summarize(label, rows):
    n = len(rows)
    sw = sum(r["winner"] == "servant" for r in rows)
    rw = sum(r["winner"] == "royal" for r in rows)
    nw = sum(r["winner"] == "none" for r in rows)
    lo, hi = wilson(sw, n)
    return {"label": label, "n":n,"servant":sw,"royal":rw, "none":nw, "rate": sw/n, "lo":lo, "hi":hi, "mean_time":sum(r["game_time"] for r in rows)/n, "deadline": sum(r["how"] == "deadline" for r in rows)}
def print_summary(s):
    flag = " <- in 40-60% target" if 0.4 <= s["rate"] <= 0.6 else ""
    print(f"{s['label']:26} n={s['n']:3}  servant {s['servant']:3}  ({s['rate']:5.1%}, "
          f"95% CI {s['lo']:.0%}-{s['hi']:.0%})   royal {s['royal']:3}   none  {s['none']:2}  "
          f"deadline {s['deadline']:2}  mean {s['mean_time']:5.0f}s{flag}")
def repro(seed=7):
    skip = {"wall_s", "servant_plan_s", "royal_plan_s"}
    strip = lambda r: {k:v for k, v in r.items() if k not in skip}
    a, b, c = run_game(seed, "repro"), run_game(seed, "repro"), run_game(seed + 1, "repro")
    print("same seed gives the same game:     ", strip(a) == strip(b))
    print("different seed gives a different one: ", strip(a) != strip(c))

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--repro" in args:
        repro()
        sys.exit()
    n = int(args[0]) if args else 10
    ov = {k: ast.literal_eval(v) for k,v in (a.split("=", 1) for a in args[1:])}
    workers = int(ov.pop("workers", 1))
    rows = run_batch("custom", n, workers=workers, **ov)
    for r in rows[:5]:
        print(r["seed"], r["winner"], r["how"], r["game_time"], "wall", r["wall_s"])
    print_summary(summarize("custom " + " ".join(args[1:]), rows))
