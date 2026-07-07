#!/usr/bin/env python3
# doc_lint.py — mechanized doc-hygiene gate (PROCESS_CHANGES §2). Run before every tarball cut; exits 1 on FAIL.
#   python3 doc_lint.py [TREE_ROOT]
# LIVE forward-status docs: banned status words ("closed"/"done") + superseded-hash-claimed-current are FAILs.
# HISTORY docs (changelog/provenance/archived handover): past-tense narration is legitimate -> hash-claim check ONLY.
import os, re, sys
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
SUPERSEDED = ["8c6d5582", "55e3c3a9", "7147b824", "7c199a1f"]  # lineage candidates: never label current/LATEST/head. (7c199a1f=v2.4 pre-dial, superseded by baked c47cb43d. 8aed420a=prior working head, pervasive in past-tense history, so its retirement is tracked via the CHANGELOG lineage banner, not this staleness trigger.)
BANNED   = re.compile(r'\b(closed|done)\b', re.I)       # five-state vocab bans these as status words
STALE    = re.compile(r'\b(LATEST|pending|not yet|TODO)\b')
# Warn allowlist: legitimate gap/gate statements, not stale status (tuned 2026-07-02).
ALLOW    = re.compile(r'(not yet created|pending luke|decision pending)', re.I)
CURCLAIM = re.compile(r'(current|latest|head)', re.I)
LIVE    = ["START_HERE.md", "CHECKPOINT_MANIFEST.md", "REQUIRED_INPUTS.md",
           "docs/UNRESOLVED.md", "docs/KICKOFF_PROMPT.md", "SHIP_GATES.md", "BAKE_CHECKLIST.md"]
HISTORY = ["PROVENANCE_2026-07-01.md", "docs/archive/HANDOVER_historical.md"]
# NOTE: docs/CHANGELOG.md is the lineage record (its job is to list historical candidate hashes) -> exempt by design.
fails, warns = [], []
def scan(rel, live):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return
    for i, ln in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
        low = ln.lower()
        exempt = any(w in low for w in ("supersede", "lineage", "banned", "five-state", "reconciliation"))
        for h in SUPERSEDED:
            if h in ln and CURCLAIM.search(ln) and not exempt:
                fails.append(f"{rel}:{i}: superseded hash {h} claimed current: {ln.strip()[:84]}")
        if live and not exempt:
            if BANNED.search(ln) and "ban" not in low:
                fails.append(f"{rel}:{i}: banned status word (use five-state): {ln.strip()[:84]}")
            if STALE.search(ln) and not ALLOW.search(low):
                warns.append(f"{rel}:{i}: stale status word: {ln.strip()[:72]}")
for rel in LIVE:
    scan(rel, True)
for rel in HISTORY:
    scan(rel, False)
print(f"doc_lint: {len(fails)} FAIL, {len(warns)} WARN  (live={len(LIVE)} history={len(HISTORY)})")
for f in fails:
    print("  FAIL", f)
for w in warns[:20]:
    print("  warn", w)
sys.exit(1 if fails else 0)
