import sys, os, math, json, collections, multiprocessing as mp
sys.path.insert(0, os.path.expanduser("~/repos/mech-royale-bot"))
from brain.agent import Agent
from sim.engine import Match
from sim.house import HouseBot
PAR = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
def run(seed):
    C = collections.Counter(); last = {}
    class D(Agent):
        def __init__(self, *a, **k):
            super().__init__(*a, **k); self.P.update(PAR)
        def act(self, obs):
            me = obs["self"]; p = me["pos"]; t = obs["t"]
            vis = [m for m in obs.get("mechs", []) if m.get("kind") == "mech"]
            ds = sorted(math.dist(m["pos"][:2], p[:2]) for m in vis)
            last.update(t=t, hp=me["hp"], nvis=len(vis), d0=ds[0] if ds else None, energy=me["energy"])
            if 200 <= t <= 325:
                C["w_ticks"] += 1; C["w_vis"] += bool(vis); C["w_vis_lt60"] += bool(ds and ds[0] < 60)
                for e in obs["events"]:
                    if e["type"] == "damaged": C["w_dmg"] += e["amount"]; C["w_dmg_" + e.get("weapon", "?")] += e["amount"]
            return super().act(obs)
    slot = seed % 16
    lineup = [("agent", D) if s == slot else ("house", HouseBot) for s in range(16)]
    Match(lineup, seed, timed=(slot,), squad_prey=slot).run()
    C["died_in_window"] += 200 <= last.get("t", 0) <= 325
    if 200 <= last.get("t", 0) <= 325:
        C["death_nvis"] += last["nvis"]; C["death_d0"] += last["d0"] or 0; C["death_energy"] += last["energy"]
    return C
if __name__ == "__main__":
    with mp.Pool(8) as p: R = p.map(run, range(1, 25))
    T = sum(R, collections.Counter()); n = len(R); k = max(1, T["died_in_window"])
    print("per match:", {a: round(b / n, 2) for a, b in T.items() if a.startswith("w_")})
    print("died in window", T["died_in_window"], "/", n, "at death: visible", round(T["death_nvis"] / k, 1),
          "nearest m", round(T["death_d0"] / k), "energy", round(T["death_energy"] / k))
