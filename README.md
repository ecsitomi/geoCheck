# GEOcheck – Website GEO (Generative Engine Optimization) Audit  


## Tartalomjegyzék

1. [Mi az a GEO és miért fontos?](#mi-az-a-geo-és-miért-fontos)  
2. [Fő funkciók áttekintése](#fő-funkciók-áttekintése)  
3. [Rendszer-architektúra (modulok és felelősségek)](#rendszer-architektúra-modulok-és-felelősségek)  
4. [Telepítés és futtatás](#telepítés-és-futtatás)  
5. [Használat lépésről lépésre](#használat-lépésről-lépésre)  
6. [Pontozás és módszertan (hogyan számolunk?)](#pontozás-és-módszertan-hogyan-számolunk)  
7. [Mutatók magyarázata + tooltip szövegek](#mutatók-magyarázata--tooltip-szövegek)  
8. [Hogyan érjünk el 100%-ot? — gyakorlati checklisták](#hogyan-érjünk-el-100--ot--gyakorlati-checklisták)  
9. [Riportok és export](#riportok-és-export)  
10. [Cache, teljesítmény és korlátok](#cache-teljesítmény-és-korlátok)  
11. [Biztonság, költségek és megfelelés](#biztonság-költségek-és-megfelelés)  
12. [Gyakori kérdések](#gyakori-kérdések)

---

## Mi az a GEO és miért fontos?

**GEO (Generative Engine Optimization)**: tartalom és technikai optimalizálás **AI-alapú keresők** és **generatív asszisztensek** (pl. ChatGPT, Claude, Gemini, Bing Copilot) számára.  
Míg az SEO a klasszikus találati oldalakat célozza, a GEO célja, hogy **a nagy nyelvi modellek könnyen értelmezhető, megbízható, jól hivatkozott és strukturált tartalmat találjanak az Ön oldalán**, és ebből minőségi válaszokat tudjanak adni a felhasználóknak.

**Üzleti érték:**  
- Több **AI-csatornából érkező forgalom** és márkaemlítés  
- **Magasabb konverzió**: a jobb strukturáltság és bizalomépítő elemek miatt  
- **Gyorsabb tartalomfejlesztés**: világos hiánylisták és automatikus javítási javaslatok
- **🆕 AI-vezérelt optimalizálás**: GPT-4 által készített személyre szabott fejlesztési tervek

---

## Fő funkciók áttekintése

- **Tömeges URL elemzés** (Streamlit UI)  
- **Technikai ellenőrzések:** robots.txt, sitemap, mobilbarát jelölések, H1 számlálás stb.  
- **Tartalom-minőség elemzés:** címsor-hierarchia, listák/táblázatok, Q&A-blokkok, frissesség, hivatkozások  
- **AI-alapú értékelés (OpenAI):** olvashatóság, faktualitás, AI-barátság  
- **Platform-kompatibilitás pontszámok:** ChatGPT / Claude / Gemini / Bing  
- **Schema.org validáció és „Rich Results” esély** (Google ellenőrzéssel, opcionálisan Selenium)  
- **Auto-fixes (javaslatmotor):** meta cím/description sablonok, schema ajánlások, tartalmi és technikai javítások, **priorizált feladatlista**  
- **Haladó riportok:** executive summary, technikai audit, website elemzés  
- **Exportok:** HTML és CSV riportok  
- **Cache és ismételhetőség:** 1 órás TTL, statisztika és „Cache tisztítás” gomb

---

## ✨ AI Összefoglaló és Javaslatok

**🧠 OpenAI GPT-4 Integráció**: Az elemzés eredményeit most az OpenAI GPT-4 is kiértékeli és praktikus összefoglalót készít!

### Új funkciók:
- **📝 AI Összefoglaló**: GPT-4 által készített intelligens összefoglaló az elemzési eredményekről
- **💡 AI Javaslatok**: Konkrét, végrehajtható fejlesztési javaslatok GEO optimalizáláshoz
- **🔄 Frissítés gomb**: Valós időben újragenerálható AI elemzés
- **🎯 Első helyen**: Az AI Összefoglaló tab lett az első a jelentésekben

---

## Rendszer-architektúra (modulok és felelősségek)

- `app.py` – **Streamlit UI**, beállítások (cache, enhanced mód), futtatás, állapotjelzés  
- `main.py` – **GEOAnalyzer** és URL-feldolgozás (robots.txt, HTTP letöltés, BeautifulSoup), pipeline-vezérlés  
- `content_analyzer.py` – **tartalom-minőség**: címsorok, szöveg, listák, táblázatok, olvashatóság, Q&A formátum  
- `ai_metrics.py` – **AI-specifikus metrikák**: enhanced struktúra, QA-score, entity/freshness/citation jelek, „AI-friendliness”  
- `ai_evaluator.py` – **OpenAI-alapú** olvashatóság- és faktualitás-értékelés + szemantikus relevancia (API kulccsal)  
- `platform_optimizer.py` – **MultiPlatformGEOAnalyzer**: jel-alapú és (ha elérhető) ML-súlyozás (sklearn), ChatGPT/Claude/Gemini/Bing pontok  
- `schema_validator.py` – **schema.org** típusok felismerése, teljesség/komplettség, Google validáció (rich results), opcionálisan Selenium  
- `auto_fixes.py` – **javítási javaslatok**: meta sablonok, schema-bővítés, tartalom-optimalizáció, technikai fixek, implementációs guide, priorizálás  
- `advanced_reporting.py` – **riport-összesítő**: score eloszlás, platform-teljesítmény, csatornánkénti hiányok és lehetőségek  
- `report.py` – **HTML/CSV** generálás + **tooltip szövegkészlet**  
- `cache_manager.py` – fájl-alapú cache (TTL: 1 óra), statisztika, tisztítás  
- `config.py` – API kulcsok betöltése: `.env` → környezeti változó → `st.secrets` fallback

---

## Telepítés és futtatás

### Követelmények
- **Python 3.10+**  
- Ajánlott: virtuális környezet

### Telepítés
```bash
pip install -U streamlit requests beautifulsoup4 python-dotenv openai
# Opcionális (platform score-hoz ML):
pip install -U scikit-learn numpy
# Opcionális (Google Rich Results ellenőrzéshez):
pip install -U selenium
```

### Környezeti változók
Hozz létre `.env` fájlt (vagy használd a Streamlit `secrets`-et):

```env
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...   # PageSpeed/egyéb Google végpontokhoz és validációkhoz
```

> A `config.py` először `.env`-ből olvas, majd env-ből, végül `st.secrets` fallback.

### Futtatás
```bash
streamlit run app.py
```

---

## Használat lépésről lépésre

1. **Indítsd az appot**, illeszd be az URL(eke)t (több sorban is lehet).  
2. Oldalt válaszd ki:  
   - **Use Cache** (gyorsabb ismétlések)  
   - **Enhanced / AI metrikák** (OpenAI kulccsal)  
   - **Schema Enhanced + Google validation** (opcionális Selenium)  
3. Kattints **„Elemzés”**.  
4. Nézd meg a **Topline pontszámokat**, platform-score-okat, technikai és tartalmi hibákat.  
5. Töltsd le a **HTML/CSV riportot**, vagy használd az **Auto-fixes** javaslatokat a javításhoz.

---

## Pontozás és módszertan (hogyan számolunk?)

A végső **AI Readiness Score (0–100)** három komponensből áll:

- **Hagyományos + Tartalmi jelek (kb. 40%)**  
  Címsorok, meta elemek, olvashatóság, listák/táblázatok, frissesség, hivatkozások stb.
- **ML/Heurisztikus jelek (kb. 40%)**  
  Több jel súlyozott kombinációja (Q&A-nyomok, entitások, strukturáltság, interaktív elemek stb.).  
  (Ha a `scikit-learn` elérhető, a súlyozás és validáció kifinomultabb.)
- **AI-értékelés (kb. 20%)**  
  OpenAI-alapú olvashatóság, faktualitás és AI-barátság értékelések.

**Platform pontok (ChatGPT / Claude / Gemini / Bing):**  
„Hybrid” módszerrel számítódnak (hagyományos + ML jelek kombinációja), **platform-specifikus preferenciákkal** (pl. Q&A és források → Bing, mély tartalom → Claude, frissesség & mobilbarát → Gemini, jól strukturált FAQ és lépéslista → ChatGPT).

> A `report.py` segítségével a pontok **tooltip** magyarázattal jelennek meg a felületen és az exportban is.

---

## 🆕 AI Összefoglaló és Javaslatok

### Konfiguráció

Az AI összefoglaló funkcióhoz szükséges az OpenAI API kulcs beállítása:

```bash
# .env fájlban vagy környezeti változóként
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### Funkciók

**📝 AI Összefoglaló**
- GPT-5 által készített intelligens kiértékelés
- Maximum 500 szavas összefoglaló az eredményekről
- Automatikus felismerés az AI-readiness szintről

**💡 AI Javaslatok**
- Maximum 600 szavas konkrét fejlesztési terv
- Végrehajtható lépések priorizált sorrendben
- GEO-specifikus optimalizálási tanácsok

**🔄 Interaktív frissítés**
- Frissítés gomb minden AI összefoglalónál
- Valós idejű regenerálás lehetősége
- Placeholder szöveg API kulcs nélkül

### Használat

1. **Automatikus**: A jelentésben az "🧠 AI Összefoglaló" tab az első
2. **Manuális**: A "🔄 Frissítés" gombbal újragenerálható
3. **Programozottan**: `ai_summary.py` modul közvetlen használata

```python
from ai_summary import generate_ai_summary_from_file

summary, recommendations = generate_ai_summary_from_file('results.json')
print(f"Összefoglaló: {summary}")
print(f"Javaslatok: {recommendations}")
```

