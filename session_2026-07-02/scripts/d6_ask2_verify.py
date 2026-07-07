#!/usr/bin/env python3
# D6 ASK 2c — run the WIRED prototype (engine/prototypes/floor_pricing_clamp.py) against the head
# engine and verify the clamp is a pure lower bound: byte-exact everywhere except below-floor ND
# entrants, per variant. One engine load; both variants are post-ev clamps so share the load.
import os, sys, io, json, contextlib, hashlib
RA = '/home/claude/rl_workspace/rl_after'
REPO = '/home/user/afl-rl-engine'
os.environ.update(PYTHONHASHSEED='0', RL_GAMMA='0.85', RL_PICK1='3000', RL_RUCK_TAX='0.25',
                  RL_RECENCY_DECAY='0.72', RL_PRIOR_TREES='400', PAR_RAMPS='22')
sys.path[:0] = [RA, '/home/claude/rl_workspace/forward_valuation', '/home/claude/rl_vendor',
                os.path.join(REPO, 'engine', 'prototypes')]
os.chdir(RA)
g = {}
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('_merged_recover.py').read().split('print("=== AFTER')[0], g)
ev, MA = g['ev'], g['MA']
draftval, delisted = g['draftval'], g['delisted']
ENG = hashlib.md5(open('_merged_recover.py', 'rb').read()).hexdigest()[:8]
import floor_pricing_clamp as FPC
PROTO_MD5 = hashlib.md5(open(os.path.join(REPO, 'engine', 'prototypes', 'floor_pricing_clamp.py'), 'rb').read()).hexdigest()[:8]
print(f'[d6-ask2c] engine={ENG} prototype={PROTO_MD5}')

res = {}
for variant in ('A', 'B'):
    saves = []
    ef = FPC.make_ev_final(ev, draftval, delisted, variant=variant, saves=saves)
    n_all = n_same = n_up = n_down = n_nonnd_moved = 0
    with contextlib.redirect_stdout(io.StringIO()):
        for p in MA.data:
            if p.get('_retired'):
                continue
            try:
                v0 = ev(p, 2026)
            except Exception:
                continue
            v1 = ef(p, 2026)
            n_all += 1
            if v1 == v0:
                n_same += 1
            elif v1 > v0:
                n_up += 1
                if p.get('type') != 'ND':
                    n_nonnd_moved += 1
            else:
                n_down += 1
    res[variant] = dict(n_all=n_all, n_same=n_same, n_up=n_up, n_down=n_down,
                        n_nonnd_moved=n_nonnd_moved, n_saves=len(saves),
                        agg_lift=round(sum(s['lift'] for s in saves), 1), saves=saves)
    print(f'  variant {variant}: evaluated={n_all} byte-identical={n_same} lifted={n_up} '
          f'LOWERED={n_down} (must be 0) non-ND moved={n_nonnd_moved} (must be 0) '
          f'saves-collector={len(saves)} agg lift={res[variant]["agg_lift"]}')
out = dict(engine_md5=ENG, proto_md5=PROTO_MD5, variants=res)
json.dump(out, open(sys.argv[1], 'w'), indent=1)
print('wrote', sys.argv[1])
