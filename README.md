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

## Source & License

The scholarly study content (i'rab, qiraat, asbab al-nuzul, word meanings, tajweed)
is derived from the **Tafsir Center for Quranic Studies** dataset
([tafsir.net](https://tafsir.net)), licensed **CC BY 4.0**
(<https://creativecommons.org/licenses/by/4.0/>) — free to use and redistribute
with attribution. This repository redistributes that data under the same license.
