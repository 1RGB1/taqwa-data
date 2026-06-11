#!/usr/bin/env python3
"""
One-off export: tafsir-mcp SQLite DB -> taqwa-data@v2 root datasets.

Source: ~/.cache/tafsir-mcp/quran.db, table `word_statistics` (Tafsir Center
for Quranic Studies dataset, CC BY 4.0). Word numbering (`wordNo`, 1-based)
is verified identical to study/words.json across all 6,236 ayahs, so the
app's existing word chips index straight into these maps.

Outputs (under roots/):
  index.json      root -> { id, c (occurrences), s (surahs), a (ayahs),
                            t (top-3 surahs by count) }  + attribution meta
  word-root.json  "surah:ayah" -> [root per word, in wordNo order]
  occ/<id>.json   { r: root, o: [[surah, ayah, wordNo], ...] }  (lazy-fetch)
"""

import json
import os
import sqlite3
from collections import Counter, defaultdict

DB = os.path.expanduser("~/.cache/tafsir-mcp/quran.db")
OUT = os.path.join(os.path.dirname(__file__), "..", "roots")

ATTRIBUTION = {
    "ar": "المحتوى العلمي (جذور الكلمات وإحصاءاتها) مصدره بيانات مركز تفسير للدراسات القرآنية (tafsir.net) — رخصة CC BY 4.0.",
    "en": "Scholarly content (word roots and statistics) is from the Tafsir Center for Quranic Studies (tafsir.net) dataset — licensed CC BY 4.0.",
    "license": "CC BY 4.0",
    "source": "https://tafsir.net",
}

def main() -> None:
    con = sqlite3.connect(DB)
    cur = con.cursor()
    rows = cur.execute(
        "SELECT surahNo, ayahNo, wordNo, root, rootRepeatitionCount,"
        " surahCountWithRoot, ayahCountWithRoot"
        " FROM word_statistics ORDER BY surahNo, ayahNo, wordNo"
    ).fetchall()

    word_root: dict[str, list[str]] = defaultdict(list)
    occurrences: dict[str, list[list[int]]] = defaultdict(list)
    stored_count: dict[str, int] = {}
    per_surah: dict[str, Counter] = defaultdict(Counter)
    ayah_sets: dict[str, set] = defaultdict(set)

    for s, a, w, root, c, sc, ac in rows:
        key = f"{s}:{a}"
        words = word_root[key]
        # wordNo is 1-based and contiguous everywhere EXCEPT 2:1, where the
        # source counts the basmala as words 1-4 (the app's words.json carries
        # the same numbering). Pad with "" so arr[wordNo-1] always works.
        while len(words) < w - 1:
            words.append("")
        assert len(words) == w - 1, f"word order broken at {key}:{w}"
        # Compound words (وممّا = مِن+ما) carry "مِن/ما" — keep the raw string
        # here (the app splits on "/" for display)…
        words.append(root)
        # …but in the index each COMPONENT root gets credited.
        for comp in root.split("/"):
            occurrences[comp].append([s, a, w])
            per_surah[comp][s] += 1
            ayah_sets[comp].add((s, a))
        # Stored per-root count is only a clean int on non-compound rows;
        # remember it for validation against our own aggregation.
        if "/" not in root:
            try:
                stored_count[root] = int(c)
            except (TypeError, ValueError):
                pass

    # All stats computed from our own aggregation so `c` ALWAYS equals the
    # occurrence-list length (the SPEC acceptance for the explorer UI).
    # Stable ids: occurrence count desc, then root text — deterministic rerun.
    ordered = sorted(occurrences.keys(), key=lambda r: (-len(occurrences[r]), r))
    index = {}
    validated = mismatched = 0
    for i, root in enumerate(ordered):
        occ = occurrences[root]
        top = [sn for sn, _ in per_surah[root].most_common(3)]
        index[root] = {
            "id": i,
            "c": len(occ),
            "s": len(per_surah[root]),
            "a": len(ayah_sets[root]),
            "t": top,
        }
        if root in stored_count:
            validated += 1
            if stored_count[root] != len(occ):
                mismatched += 1
                if mismatched <= 8:
                    print(f"  stat note {root}: stored {stored_count[root]} vs computed {len(occ)}")
    print(f"validated {validated} roots against stored counts; {mismatched} differ")

    os.makedirs(os.path.join(OUT, "occ"), exist_ok=True)

    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as f:
        json.dump(
            {
                "version": 2,
                "generated": "2026-06-11",
                "attribution": ATTRIBUTION,
                "rootCount": len(index),
                "wordCount": len(rows),
                "roots": index,
            },
            f,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    with open(os.path.join(OUT, "word-root.json"), "w", encoding="utf-8") as f:
        json.dump(dict(word_root), f, ensure_ascii=False, separators=(",", ":"))

    for root, i in ((r, index[r]["id"]) for r in ordered):
        with open(os.path.join(OUT, "occ", f"{i}.json"), "w", encoding="utf-8") as f:
            json.dump(
                {"r": root, "o": occurrences[root]},
                f,
                ensure_ascii=False,
                separators=(",", ":"),
            )

    print(f"roots: {len(index)}  words: {len(rows)}  ayahs: {len(word_root)}")
    print(f"index.json: {os.path.getsize(os.path.join(OUT, 'index.json')):,} bytes")
    print(f"word-root.json: {os.path.getsize(os.path.join(OUT, 'word-root.json')):,} bytes")


if __name__ == "__main__":
    main()
