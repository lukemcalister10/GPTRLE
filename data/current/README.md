# Current-season player eligibility source

`Players_2026.csv.gz.b64` is the authoritative current-season player list supplied by Luke. It contains 804 player rows with columns:

- `Player Name`
- `AFFL Team`
- `Position/s`

The file is gzip-compressed CSV encoded as base64 because the GitHub connector can create UTF-8 text files but not binary uploads.

Materialise it from the repository root with:

```bash
python - <<'PY'
import base64, gzip
from pathlib import Path
src = Path('data/current/Players_2026.csv.gz.b64')
out = Path('data/current/Players_2026.csv')
out.write_bytes(gzip.decompress(base64.b64decode(src.read_text().strip())))
print(out)
PY
```

The resulting CSV should have one header row and 804 player rows. Treat it as authoritative for the current-season player universe, AFFL team and positional eligibility only. Do not use its current-season fields as historical model features.
