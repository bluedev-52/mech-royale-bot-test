import sys, os, collections, multiprocessing as mp
sys.path.insert(0, os.path.expanduser("~/repos/mech-royale-bot"))
from brain.agent import Agent
from sim.engine import Match
from sim.house import HouseBot
def run(seed):
    dmg = collections.defaultdict(float); killed = set(); maxhp_lost = {}
    gaps = []  # seconds between consecutive hits on same target
    last = {}
    class D(Agent):
        def act(self, obs):
            for e in obs["events"]:
                if e["type"] == "hit" and isinstance(e.get("target"), int) and e["target"] < 100:
                    tg = e["target"]; dmg[tg] += e["amount"]
                    if tg in last: gaps.append(obs["t"] - last[tg])
                    last[tg] = obs["t"]
                elif e["type"] == "kill":
                    killed.add(e["target"])
            return super().act(obs)
    slot = seed % 16
    lineup = [("agent", D) if s == slot else ("house", HouseBot) for s in range(16)]
    Match(lineup, seed, timed=(slot,), squad_prey=slot).run()
    k = sum(v for t, v in dmg.items() if t in killed); w = sum(v for t, v in dmg.items() if t not in killed)
    return k, w, len(killed), len(dmg), sum(1 for g in gaps if g > 5.0), len(gaps)
if __name__ == "__main__":
    with mp.Pool(8) as p: R = p.map(run, range(1, 25))
    K = sum(r[0] for r in R); W = sum(r[1] for r in R); n = len(R)
    print(f"dmg on later-killed {K/n:.0f}/match, on survivors {W/n:.0f}/match ({100*W/(K+W):.0f}% wasted)")
    print(f"kills {sum(r[2] for r in R)/n:.2f}, targets damaged {sum(r[3] for r in R)/n:.1f}, hit gaps>5s (regen restarts) {sum(r[4] for r in R)/n:.1f} of {sum(r[5] for r in R)/n:.0f}")
