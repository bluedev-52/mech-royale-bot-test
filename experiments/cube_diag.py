import sys, os, math, collections, multiprocessing as mp
sys.path.insert(0, os.path.expanduser("~/repos/mech-royale-bot"))
from brain.agent import Agent
from sim.engine import Match
from sim.house import HouseBot
def run(seed):
    C = collections.Counter()
    class D(Agent):
        def act(self, obs):
            me = obs["self"]; p = me["pos"]
            C["ticks"] += 1
            if any(m.get("kind") == "npc" for m in obs.get("mechs", [])): C["npc_vis"] += 1
            if obs.get("cubes"): C["cube_vis"] += 1
            if obs.get("crates"): C["crate_vis"] += 1
            for e in obs["events"]:
                if e["type"] == "pickup": C["cube_pick"] += 1
                elif e["type"] == "drop": C["drop_cap"] += 1
                elif e["type"] == "hit" and isinstance(e.get("target"), int) and e["target"] >= 100: C["npc_hits"] += 1
            return super().act(obs)
    slot = seed % 16
    lineup = [("agent", D) if s == slot else ("house", HouseBot) for s in range(16)]
    Match(lineup, seed, timed=(slot,), squad_prey=slot).run()
    return C
if __name__ == "__main__":
    with mp.Pool(8) as p: R = p.map(run, range(1, 17))
    T = sum(R, collections.Counter()); n = len(R)
    print({k: round(v / n, 1) for k, v in T.items()}, "fractions:",
          {k: round(T[k] / T["ticks"], 3) for k in ("npc_vis", "cube_vis", "crate_vis")})
