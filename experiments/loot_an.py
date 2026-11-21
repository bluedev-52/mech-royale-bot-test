import sys, os, math, json
from multiprocessing import Pool
sys.path.insert(0, os.path.expanduser("~/repos/mech-royale-bot"))
from brain.agent import Agent
from sim.engine import Match
from sim.house import HouseBot

class Rec(Agent):
    log = None
    def act(self, obs):
        a = super().act(obs)
        me = obs["self"]; kinds = [w["kind"] if w else None for w in me["weapons"]]
        L = Rec.log
        good = [p for p in obs.get("pickups", []) if p["kind"] in ("laser", "lightning")]
        if good and L["first_seen"] is None:
            d = min(math.dist(p["pos"][:2], me["pos"][:2]) for p in good)
            L["first_seen"] = (round(obs["t"], 1), round(d))
        if good:
            L["seen_ticks"] += 1
            L["min_d"] = min(L["min_d"], min(math.dist(p["pos"][:2], me["pos"][:2]) for p in good))
        k2 = [k for k in kinds if k and k != "gun"]
        if k2 and L["got"] is None:
            L["got"] = (k2[0], round(obs["t"], 1))
        for e in obs["events"]:
            if e["type"] == "kill":
                L["kills"].append(round(obs["t"], 1))
        return a

def run(seed):
    slot = seed % 16
    Rec.log = {"first_seen": None, "seen_ticks": 0, "min_d": 1e9, "got": None, "kills": []}
    lineup = [("agent", Rec) if s == slot else ("house", HouseBot) for s in range(16)]
    res = Match(lineup, seed, timed=(slot,), squad_prey=slot).run()
    me = res["mechs"][slot]
    L = Rec.log; L["seed"] = seed; L["place"] = me["place"]; L["death"] = me["death_t"]; L["min_d"] = round(L["min_d"])
    return L

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 48
    with Pool(8) as p:
        out = p.map(run, range(1, n + 1))
    json.dump(out, open(os.path.expanduser("~/work/loot_an.json"), "w"))
    for L in out:
        print(L)
