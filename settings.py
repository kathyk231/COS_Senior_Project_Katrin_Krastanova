import random

class Settings:
    DEFAULTS = dict(
        court_time=240.0,
        evidence_bonus=2,
        toast_bonus=2,
        base_suspicion=2.5,
        lock_time=45.0,
        alert_gain=0.3,
        patrol=True,
        patrol_interval=40.0,
        cost_noise=0.15,
        think_delay=(0.1,0.6),
        suspicion_noise=0.5,
        alert_shift =0.0,
        deadline=600.0
    )

    def __init__(self):
        self.quiet = False
        self.step = 1.0/60.0
        self.reset(0)

    def reset(self, seed=0, **overrides):
        for k,v in self.DEFAULTS.items():
            setattr(self, k, v)
        for k,v in overrides.items():
            if k not in self.DEFAULTS:
                raise KeyError(f"unknown setting: {k}")
            setattr(self, k, v)
        self.seed = seed
        self.rng_cost = random.Random(f"{seed}:cost")
        self.rng_think = random.Random(f"{seed}:think")
        self.rng_judge = random.Random(f"{seed}:judge")

cfg = Settings()