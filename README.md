# taqwa-data

Static JSON data assets for the **Taqwa** Islamic companion app, served via [jsDelivr](https://www.jsdelivr.com/) and downloaded on demand by the app to keep the installed binary small.

## Contents

`study/` — per-ayah Quranic study data, keyed by `"surah:ayah"`:

| File | Description |
| --- | --- |
| `asbab.json` | أسباب النزول — occasions of revelation |
| `irab.json` | الإعراب — full-verse grammatical analysis |
| `tajweed.json` | التجويد — recitation (tajweed) notes |
| `qeraat.json` | القراءات — per-word variant readings |
| `words.json` | معاني الكلمات — per-word meanings |

`roots/` — Quranic word-root datasets (added in `v2`, for the Deep Study root explorer):

| File | Description |
| --- | --- |
| `index.json` | `root → { id, c, s, a, t }` — occurrence count, surah count, ayah count, top-3 surahs; plus attribution meta. 1,825 roots. |
| `word-root.json` | `"surah:ayah" → [root per word]` — array index = `wordNo - 1` (same 1-based word numbering as `study/words.json`; the single irregular ayah 2:1 is `""`-padded). Compound words keep the slash-joined source form (e.g. `مِن/ما`) — split on `/` for display. |
| `occ/<id>.json` | `{ r: root, o: [[surah, ayah, wordNo], …] }` — per-root occurrence list, fetched lazily by `id` from `index.json`. |

Counts in `index.json` are computed from the occurrence lists themselves (so a
displayed count always equals the list length) and validated 1:1 against the
source dataset's own statistics. Regenerate with `scripts/export_roots_v2.py`
(reads the [tafsir-mcp](https://pypi.org/project/tafsir-mcp/) SQLite database).

## Source & License

The scholarly study content (i'rab, qiraat, asbab al-nuzul, word meanings, tajweed,
word roots and their statistics)
is derived from the **Tafsir Center for Quranic Studies** dataset
([tafsir.net](https://tafsir.net)), licensed **CC BY 4.0**
(<https://creativecommons.org/licenses/by/4.0/>) — free to use and redistribute
with attribution. This repository redistributes that data under the same license.
