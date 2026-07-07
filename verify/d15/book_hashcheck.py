#!/usr/bin/env python3
"""
D15 V3 — WALK-FORWARD BOOK BYTE-IDENTITY  (v2.4 / fa6abd0 / engine md5 7c199a1f)

Regenerates the walk-forward valuation book (the calendar-indexed s4 matrix) on
fa6abd0 by running the committed generator engine/rl_after/s4_matrix_M1v7.py in an
isolated materialised v2.4 tree. That generator sets _BOARD_PATH=False (Luke's
backtest exemption: the D14 board-only laws — V0 curve, KPP floor — are OFF on the
historical book so it must reproduce v2.3 byte-for-byte). The regenerated book is
compared against the committed artifact session_2026-07-03/d14/s4_matrix_v24.json.

NOTE ON KEYS: the generator serialises the matrix keyed by str(id(p)) — a Python
memory address (s4_matrix_M1v7.py:108) — which is NOT stable across interpreter runs.
So the RAW files can never share a sha256 by construction (only the top-level key
strings differ; every record is identical). Byte-identity is therefore established on
the STABLE-KEYED book: both sides are re-keyed by player identity (player,type,year,
pick), each record canonicalised (sort_keys, tight separators), and the concatenation
sha256'd. That is exactly the "2649 stable-keyed players, maxΔ=0" the PR#21 audit
claimed. Both the raw-file shas (differ — explained) and the stable-key shas (must be
identical) are reported, plus the max numeric delta over anchor/cur/Vpath.

PASS = stable-keyed canonical sha256 identical AND max numeric delta == 0.
On mismatch: reports the first divergent record/value.

Run:  python verify/d15/book_hashcheck.py   (from repo root, pinned venv)
"""
import os, sys, json, hashlib, shutil, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _d15_common as C

COMMITTED_REL = 'session_2026-07-03/d14/s4_matrix_v24.json'


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def stable_key(rec):
    return (rec.get('player'), rec.get('type'), rec.get('year'), rec.get('pick'))


def load_by_stable_key(path):
    d = json.load(open(path))
    out = {}
    collisions = []
    for _idk, rec in d.items():
        k = stable_key(rec)
        if k in out:
            collisions.append(k)
        out[k] = rec
    return out, collisions


def canon_sha(by_key):
    """sha256 of the stable-key-sorted, canonicalised records (id-independent)."""
    h = hashlib.sha256()
    for k in sorted(by_key.keys(), key=lambda t: json.dumps(t, sort_keys=True)):
        h.update(json.dumps(k, sort_keys=True).encode())
        h.update(json.dumps(by_key[k], sort_keys=True, separators=(',', ':')).encode())
    return h.hexdigest()


def max_numeric_delta(a, b):
    """max abs delta over anchor/cur and Vpath across shared stable keys; also count differing records."""
    worst = (0.0, None); ndiff = 0
    shared = set(a) & set(b)
    for k in shared:
        ra, rb = a[k], b[k]
        if ra != rb:
            ndiff += 1
        for fld in ('anchor', 'cur', 'old_anchor'):
            va, vb = ra.get(fld), rb.get(fld)
            if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
                d = abs(va - vb)
                if d > worst[0]:
                    worst = (d, f"{k} .{fld}: {va} vs {vb}")
        for i, (va, vb) in enumerate(zip(ra.get('Vpath') or [], rb.get('Vpath') or [])):
            if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
                d = abs(va - vb)
                if d > worst[0]:
                    worst = (d, f"{k} .Vpath[{i}]: {va} vs {vb}")
    return worst, ndiff, len(shared)


def main():
    root = C.repo_root()
    C.ensure_cm_cache(root)
    out_path = os.path.join(root, 'verify', 'd15', 'book_hashes.txt')
    committed = os.path.join(root, COMMITTED_REL)
    L = []
    def P(*a):
        s = ' '.join(str(x) for x in a); print(s); L.append(s)

    sha, exp = C.TREES['v2.4']
    rundir, md5 = C.materialize(sha, root)
    assert md5 == exp, f"v2.4 engine md5 {md5} != expected {exp}"
    ra = os.path.join(rundir, 'engine', 'rl_after')
    regen = os.path.join(rundir, 's4_matrix_regen.json')
    env = C.tree_env(rundir, root)
    env['S4_MATRIX'] = regen
    try:
        proc = subprocess.run([sys.executable, 's4_matrix_M1v7.py'], cwd=ra, env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=1200)
        gen_tail = (proc.stdout or '')[-600:]
        if not os.path.exists(regen):
            raise RuntimeError(f"generator did not write matrix (rc={proc.returncode})\n"
                               f"STDOUT:\n{proc.stdout[-2000:]}\nSTDERR:\n{proc.stderr[-2000:]}")
        h_regen_raw = sha256_file(regen)
        h_commit_raw = sha256_file(committed)
        regen_by, coll_r = load_by_stable_key(regen)
        commit_by, coll_c = load_by_stable_key(committed)
        h_regen_stable = canon_sha(regen_by)
        h_commit_stable = canon_sha(commit_by)
        (worst_d, worst_where), ndiff, nshared = max_numeric_delta(regen_by, commit_by)
        keyset_equal = (set(regen_by) == set(commit_by))
        stable_identical = (h_regen_stable == h_commit_stable)
        pass_ = stable_identical and worst_d == 0.0 and keyset_equal

        P(f"# D15 V3 — WALK-FORWARD BOOK BYTE-IDENTITY   (git {sha} / engine md5 {md5})")
        P(f"# generator: engine/rl_after/s4_matrix_M1v7.py  (_BOARD_PATH=False, backtest exemption)")
        P("")
        P(f"regenerated (fa6abd0) : {len(regen_by)} players   committed {COMMITTED_REL}: {len(commit_by)} players")
        P("")
        P("## RAW FILE sha256 (top-level keys = str(id(p)) memory addresses -> NON-deterministic by construction):")
        P(f"   regen    = {h_regen_raw}")
        P(f"   committed = {h_commit_raw}")
        P(f"   raw identical: {'YES' if h_regen_raw==h_commit_raw else 'NO (expected — id-keyed; see below for value identity)'}")
        P("")
        P("## STABLE-KEYED sha256 (re-keyed by (player,type,year,pick), records canonicalised sort_keys):")
        P(f"   regen    = {h_regen_stable}")
        P(f"   committed = {h_commit_stable}")
        P(f"   stable-key set equal: {'YES' if keyset_equal else 'NO'}   (shared keys: {nshared})")
        P(f"   stable-key collisions: regen={len(coll_r)} committed={len(coll_c)}")
        P(f"   records differing (any field): {ndiff}")
        P(f"   max numeric delta over anchor/cur/old_anchor/Vpath: {worst_d:g}"
          + (f"   at [{worst_where}]" if worst_where else ""))
        P("")
        P(f"## STABLE-KEY IDENTICAL: {'YES' if stable_identical else 'NO'}")
        if not stable_identical:
            only_r = list(set(regen_by) - set(commit_by))[:5]
            only_c = list(set(commit_by) - set(regen_by))[:5]
            if only_r or only_c:
                P(f"   first divergent SECTION — key-set mismatch: regen-only[:5]={only_r} committed-only[:5]={only_c}")
            else:
                for k in sorted(set(regen_by) & set(commit_by), key=lambda t: json.dumps(t, sort_keys=True)):
                    if regen_by[k] != commit_by[k]:
                        P(f"   first divergent SECTION — key {k}:")
                        P(f"     regen    = {json.dumps(regen_by[k])[:400]}")
                        P(f"     committed = {json.dumps(commit_by[k])[:400]}")
                        break
        P("")
        P(f"## VERDICT: {'PASS' if pass_ else 'FAIL'}   "
          f"(walk-forward book {'byte-identical (stable-keyed) to' if pass_ else 'DIFFERS from'} "
          f"the committed v2.4 book; maxΔ={worst_d:g})")
        P("")
        P("## generator stdout (tail):")
        for ln in gen_tail.strip().splitlines():
            P("   " + ln)
    finally:
        shutil.rmtree(rundir, ignore_errors=True)

    open(out_path, 'w').write("\n".join(L) + "\n")
    print(f"\nwrote {out_path}")


if __name__ == '__main__':
    main()
