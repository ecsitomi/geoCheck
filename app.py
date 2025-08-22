import streamlit as st
import json
import os
from main import analyze_urls_enhanced, GEOAnalyzer
from report import generate_html_report, generate_csv_export
from advanced_reporting import AdvancedReportGenerator  
import time
from config import GOOGLE_API_KEY, OPENAI_API_KEY

st.set_page_config(
    page_title="GEOcheck",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 GEOcheck")
st.markdown("**Generative Engine Optimization** website elemző rendszer AI & ML támogatással")

# Sidebar beállítások
st.sidebar.header("⚙️ Beállítások")

api_key = GOOGLE_API_KEY

use_ai_evaluation = st.sidebar.checkbox(
    "AI tartalom értékelés",
    value=True,
    help="AI-alapú tartalom minőség értékelés bekapcsolása"
)

use_cache = st.sidebar.checkbox(
    "Intelligens cache",
    value=True,
    help="Eredmények cache-elése a gyorsabb feldolgozásért"
)

force_refresh = st.sidebar.checkbox(
    "Cache kihagyása",
    value=False,
    help="Minden URL újraelemzése cache mellőzésével"
)

skip_pagespeed = st.sidebar.checkbox(
    "PageSpeed átugrása", 
    value=not bool(api_key),
    help="Gyorsabb elemzés PageSpeed nélkül"
)

parallel_processing = st.sidebar.checkbox(
    "Párhuzamos feldolgozás", 
    value=True,
    help="Több URL egyidejű elemzése (gyorsabb)"
)

max_workers = st.sidebar.slider(
    "Párhuzamos szálak száma",
    min_value=1,
    max_value=5,
    value=2,
    help="Több szál = gyorsabb, de több terhelés"
)



# Cache státusz megjelenítése
if use_cache:
    st.sidebar.subheader("💾 Cache állapot")
    if st.sidebar.button("Cache statisztikák"):
        try:
            analyzer = GEOAnalyzer(use_cache=True)
            cache_stats = analyzer.get_cache_stats()
            if cache_stats.get('cache_enabled'):
                st.sidebar.success(f"Cache fájlok: {cache_stats.get('total_files', 0)}")
                st.sidebar.info(f"Méret: {cache_stats.get('total_size_mb', 0)} MB")
            else:
                st.sidebar.warning("Cache nem elérhető")
        except Exception as e:
            st.sidebar.error(f"Cache hiba: {e}")
    
    if st.sidebar.button("Cache tisztítás"):
        try:
            analyzer = GEOAnalyzer(use_cache=True)
            clear_result = analyzer.clear_all_cache()
            if clear_result.get('status') == 'success':
                st.sidebar.success(f"✅ {clear_result.get('message', 'Cache törölve')}")
            else:
                st.sidebar.error(f"❌ {clear_result.get('message', 'Ismeretlen hiba')}")
        except Exception as e:
            st.sidebar.error(f"Tisztítás hiba: {e}")

# Főoldal
col1, col2 = st.columns([3, 2])

with col1:
    st.header("📝 URL-ek megadása")
    
    # URL input módok
    input_method = st.radio(
        "Bevitel módja:",
        ["Szöveges lista", "Fájl feltöltés"]
    )
    
    if input_method == "Szöveges lista":
        urls_text = st.text_area(
            "URL-ek (soronként egy URL):",
            height=200,
            placeholder="https://example.com\nhttps://another-site.com\nhttps://third-site.com"
        )
        url_list = [url.strip() for url in urls_text.split('\n') if url.strip()]
    
    else:
        uploaded_file = st.file_uploader(
            "URL lista feltöltése",
            type=['txt', 'csv'],
            help="Soronként egy URL a fájlban"
        )
        
        url_list = []
        if uploaded_file:
            content = str(uploaded_file.read(), "utf-8")
            url_list = [url.strip() for url in content.split('\n') if url.strip()]

with col2:
    st.header("📊 Elemzés indítása")
    st.markdown("""
     
    """)
    if st.button("▶️ GEO Elemzés kezdése", type="primary"):
        if not url_list:
            st.error("❌ Nem adtál meg URL-eket!")
        else:
            # Progress bar és status
            progress_bar = st.progress(0)
            status_text = st.empty()
            try:
                # Időmérés kezdése
                start_time = time.time()
                
                status_text.text("🚀 Enhanced elemzés inicializálása...")
                progress_bar.progress(10)
                
                # Fájlnév generálás timestamp-pel
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                json_filename = f"geo_enhanced_analysis_{timestamp}.json"
                html_filename = f"geo_enhanced_report_{timestamp}.html"
                
                status_text.text("🧠 GEO elemzése folyamatban...")
                progress_bar.progress(20)
                
                # Enhanced elemzés futtatása
                analyze_urls_enhanced(
                    url_list=url_list,
                    api_key=api_key if not skip_pagespeed else None,
                    output_file=json_filename,
                    parallel=parallel_processing,
                    skip_pagespeed=skip_pagespeed,
                    max_workers=max_workers if parallel_processing else 1,
                    use_cache=use_cache,
                    use_ai=use_ai_evaluation,
                    force_refresh=force_refresh
                )
                
                progress_bar.progress(70)
                status_text.text("📋 AI jelentés lekérése...")
                
                # HTML jelentés
                generate_html_report(json_filename, html_filename)
                
                progress_bar.progress(90)
                status_text.text("📊 CSV export...")
                
                # CSV export
                csv_filename = f"geo_enhanced_export_{timestamp}.csv"
                generate_csv_export(json_filename, csv_filename)
                
                progress_bar.progress(100)
                
                # Sikeres befejezés
                elapsed_time = time.time() - start_time
                status_text.text(f"✅ GEO elemzés befejezve! ({elapsed_time:.1f} másodperc)")
                
                # Download gombok
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    with open(json_filename, 'rb') as f:
                        st.download_button(
                            "📄 JSON jelentés letöltése",
                            f,
                            file_name=json_filename,
                            mime="application/json"
                        )
                
                with col2:
                    with open(html_filename, 'rb') as f:
                        st.download_button(
                            "📊 HTML jelentés letöltése",
                            f,
                            type="primary",
                            file_name=html_filename,
                            mime="text/html"
                        )
                
                with col3:
                    with open(csv_filename, 'rb') as f:
                        st.download_button(
                            "📈 CSV jelentés letöltése",
                            f,
                            file_name=csv_filename,
                            mime="text/csv"
                        )
            
            except Exception as e:
                st.error(f"❌ Hiba történt az enhanced elemzés során: {str(e)}")
                status_text.text("❌ Enhanced elemzés megszakítva")
                import traceback
                st.code(traceback.format_exc())

col1, col2 = st.columns([1, 1])

with col1:
# Információs szekció
    with st.expander("🚀 GEOcheck - Teljes funkcionalitás ℹ️"):
        st.markdown("""
                    
        #### 🎯 GEO (Generative Engine Optimization) Definíció:
        
        A **Generative Engine Optimization** az AI-alapú keresőmotorok és chatbotok (ChatGPT, Claude, Gemini, Bing Chat) számára való tartalom optimalizálás. Célja hogy a tartalom megjelenjen AI válaszokban és hivatkozásként szolgáljon.
        
        **🚀 Valós AI Integráció (OpenAI GPT-4o-mini):**
        - **AI Content Evaluation**: Valós OpenAI API-val tartalom minőség értékelés
        - **AI Readability Score**: Clarity, Engagement, Structure, AI Friendliness metrikák
        - **AI Factual Check**: Faktualitás, hivatkozások, citations, confidence elemzés
        - **Platform-specific AI Evaluation**: ChatGPT, Claude, Gemini, Bing Chat optimalizálás
        - **Semantic Relevance**: Kulcsszavak szemantikai relevancia mérése
        - **Fallback Heuristics**: Ha API nem elérhető, intelligens fallback algoritmusok
        
        **🧠 Machine Learning Motor (Scikit-learn):**
        - **Random Forest & Gradient Boosting**: Platform kompatibilitás előrejelzés
        - **Feature Engineering**: 20+ szöveges jellemző automatikus kinyerése
        - **Hybrid Scoring**: (Hagyományos + ML + AI) súlyozott kombinációja
        - **Confidence Levels**: ML bizonyossági szintek (High/Medium/Low)
        - **Feature Importance**: Mely tényezők a legfontosabbak platformonként
        - **Model Persistence**: Betanított modellek mentése és betöltése
        
        **🏗️ Enhanced Schema Validation:**
        - **Google Rich Results Test**: Valós Google validátor szimuláció
        - **Schema.org Compliance**: 50+ schema típus teljes validációja
        - **Rich Results Eligibility**: FAQ, Article, Product, HowTo támogatás
        - **Schema Effectiveness**: CTR impact és AI understanding mérés
        - **Dynamic Recommendations**: Automatikus schema javaslatok
        - **JSON-LD, Microdata, RDFa**: Minden formátum támogatása
        
        **💾 Intelligens Cache Rendszer:**
        - **File-based Caching**: Redis-mentes, egyszerű deployment
        - **TTL Management**: Automatikus cache lejárat kezelés (1 óra)
        - **Versioning**: Cache verziókezelés kompatibilitáshoz
        - **Cache Statistics**: Teljesítmény és találati arány mérés
        - **Intelligent Invalidation**: Automatikus cache törlés lejáratkor
        - **Force Refresh**: Manual cache bypass lehetőség
        
        **📊 Fejlett Tartalom Elemzés:**
        - **Content Quality Analyzer**: Olvashatóság, kulcsszó sűrűség, szemantikai gazdagság
        - **AI-Specific Metrics**: 8 AI-readiness metrika (structure, qa_format, entities, stb.)
        - **Authority Signals**: Szerző info, publikálási dátum, szakmai terminológia
        - **Semantic Richness**: Entitások, domain expertise, kapcsolatok
        - **Readability Scores**: Flesch score, mondathossz, szókincs gazdagság
        
        **🎯 Multi-Platform Optimization:**
        - **ChatGPT Optimizer**: Lépésenkénti útmutatók, listák, gyakorlati tartalom
        - **Claude Optimizer**: Részletes kontextus, hivatkozások, árnyalt magyarázatok  
        - **Gemini Optimizer**: Friss információk, multimédia, strukturált adatok
        - **Bing Chat Optimizer**: Források, külső hivatkozások, időszerű tartalom
        - **Platform Scoring**: Hagyományos + ML + AI triple hybrid rendszer
        
        **🔧 Auto-Fix Generator:**
        - **Meta Tag Templates**: Title, description, keywords optimalizálás
        - **Schema Templates**: Organization, Article, FAQ, Product automatikus generálás
        - **Platform-specific Fixes**: Egyedi javítási javaslatok platformonként
        - **Priority Scoring**: Javítások fontossági sorrendben
        - **Code Generation**: Kész HTML/JSON-LD kód generálás
        
        **⚡ PageSpeed Insights Integráció (Google API):**
        - **Mobile & Desktop Teljesítmény**: Valós Google PageSpeed API mérések
        - **Core Web Vitals**: LCP, FID, CLS metrikák részletes elemzése
        - **Performance Scoring**: 0-100 pontszám mobil és desktop verzióra
        - **SEO Technical Score**: Technikai SEO tényezők Google értékelése
        - **Visual Indicators**: Színkódolt eredmények (jó/javítandó/gyenge)
        - **Performance Impact**: Teljesítmény hatása AI platform rangsorolásra
        - **Optimization Tips**: Automatikus teljesítmény javítási javaslatok
        
        **📈 Advanced Reporting:**
        - **Executive Summary**: C-level döntéshozói összefoglaló
        - **Technical Audit**: Fejlesztői részletes technikai jelentés
        - **Competitor Analysis**: Versenytárselemzés és összehasonlítás
        - **Action Plan**: Konkrét lépésenkénti cselekvési terv
        - **Progress Tracking**: Fejlődés követése időben
        - **Multi-format Export**: HTML, JSON, CSV jelentések
        
        
        ### ⚙️ Technikai Architektúra:
        
        **Moduláris Felépítés:**
        - `main.py`: Core analyzer, threading, cache integration
        - `ai_evaluator.py`: OpenAI API integration, AI scoring
        - `platform_optimizer.py`: ML models, platform-specific algorithms  
        - `schema_validator.py`: Schema.org validation, Google Rich Results
        - `content_analyzer.py`: Text analysis, quality metrics
        - `cache_manager.py`: File-based caching system
        - `auto_fixes.py`: Fix generation, code templates
        - `advanced_reporting.py`: Multi-format report generation
        - `ai_metrics.py`: AI-readiness specific metrics
        
        """)
with col2:
    # ML szerepe és működése
    with st.expander("🧠 Machine Learning a GEO Check alkalmazásban ℹ️"):
        st.markdown("""

        #### **1. 📊 Platform Kompatibilitás Előrejelzés**
        Az ML modell **platform-specifikus pontszámokat** jósol meg:
        - **ChatGPT, Claude, Gemini, Bing Chat** kompatibilitási pontszámok
        - A hagyományos algoritmus mellett **második vélemény** nyújtása
        - **Hybrid Score** = (Hagyományos + ML) / 2

        #### **2. 🎯 Miből tanul az ML?**
        Az ML modell **szöveg jellemzőket** elemez:
        - **Szöveg hossza** és struktúrája
        - **Bekezdések száma** és eloszlása
        - **Listák, táblázatok** megléte
        - **Címsorok hierarchiája** (H1-H6)
        - **Kulcsszavak gyakorisága**
        - **Mondathossz átlagok**
        - **Szakmai terminológia** sűrűsége

        #### **3. 🔮 Hogyan működik?**
        1. **Betanítás**: Sok weboldalon **"kézi értékelések"** alapján tanul
        2. **Feature extraction**: A szövegből **számszerű jellemzőket** von ki
        3. **Predikció**: Új oldalakra **pontszámot jósol** (0-100)
        4. **Validáció**: **Confidence level** - mennyire biztos az eredményben

        #### **4. 📈 Pontszám kombináció:**
        ```
        Hybrid Score = (Hagyományos algoritmus + ML jóslat) / 2
        ```

        **Példa**:
        - Hagyományos ChatGPT score: 40
        - ML ChatGPT score: 60  
        - **Hybrid score: 50**

        #### **5. 🎨 ML Confidence (biztonság):**
        - **High**: <10 pont különbség (ML és hagyományos között)
        - **Medium**: 10-20 pont különbség
        - **Low**: >20 pont különbség

        #### **6. 🔍 Feature Importance:**
        Az ML **megmondja** hogy melyik jellemző **mennyire fontos** az egyes platformoknak:
        - **ChatGPT**: listák, lépések fontosak
        - **Claude**: hosszú szöveg, hivatkozások
        - **Gemini**: frissesség, strukturáltság
        - **Bing**: források, külső linkek

        #### **7. 🚀 Miért hasznos ez?**
        - **Objektívebb értékelés**: Nem csak szabály-alapú
        - **Mintázat felismerés**: Rejtett összefüggéseket talál
        - **Adaptivitás**: Idővel "tanul" és javul
        - **Komplexitás kezelés**: Sok tényezőt egyszerre mérlegel

        #### **8. 💡 Gyakorlati haszon:**
        Az ML **finomítja** a hagyományos algoritmust - ha például egy oldal **szabály szerint** jó pontot kapna, de az **ML alacsony pontot** jósol, akkor valószínűleg **valami rejtett probléma** van amit érdemes megvizsgálni!

        Ez teszi a rendszert **intelligensebbé** és **pontosabbá** a platform optimalizálásban! 🎯
        """)

# Footer
st.markdown("---")
st.markdown("🚀 **GEOcheck** | AI & ML támogatott generativ engine optimalizált website ellenőrző rendszer | Fejlesztette: Ecsedi Tamás | 2025")