# TASK-014 accepted-stack current-board composition

Diagnostic only. No keeper utility, production export, board value or TASK-006 output is used.

## Compared stacks

- baseline: accepted TASK-009 zero-history state separation;
- candidate: TASK-009 plus accepted TASK-012 evidence-weighted demonstrated ceiling.

## Result

The complete authoritative 804-player universe was scored at five leads per player, producing 4,020 rows per stack.

All fields that TASK-012 is required not to change were exactly identical across every row:

- meaningful-season probability;
- conditional games;
- expected games;
- probabilities of averages at least 80, 90, 100, 110 and 120.

Current-board effects were modest relative to the five-year forecast scale:

- mean absolute five-year expected-points change: 16.71;
- median five-year change: -0.48;
- range: -99.42 to +149.03;
- mean absolute rank movement: 1.55;
- maximum rank movement: 9;
- top-100 overlap: 99 of 100.

The reporting-only current established low-ceiling cohort contains 39 players and 195 player-lead rows. Its mean conditional-average change is +0.115 points and mean expected-points change is -0.073 per player-lead row. This is a diagnostic current-state effect, not an outcome target and not a player-ordering gate.

## Provenance

New GitHub-hosted jobs began failing before step 1 while unrelated older jobs continued normally. The compact evidence was therefore reproduced locally using:

- `annual_rows.csv` from successful TASK-003N run `28916943549`, artifact `8157996496`, SHA-256 `650a2e2399af1776127807d653bffe113aeba4baaf4d928671721172f7991766`;
- the authoritative registry from the same artifact, SHA-256 `40a01c6f653453ce8ee75539e7458f0fc652862f5c415a64156c8b23340e09b4`;
- merged TASK-009 blob `97874e9d8223a27a873a214b2fa38cddd64a2999`;
- merged TASK-012 blob `7a6af010793e5354ba613d080d3b5ffa8de13a20`;
- dependency versions inside the repository's allowed ranges.

The branch retains an executable GitHub Actions workflow so the same report can be regenerated when hosted runners resume. Full annual and player-rollup outputs remain diagnostic artifacts; compact cohort and extreme-change evidence is committed here.
