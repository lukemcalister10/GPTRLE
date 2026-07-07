# Historical AFL list eligibility — DraftGuru 2018–2024

This directory contains the reviewed historical-list evidence used to determine whether a repository player was on an AFL club list at each benchmark origin from 2018 through 2024.

## Source and meaning

The source is DraftGuru's annual AFL club-list pages. The acquisition script discovers all 18 club pages for each year and retains the source URL for each positive player-season record.

For this dataset:

- presence on any annual club list means `eligible=True` for that origin year;
- absence from all 18 annual club lists means `eligible=False` for that origin year;
- current 2026 list, retirement, club and position fields are not used;
- no draft-tenure heuristic is used.

## Reviewed identity results

- 1,465 unique DraftGuru people were observed;
- 1,440 were matched to repository player keys;
- 25 were intentionally excluded because they are absent from, or intentionally excluded from, the repository database;
- 5,622 repository player-year rows have verified list presence;
- the complete matrix has 18,564 rows: 2,652 repository keys × 7 origins.

The reviewed decisions are in `draftguru_manual_decisions_2018_2024.csv`. Blank review choices were treated as intentional exclusions. The older Western Bulldogs/Carlton Will Hayes is mapped to `will-hayes-a`.

Duplicate-name identities were separately checked for Bailey Williams, Callum Brown, Josh Kennedy and Sam Reid.

## Committed source files

Large CSVs are gzip-compressed and base64-encoded because the GitHub connector can create UTF-8 text files but not binary uploads:

- `historical_eligibility_2018_2024.csv.gz.b64`
- `draftguru_player_key_map_final.csv.gz.b64`
- `draftguru_players_excluded_from_repository_mapping.csv.gz.b64`
- `database_player_keys.csv.gz.b64`

`final_manifest.json` records SHA-256 hashes of the decoded CSV bytes. `finalization_summary.json` records row and matching totals.

Materialise and verify the CSVs from the repository root with:

```bash
python scripts/materialize_draftguru_historical.py
```

To verify without retaining decoded files:

```bash
python scripts/materialize_draftguru_historical.py --check-only
```

The scraper, conservative automatic matcher and reviewed finaliser are retained under `scripts/` so the evidence can be regenerated and audited.

## Scope boundary

These files provide historical cohort eligibility only. They do not alter frozen legacy behaviour, model training, predictions, current player values, keeper utility or the UI.
