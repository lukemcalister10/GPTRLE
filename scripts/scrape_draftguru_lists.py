#!/usr/bin/env python3
"""Scrape annual DraftGuru AFL club lists into auditable player-season evidence.

This is a data-acquisition utility only. It does not match players to repository
keys and it does not alter benchmark/model behaviour.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.draftguru.com.au"
DEFAULT_YEARS = tuple(range(2018, 2025))
DOB_RE = re.compile(r"\b\d{1,2}\s+[A-Z][a-z]{2}\s+\d{2}\b")
DRAFT_RE = re.compile(
    r"(?:#\d+\s+)?(?:National|Rookie|Pre-Season|Mid-Season|International|"
    r"Zone|SSP|Prelist|Supplemental|Unregistered|Priority|Mini-Draft|"
    r"Scholarship)\s+\d{4}",
    re.IGNORECASE,
)


def clean_text(value: str) -> str:
    return " ".join(str(value).replace("\xa0", " ").split())


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


class Fetcher:
    def __init__(self, cache_dir: Path, delay: float = 0.45) -> None:
        self.cache_dir = cache_dir
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (compatible; AFL-RL-Engine historical-list "
                    "research; +https://github.com/lukemcalister10/GPTRLE)"
                ),
                "Accept": "text/html,application/xhtml+xml",
            }
        )

    def get(self, url: str, cache_path: Path) -> str:
        full_path = self.cache_dir / cache_path
        if full_path.exists():
            return full_path.read_text(encoding="utf-8")

        full_path.parent.mkdir(parents=True, exist_ok=True)
        last_error: Exception | None = None
        for attempt in range(1, 4):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                text = response.text
                if "Draftguru" not in text:
                    raise RuntimeError(f"unexpected response body for {url}")
                full_path.write_text(text, encoding="utf-8")
                time.sleep(self.delay)
                return text
            except Exception as exc:  # fail after bounded retries, never skip
                last_error = exc
                if attempt < 3:
                    time.sleep(attempt * 2)
        raise RuntimeError(f"failed to fetch {url}: {last_error}")


def discover_club_pages(fetcher: Fetcher, year: int) -> list[tuple[str, str]]:
    url = f"{BASE_URL}/lists/{year}"
    html = fetcher.get(url, Path(str(year)) / "index.html")
    soup = BeautifulSoup(html, "html.parser")
    found: dict[str, str] = {}
    expected_prefix = f"/lists/{year}/"
    for anchor in soup.find_all("a", href=True):
        href = str(anchor["href"])
        path = urlparse(urljoin(BASE_URL, href)).path.rstrip("/")
        if not path.startswith(expected_prefix):
            continue
        slug = path[len(expected_prefix) :]
        if not slug or "/" in slug:
            continue
        found[slug] = urljoin(BASE_URL, path)
    pages = sorted(found.items())
    if len(pages) != 18:
        raise RuntimeError(
            f"expected 18 club pages for {year}, discovered {len(pages)}: "
            f"{[slug for slug, _ in pages]}"
        )
    return pages


def find_player_table(soup: BeautifulSoup):
    for table in soup.find_all("table"):
        headers = [clean_text(cell.get_text(" ", strip=True)).lower() for cell in table.find_all("th")]
        if any(header == "player" or header.startswith("player ") for header in headers):
            return table
    raise RuntimeError("could not locate player list table")


def parse_club_page(year: int, club_slug: str, source_url: str, html: str) -> list[dict[str, object]]:
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.find(["h1", "h2"], string=re.compile(r"Playing List for"))
    club_name = clean_text(heading.get_text(" ", strip=True)).split(" Playing List for", 1)[0] if heading else club_slug.replace("-", " ").title()
    table = find_player_table(soup)

    rows: list[dict[str, object]] = []
    for tr in table.find_all("tr"):
        player_link = tr.find("a", href=re.compile(r"^/?players/"))
        cells = tr.find_all("td")
        if player_link is None or not cells:
            continue

        player_name = clean_text(player_link.get_text(" ", strip=True))
        player_url = urljoin(BASE_URL, str(player_link.get("href", "")))
        player_path = urlparse(player_url).path.strip("/")
        player_slug = player_path.split("/", 1)[1] if player_path.startswith("players/") else player_path
        cell_texts = [clean_text(cell.get_text(" ", strip=True)) for cell in cells]
        row_text = clean_text(tr.get_text(" ", strip=True))

        number_cell = cell_texts[0] if cell_texts else ""
        number_match = re.search(r"\d+", number_cell)
        list_number = int(number_match.group()) if number_match else None
        list_marker = clean_text(re.sub(r"\d+", "", number_cell).strip(" .-"))

        dob_match = DOB_RE.search(row_text)
        draft_match = DRAFT_RE.search(row_text)
        grade = ""
        for index, text in enumerate(cell_texts):
            if text == player_name and index + 1 < len(cell_texts):
                candidate = cell_texts[index + 1]
                if re.fullmatch(r"[A-F][+-]?", candidate):
                    grade = candidate
                break

        rows.append(
            {
                "season": year,
                "club": club_name,
                "club_slug": club_slug,
                "list_number": list_number,
                "list_marker": list_marker,
                "player_name": player_name,
                "draftguru_player_slug": player_slug,
                "draftguru_player_url": player_url,
                "dob_text": dob_match.group(0) if dob_match else "",
                "grade": grade,
                "draft_text": draft_match.group(0) if draft_match else "",
                "source_url": source_url,
                "raw_cells_json": json.dumps(cell_texts, ensure_ascii=False, separators=(",", ":")),
                "raw_row_text": row_text,
            }
        )

    if not 30 <= len(rows) <= 60:
        raise RuntimeError(f"unexpected player row count for {year} {club_slug}: {len(rows)}")
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_years(text: str) -> list[int]:
    years: set[int] = set()
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = (int(value) for value in part.split("-", 1))
            years.update(range(start, end + 1))
        else:
            years.add(int(part))
    return sorted(years)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--years", default="2018-2024")
    parser.add_argument("--out", default="build/draftguru")
    parser.add_argument("--delay", type=float, default=0.45)
    args = parser.parse_args()

    years = parse_years(args.years)
    if years != list(DEFAULT_YEARS):
        print(f"Scraping requested years: {years}")
    out = Path(args.out)
    cache = out / "source_html"
    fetcher = Fetcher(cache, delay=args.delay)

    all_rows: list[dict[str, object]] = []
    page_summary: list[dict[str, object]] = []
    for year in years:
        for club_slug, source_url in discover_club_pages(fetcher, year):
            html = fetcher.get(source_url, Path(str(year)) / f"{club_slug}.html")
            rows = parse_club_page(year, club_slug, source_url, html)
            all_rows.extend(rows)
            page_summary.append(
                {
                    "season": year,
                    "club_slug": club_slug,
                    "source_url": source_url,
                    "player_rows": len(rows),
                }
            )
            print(f"{year} {club_slug}: {len(rows)}")

    all_rows.sort(key=lambda row: (int(row["season"]), str(row["club"]), str(row["player_name"]), str(row["draftguru_player_slug"])))
    raw_fields = [
        "season",
        "club",
        "club_slug",
        "list_number",
        "list_marker",
        "player_name",
        "draftguru_player_slug",
        "draftguru_player_url",
        "dob_text",
        "grade",
        "draft_text",
        "source_url",
        "raw_cells_json",
        "raw_row_text",
    ]
    raw_path = out / "draftguru_lists_2018_2024_raw.csv"
    write_csv(raw_path, all_rows, raw_fields)

    eligibility_rows = [
        {
            "season": row["season"],
            "club": row["club"],
            "player_name": row["player_name"],
            "draftguru_player_slug": row["draftguru_player_slug"],
            "draftguru_player_url": row["draftguru_player_url"],
            "dob_text": row["dob_text"],
            "draft_text": row["draft_text"],
            "list_marker": row["list_marker"],
            "historically_listed": True,
            "source_url": row["source_url"],
        }
        for row in all_rows
    ]
    eligibility_path = out / "draftguru_eligibility_2018_2024.csv"
    write_csv(
        eligibility_path,
        eligibility_rows,
        [
            "season",
            "club",
            "player_name",
            "draftguru_player_slug",
            "draftguru_player_url",
            "dob_text",
            "draft_text",
            "list_marker",
            "historically_listed",
            "source_url",
        ],
    )

    pages_path = out / "page_summary.csv"
    write_csv(pages_path, page_summary, ["season", "club_slug", "source_url", "player_rows"])

    duplicates: dict[tuple[int, str], list[str]] = {}
    for row in eligibility_rows:
        key = (int(row["season"]), str(row["draftguru_player_slug"]))
        duplicates.setdefault(key, []).append(str(row["club"]))
    duplicate_rows = [
        {"season": season, "draftguru_player_slug": slug, "clubs": "|".join(sorted(clubs)), "count": len(clubs)}
        for (season, slug), clubs in sorted(duplicates.items())
        if len(clubs) > 1
    ]
    duplicates_path = out / "same_season_duplicate_players.csv"
    write_csv(duplicates_path, duplicate_rows, ["season", "draftguru_player_slug", "clubs", "count"])

    manifest = {
        "source": "DraftGuru annual AFL club-list pages",
        "source_base_url": BASE_URL,
        "years": years,
        "club_pages": len(page_summary),
        "player_season_rows": len(all_rows),
        "same_season_duplicate_player_rows": len(duplicate_rows),
        "files": {},
    }
    for path in [raw_path, eligibility_path, pages_path, duplicates_path]:
        manifest["files"][path.name] = {"sha256": sha256_file(path), "bytes": path.stat().st_size}
    manifest_path = out / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if len(page_summary) != len(years) * 18:
        raise RuntimeError("club-page total failed final validation")
    if not all_rows:
        raise RuntimeError("no player-season rows extracted")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
