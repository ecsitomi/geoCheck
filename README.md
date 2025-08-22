# geoCheck — Generative Engine Optimization (GEO) Checker

**Röviden:** a geoCheck egy elemző eszköz, amely egy megadott webcikket / tartalmat feldolgoz és **LLM‑ek, kereső‑asszisztensek és RAG rendszerek** szempontjából kiértékeli. Célja, hogy

* mennyire **könnyen emészthető** a szöveg a modellek számára,
* mennyire **szabványos és gépileg olvasható** (metaadatok, schema, szekcionálás),
* mennyire **idézhető és megbízható** (források, dátumok),
* és milyen **automatizálható javításokat** érdemes elvégezni.

> **Megjegyzés:** A dokumentáció a projektfájlok ( `app.py`, `main.py`, `ai_metrics.py`, `content_analyzer.py`, `platform_optimizer.py`, `auto_fixes.py`, `report.py`, `advanced_reporting.py`, `requirements.txt` ) alapján épül fel. A függvénynevek példák – a modulok felelősségét és a mért eredmények értelmét írjuk le részletesen.

---

## Fő funkciók

* **URL / nyers szöveg feldolgozása** és tartalomkinyerés
* **Tokenizálás és szövegszerkezet-elemzés** (címek hierarchiája, bekezdéshossz, felsorolások, táblázatok)
* **Olvashatóság és komplexitás** (Flesch‑szerű mutatók, mondathossz, szakzsargon arány)
* **GEO‑metrikák** (pl. Embeddability, Schema Coverage, Headings Coverage, Citations, Q\&A jelenlét, Duplicate ratio, Chunk-fit)
* **Platform‑specifikus ellenőrzések** (OpenGraph/Twitter meta, JSON‑LD/Schema.org, robots, sitemap)
* **Automatikus javítási javaslatok** (konkrét, bemásolható patchek / sablonok)
* **Jelentésgenerálás** (Markdown/HTML/CSV/JSON), „GEO Score” és részpontszámok
* **CLI és (opcionális) UI** futtatás

---

## Telepítés

### Követelmények

* **Python 3.10+** (ajánlott)
* `pip` és a projekt gyökérben található `requirements.txt` csomagjai
* **API kulcsok beállítása** (opcionális, de ajánlott):
  * `GOOGLE_API_KEY` - PageSpeed Insights API-hoz
  * `OPENAI_API_KEY` - AI tartalom értékeléshez

### API kulcsok konfigurálása

A rendszer két módon kezeli az API kulcsokat **prioritási sorrendben**:

1. **`.env` fájl** (elsődleges):
```bash
# .env fájl a projekt gyökérben
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

2. **Streamlit Secrets** (fallback):
```toml
# .streamlit/secrets.toml fájl
GOOGLE_API_KEY = "your_google_api_key_here"
OPENAI_API_KEY = "your_openai_api_key_here"
```

**Jegyzet**: Ha nincs beállítva API kulcs, az alkalmazás fallback algoritmusokkal működik csökkentett funkcionalitással.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Futtatás

**CLI:**

```bash
python main.py --url "https://pelda.hu/cikk" --out reports/
# vagy
python main.py --text-file input.txt --model gpt-4o-mini --format md
```

**Streamlit Web Interface:**

```bash
# Streamlit alkalmazás indítása
streamlit run app.py
```

A web interface automatikusan felismeri az API kulcsok jelenlétét és a konfigurációs státuszt megjeleníti az oldalsávban.

**CLI használat:**

```bash
python main.py --url "https://pelda.hu/cikk" --out reports/
# vagy
python main.py --text-file input.txt --model gpt-4o-mini --format md
```

Argumentumok (tipikus):

* `--url` vagy `--text-file` – bemeneti forrás
* `--model` – modellnév (ha releváns)
* `--out` – kimeneti mappa
* `--format` – `md` | `html` | `json` | `csv`
* `--platform` – célplatform‑checks: `openai, google, perplexity, x` (vagy `all`)

---

## Kimenetek és pontszámok értelmezése

### Összesített GEO Score (0–100)

A fő mutató; súlyozott átlag az alábbi részeredményekből. Ajánlott skála:

* **90–100**: kiváló – asszisztens‑barát, szabványos, bőven hivatkozott
* **75–89**: jó – néhány finomhangolással optimális
* **60–74**: közepes – több szerkezeti/metaadat javítás indokolt
* **0–59**: gyenge – jelentős átalakítás szükséges

### Részpontszámok

1. **Content Clarity (0–100)**
   *Mit méri:* mondathossz-medián, Flesch‑szerű olvashatóság, redundancia, „filler” arány.
   *Mi számít jónak:* 14–22 szó/mondatátlag, rövid bekezdések, aktív igealakok, világos definíciók.

2. **Structure & Chunking (0–100)**
   *Mit méri:* H1–H3 lefedettség, szekciók azonosítói (ankorok), felsorolások/táblák aránya, **Chunk‑fit** (egy szakasz belefér‑e tipikus kontextusablakba).
   *Jó érték:* minden szakasz ≤ 600–800 token, egyértelmű címkék, kevés „árva” mondat.

3. **Machine‑Readability (0–100)**
   *Mit méri:* cím/description meta, **OpenGraph**, **Twitter**, **schema.org JSON‑LD** típusok (Article, FAQPage, HowTo), `robots.txt`, `sitemap.xml`, `hreflang`.
   *Jó érték:* teljes meta‑készlet, 1–2 JSON‑LD blokk, konzisztensek a látható tartalommal.

4. **Evidence & Citations (0–100)**
   *Mit méri:* linkelt források száma/minősége, dátumok jelenléte, számszerű állítások egységekkel, táblázatos adatok.
   *Jó érték:* minden fontos állításnak van hivatkozása; friss (≤12 hónap) dátumok.

5. **Q\&A / FAQ & Task‑orientation (0–100)**
   *Mit méri:* kérdés‑válasz blokkok, lépésről‑lépésre **HowTo**, definíció‑szótár.
   *Jó érték:* 3–10 releváns Q\&A, rövid válaszok, HowTo lépések számozva.

6. **Duplication & Canonical (0–100)**
   *Mit méri:* duplikált bekezdések, kanonikus URL jelenléte, címke‑inkonzisztenciák.
   *Jó érték:* nincs duplikátum, `link rel="canonical"` beállítva.

> **„Chunk‑fit”**: a szekciók token‑becslését hasonlítja az általad célzott modellek kontextusablakához (pl. 8k / 32k). Ha egy fejezet > kontextus 70–80%-a, bontás javasolt.

---

## Modulok és (tipikus) felelősségük

### `content_analyzer.py`

**Feladat:** nyers HTML/Markdown → tiszta, strukturált szöveg + szerkezeti jelölők.

Lehetséges fő függvények / osztályok:

* `extract_from_url(url) → Content` – HTML letöltés, `<main>`/`<article>` preferencia, boilerplate szűrés
* `extract_from_markdown(md_str) → Content`
* `segment(content) → list[Section]` – címsorok alapján szekcionálás, táblázatok és kódrészletek megőrzése
* `estimate_tokens(text, model) → int` – tiktoken/szabályalapú becslés
* `readability_metrics(text) → dict` – átlagos mondathossz, Flesch‑mutatók, passzív szerkezet arány

**Kimenet (példa `Content`):**

```json
{
  "url": "https://pelda.hu/cikk",
  "title": "Példa cikk",
  "sections": [
    {"id": "bevezetes", "h": 2, "text": "...", "tokens": 312},
    {"id": "eredmenyek", "h": 2, "text": "...", "tokens": 541}
  ],
  "meta": {"og": {...}, "twitter": {...}, "json_ld": [...], "canonical": "..."}
}
```

### `ai_metrics.py`

**Feladat:** GEO‑specifikus metrikák kiszámítása a `Content` alapján.

Kulcsmetrikák (tipikus):

* **EmbeddabilityScore** – szekciók átlagos hossza, szerkezet, listák/definíciók jelenléte
* **SchemaCoverage** – JSON‑LD típusok és kulcsmezők aránya
* **HeadingsCoverage** – H‑hierarchia, elnevezett horgonyok
* **CitationScore** – hivatkozások és dátumok sűrűsége
* **QA/HowToScore** – Q\&A/HowTo blokkok felismerése
* **DuplicationScore** – ismétlődő bekezdések aránya
* **ChunkFitScore(model\_ctx)** – token‑becslés vs. kontextus

Tipikus API:

```python
scores = compute_all_metrics(content, target_models=["gpt-4o", "sonnet-3.5"])
# {"geo": 82.4, "clarity": 78, "structure": 85, ...}
```

### `platform_optimizer.py`

**Feladat:** platform‑specifikus megfelelőség ellenőrzése és ajánlások.

Példák:

* **OpenGraph/Twitter** – `og:title`, `og:description`, `og:url`, `twitter:card` …
* **Schema.org** – `Article`, `BlogPosting`, `FAQPage`, `HowTo` minimál mezők
* **Robots & Sitemap** – alap tiltások, `sitemap.xml` elérhetőség, `hreflang`
* **Canonical & Duplicates** – kanonikus címke és tartalom‑duplikáció

Kimenet: „pass/warn/fail” tételes lista + rövid indoklás.

### `auto_fixes.py`

**Feladat:** célzott, bemásolható javítási javaslatok generálása.

Példák:

* **Tartalmi szétbontás** – túl hosszú szekciók darabolása H3‑akra
* **FAQ generálás** – 5–8 reprezentatív kérdés‑válasz blokk
* **Schema sablonok** – `FAQPage`, `HowTo`, `Article` JSON‑LD minták
* **Meta sablonok** – `<title>`, `meta description`, OpenGraph/Twitter
* **Források** – hiányzó állításokhoz forrástípus‑lista (tanulmány, hivatalos stat, dokumentáció)

Kimenet: `Fix` objektumok listája (`title`, `why`, `how`, `snippet`).

### `report.py` és `advanced_reporting.py`

**Feladat:** emberi olvasásra optimalizált jelentés és gép‑barát exportok.

* **`report.py`** – Markdown/HTML áttekintés, „trafiklámpás” (✅/⚠️/❌) státuszok, táblázatok
* **`advanced_reporting.py`** – CSV/JSON összesítők több futásról (trendek), modell‑összehasonlítás

Példa kimenet (MD):

```md
# GEO Score: 82/100
- Clarity: 78  
- Structure & Chunking: 85  
- Machine‑Readability: 80  
- Evidence & Citations: 72  
- Q&A/HowTo: 92

Top 5 teendő: 1) Canonical beállítás, 2) 3 hosszú szekció bontása, 3) FAQ JSON‑LD, 4) 6 állítás forrásolása, 5) 2 hiányzó OG meta.
```

### `app.py`

**Feladat:** egyszerű UI / szerver (pl. Streamlit / Flask) a fenti komponensekhez.

Tipikus folyam:

1. Bemenet (URL / szöveg) → 2. Elemzés (`content_analyzer`) → 3. Metrikák (`ai_metrics`) → 4. Platform‑checks → 5. Javítások → 6. Jelentés

### `main.py`

**Feladat:** CLI belépési pont, argumentumkezelés, futtatási sorrend, hibakezelés.

---

## Példa riport‑mezők magyarázata

| Mező                          | Jelentés                                       | Mi számít jónak         |
| ----------------------------- | ---------------------------------------------- | ----------------------- |
| `geo_score`                   | Összesített pont a súlyozott részpontszámokból | ≥ 85                    |
| `clarity.readability`         | Flesch‑szerű olvashatóság                      | 60–80                   |
| `clarity.avg_sentence_len`    | Átlagos szavak/mondatátlag                    | 14–22                   |
| `structure.headings_coverage` | H1–H3 lefedettség                              | ≥ 0.8                   |
| `structure.chunk_fit_8k`      | 8k kontextus‑kompatibilis szekciók aránya      | ≥ 0.9                   |
| `machine.jsonld_types`        | JSON‑LD típusok száma/használata               | ≥ 1 (Article/FAQ/HowTo) |
| `machine.opengraph_ok`        | OG/Twitter meta teljesség                      | ✅                       |
| `evidence.citation_density`   | Hivatkozássűrűség                              | ≥ 1/300–500 szó         |
| `qa.count`                    | FAQ/QA párok száma                             | 5–10                    |
| `dup.duplicate_ratio`         | Duplikáció aránya                              | ≤ 5%                    |
