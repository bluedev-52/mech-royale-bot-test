import sys, os, math, collections, multiprocessing as mp
sys.path.insert(0, os.path.expanduser("~/repos/mech-royale-bot"))
from brain.agent import Agent
from sim.engine import Match
from sim.house import HouseBot
def run(seed):
    C = collections.Counter(); first = {}
    class D(Agent):
        def act(self, obs):
            me = obs["self"]; p = me["pos"]
            for d in obs.get("drops", []):
                dist = math.dist(d["pos"][:2], p[:2])
                if d["id"] not in first and d.get("lands_in", 99) <= 12:
                    first[d["id"]] = 1; C["seen12"] += 1
                    C["d<150"] += dist < 150; C["d<80"] += dist < 80
                    C["edge_ok"] += self.time_to_edge(d["pos"][0], d["pos"][1]) > 14 + d.get("lands_in", 0) if self.me else 0
                if d.get("lands_in", 99) <= 0:
                    C["ground_ticks"] += 1
                    if dist < 8: C["in_ring"] += 1
                    if d.get("holder") not in (None, me["id"]): C["held_other"] += 1
            for e in obs["events"]:
                if e["type"] == "drop": C["captured"] += 1
            return super().act(obs)
    slot = seed % 16
    lineup = [("agent", D) if s == slot else ("house", HouseBot) for s in range(16)]
    Match(lineup, seed, timed=(slot,), squad_prey=slot).run()
    return C
if __name__ == "__main__":
    with mp.Pool(8) as p: R = p.map(run, range(1, 17))
    T = sum(R, collections.Counter()); print({k: round(v / len(R), 2) for k, v in T.items()})
