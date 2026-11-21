import sys, os, math, collections, multiprocessing as mp
sys.path.insert(0, os.path.expanduser("~/repos/mech-royale-bot"))
from brain.agent import Agent, wrap, yaw_pitch
from sim.engine import Match
from sim.house import HouseBot
def run(seed):
    C = collections.Counter(); E = []
    class D(Agent):
        def select_target(self):
            r = super().select_target(); self._lt = r; return r
        def act(self, obs):
            self._lt = None
            a = super().act(obs)
            me = obs["self"]; ws = me["weapons"]; kinds = [w["kind"] if w else None for w in ws]
            vis = [m for m in obs.get("mechs", []) if m.get("kind") == "mech" and math.dist(m["pos"][:2], me["pos"][:2]) < 230]
            fired = any(a.get("fire", [False, False]))
            g = ws[kinds.index("gun")] if "gun" in kinds else None
            if fired: c = "fire"
            elif self._lt is None: c = "vis_no_target" if vis else "no_enemy"
            else:
                th, s, clear = self._lt
                d = math.dist(th.pos[:2], me["pos"][:2])
                if g and g.get("reload", 0) > 0: c = "reload"
                elif not clear: c = "not_clear"
                elif s < self.P["fire_min_off"]: c = "low_score"
                elif d > 230: c = "far"
                else:
                    err = abs(wrap(a["aim"][0] - me["aim"][0]))
                    c = "aim_err>%.0fdeg" % (5 if err > 0.087 else 1 if err > 0.0175 else 0)
                    E.append(err)
            C[c] += 1
            return a
    slot = seed % 16
    lineup = [("agent", D) if s == slot else ("house", HouseBot) for s in range(16)]
    Match(lineup, seed, timed=(slot,), squad_prey=slot).run()
    return C
if __name__ == "__main__":
    with mp.Pool(8) as p: Cs = p.map(run, range(1, 17))
    T = sum(Cs, collections.Counter()); n = sum(T.values())
    for k, v in T.most_common(): print(f"{k:16s} {v:6d} {100*v/n:5.1f}%")
