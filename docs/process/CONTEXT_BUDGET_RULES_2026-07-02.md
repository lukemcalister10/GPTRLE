# CONTEXT BUDGET RULES — making chats last — 02/07/2026
### For BUILD + SUPERVISOR kickoffs and Luke's own practice.

MENTAL MODEL: the budget is TOKENS, not words or wall-clock. Every turn re-reads the
whole thread. Prose is cheap; file/tool content is dense and is paid again on every
subsequent turn. Chats die from WATCHING themselves work (inspecting, listing,
re-reading) not from working. Principle: heavy content lives on disk; the chat carries
only slices and verdicts.

COST TABLE (rough):
- CHEAP: prose replies, file WRITES (paid once, never re-dumped), short tool verdicts.
- MODERATE: targeted greps, view_range slices, script tails.
- EXPENSIVE: pasted bodies, whole-file views, directory trees, full archive listings,
  error-retry loops, loose text-file attachments, big web fetches.

## BUILD RULES (biggest consumer)
1. Verify by SCRIPT, never by inspection. verify_restore.sh (md5s + panel + named
   players → 15-line PASS/FAIL) is a required kickoff asset. Inspection-based
   restore-verify costs ~50-100x more for the same assurance.
2. Never print what can be grepped: no full tar listings, no directory trees, no
   whole-file engine views. Manifest is a file to query, not display.
3. Long outputs go to files; chat gets the verdict tail only.
4. Error loops are token fires: switch mechanism after two failures (this rule is a
   context rule as much as a discipline rule).
5. Build chats are one-directive-scoped by default: kickoff → restore-verify →
   directive → checkpoint → retire. The tarball is the memory, not the chat.

## SUPERVISOR RULES (should be the cheapest, longest-lived chat)
6. Ingest summaries, never bodies: enforce the ≤30-line build-return template; bounce
   nonconforming returns. Keep own replies short — verbosity is a context cost.
   (Full pastes killed the strongest supervisor instance.)

## LUKE'S RULES (the input channel)
7. Headline + attachment, never paste bodies when relaying.
8. HOW you attach matters: text uploads (.md/.txt/.csv) inject IN FULL into context on
   attach; tarballs are binary → disk only, read in slices. Ship documents INSIDE the
   tarball unless the doc is small or you want it fully read. (Likely explains several
   mystery chat deaths.)
9. Never re-paste what is already in the thread — reference by turn or filename. Every
   re-paste is paid on every subsequent turn.
10. Disposable scratch chats for one-off heavy jobs (exploration, conversion, big file
    inspection); carry only the conclusion back.

## SAFETY NETS
11. Burn reporting (standing rule): any turn ingesting significant file content ends
    with "heavy turn: ~N KB entered context." Three heavy-turn flags in a session =
    checkpoint + rotate. Converts the invisible budget into a visible one.
12. No load-bearing number lives only in chat prose — always also in a file. Auto
    context management summarizes older turns (lossy); if state lives in files,
    compaction is harmless instead of a corruption risk.

HIGHEST-IMPACT THREE: script-based verification (1), summary-only supervisor ingestion
(6), docs-inside-the-tarball (8).
