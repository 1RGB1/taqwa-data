#!/usr/bin/env python3
"""
One-off export: tafsir-mcp SQLite `surah_content` -> taqwa-data surah-info
datasets (Deep Study "About this Surah", feature #3 Phase 4).

Source: Tafsir Center for Quranic Studies dataset (CC BY 4.0).

Cleaning: the source wraps inline footnotes/citations as `¬ ... ¥`; for mobile
reading they become parenthesized text (content preserved, only typography
adapted). CRLF -> LF.

Outputs:
  surah/goals.json  { "<surahNo>": goal }  — one-line maqsad per surah (~6KB,
                    fetched once by the app)
  surah/<n>.json    { no, goal, names, fadael, nuzool } — full sections,
                    fetched lazily per surah (~20KB avg)
"""

import json
import os
import re
import sqlite3

DB = os.path.expanduser("~/.cache/tafsir-mcp/quran.db")
OUT = os.path.join(os.path.dirname(__file__), "..", "surah")


def clean(text: str | None) -> str:
    if not text:
        return ""
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    t = t.replace("¬", " (").replace("¥", ") ")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r" ?\n ?", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def main() -> None:
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT surahNo, surahGoals, surahNameInfo, surahFadael, surahNujoolInfo"
        " FROM surah_content ORDER BY surahNo"
    ).fetchall()
    assert len(rows) == 114, f"expected 114 surahs, got {len(rows)}"

    os.makedirs(OUT, exist_ok=True)
    goals = {}
    for no, goal, names, fadael, nuzool in rows:
        goals[str(no)] = clean(goal)
        with open(os.path.join(OUT, f"{no}.json"), "w", encoding="utf-8") as f:
            json.dump(
                {
                    "no": no,
                    "goal": clean(goal),
                    "names": clean(names),
                    "fadael": clean(fadael),
                    "nuzool": clean(nuzool),
                },
                f,
                ensure_ascii=False,
                separators=(",", ":"),
            )

    with open(os.path.join(OUT, "goals.json"), "w", encoding="utf-8") as f:
        json.dump(goals, f, ensure_ascii=False, separators=(",", ":"))

    empty_goals = [n for n, g in goals.items() if not g]
    print(f"surahs: {len(rows)}  empty goals: {empty_goals}")
    print(f"goals.json: {os.path.getsize(os.path.join(OUT, 'goals.json')):,} bytes")


if __name__ == "__main__":
    main()
