import streamlit as st
import json
import os
from main import analyze_urls_enhanced, GEOAnalyzer
from report import generate_html_report, generate_csv_export
from advanced_reporting import AdvancedReportGenerator  
import time
from config import GOOGLE_API_KEY, OPENAI_API_KEY
import pandas as pd

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

with st.expander("🎯 OKTATÓANYAG ℹ️"):
    # 1. BEVEZETÉS
    with st.expander("📚 **1. BEVEZETÉS - Mi az a GEO?**", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### Mi az a GEO?
            
            **Generative Engine Optimization (GEO)** = tartalom és technikai optimalizálás AI-alapú keresők és generatív asszisztensek számára.
            
            **Főbb platformok:**
            - 🤖 ChatGPT
            - 🧠 Claude (Anthropic)
            - ✨ Google Gemini
            - 🔍 Microsoft Copilot/Bing Chat
            - 🎯 Perplexity AI
            """)
        
        with col2:
            st.markdown("### SEO vs GEO - A paradigmaváltás")
            
            comparison_df = pd.DataFrame({
                'SEO (hagyományos)': [
                    'Kulcsszó-optimalizálás',
                    'Linképítés',
                    'Meta tagek',
                    'Ranking pozíció',
                    'CTR optimalizálás',
                    '10 kék link'
                ],
                'GEO (új világ)': [
                    'Szemantikus megértés',
                    'Forrás-hitelesség',
                    'Strukturált adatok',
                    'AI válaszokban megjelenés',
                    'Idézhetőség növelése',
                    'Szintetizált válaszok'
                ]
            })
            st.dataframe(comparison_df, use_container_width=True)

    # 2. MIÉRT FONTOS
    with st.expander("🎯 **2. MIÉRT FONTOS A GEO?**"):
        st.markdown("### Üzleti hatások")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Forgalom diverzifikáció", "+45%", "AI csatornákból")
            st.markdown("""
            - AI csatornákból érkező látogatók
            - Márkaemlítések AI válaszokban
            - Új célcsoportok elérése
            """)
        
        with col2:
            st.metric("Magasabb konverzió", "+28%", "strukturált tartalom")
            st.markdown("""
            - Jobban strukturált tartalom
            - Bizalomépítő elemek
            - Tisztább üzenetek
            """)
        
        with col3:
            st.metric("Jövőállóság", "100%", "AI-first stratégia")
            st.markdown("""
            - AI-first stratégia
            - Korai adaptáció előnye
            - Technológiai vezetőszerep
            """)

    # 3. A GEO 8 PILLÉRE
    with st.expander("🏗️ **3. A GEO 8 PILLÉRE**"):
        st.markdown("### Az AI optimalizálás alapjai")
        
        tabs = st.tabs([
            "1️⃣ Strukturált",
            "2️⃣ Szemantikus",
            "3️⃣ Hitelesség",
            "4️⃣ AI-barát",
            "5️⃣ Mélység",
            "6️⃣ Frissesség",
            "7️⃣ Interaktív",
            "8️⃣ Platform"
        ])
        
        with tabs[0]:
            st.markdown("""
            ### 1. Strukturált tartalom
            - ✅ Világos heading hierarchia (H1→H2→H3)
            - ✅ Számozott és pontozott listák
            - ✅ Táblázatok összehasonlításokhoz
            - ✅ Q&A formátum (kérdés-válasz)
            """)
            
            st.markdown("#### Példa: Teljes strukturált oldal")
            st.code("""
    <!DOCTYPE html>
    <html lang="hu">
    <head>
        <title>SEO és GEO Útmutató 2024</title>
    </head>
    <body>
        <article>
            <h1>Teljes körű SEO és GEO optimalizálási útmutató</h1>
            
            <nav class="toc">
                <h2>Tartalomjegyzék</h2>
                <ol>
                    <li><a href="#bevezetes">Bevezetés</a></li>
                    <li><a href="#alapok">Alapok</a></li>
                    <li><a href="#halado">Haladó technikák</a></li>
                </ol>
            </nav>
            
            <section id="bevezetes">
                <h2>1. Bevezetés a GEO világába</h2>
                <p>A Generative Engine Optimization az AI korszak új SEO-ja...</p>
                
                <h3>1.1 Miért fontos a GEO?</h3>
                <ul>
                    <li>AI platformok térnyerése</li>
                    <li>Változó keresési szokások</li>
                    <li>Új forgalmi források</li>
                </ul>
            </section>
            
            <section id="alapok">
                <h2>2. GEO alapok</h2>
                
                <h3>2.1 Technikai követelmények</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Elem</th>
                            <th>Prioritás</th>
                            <th>Hatás</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Schema markup</td>
                            <td>Magas</td>
                            <td>+40% AI megértés</td>
                        </tr>
                        <tr>
                            <td>Strukturált tartalom</td>
                            <td>Magas</td>
                            <td>+35% relevancia</td>
                        </tr>
                    </tbody>
                </table>
                
                <h3>2.2 Lépésről lépésre útmutató</h3>
                <ol>
                    <li>
                        <strong>Első lépés:</strong> Technikai audit
                        <ul>
                            <li>Robots.txt ellenőrzés</li>
                            <li>Sitemap validáció</li>
                        </ul>
                    </li>
                    <li>
                        <strong>Második lépés:</strong> Tartalom optimalizálás
                        <ul>
                            <li>Heading struktúra</li>
                            <li>Meta adatok</li>
                        </ul>
                    </li>
                </ol>
            </section>
        </article>
    </body>
    </html>
            """, language="html")
        
        with tabs[1]:
            st.markdown("""
            ### 2. Szemantikus jelölések
            - ✅ Schema.org markup (JSON-LD)
            - ✅ FAQ, HowTo, Article sémák
            - ✅ Entity markup (személyek, helyek, termékek)
            - ✅ Rich snippets eligibility
            """)
            
            st.markdown("#### Példa: Többféle Schema típus")
            st.code("""
    <script type="application/ld+json">
    {
    "@context": "https://schema.org",
    "@graph": [
        {
        "@type": "Organization",
        "@id": "https://example.com/#organization",
        "name": "TechCég Kft.",
        "url": "https://example.com",
        "logo": {
            "@type": "ImageObject",
            "url": "https://example.com/logo.png",
            "width": 600,
            "height": 60
        },
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "+36-1-234-5678",
            "contactType": "customer service",
            "areaServed": "HU",
            "availableLanguage": ["hu", "en"]
        },
        "sameAs": [
            "https://facebook.com/techceg",
            "https://linkedin.com/company/techceg",
            "https://twitter.com/techceg"
        ]
        },
        {
        "@type": "WebSite",
        "@id": "https://example.com/#website",
        "url": "https://example.com",
        "name": "TechCég",
        "publisher": {"@id": "https://example.com/#organization"},
        "potentialAction": {
            "@type": "SearchAction",
            "target": "https://example.com/search?q={search_term_string}",
            "query-input": "required name=search_term_string"
        }
        },
        {
        "@type": "FAQPage",
        "mainEntity": [
            {
            "@type": "Question",
            "name": "Mennyi időbe telik a GEO optimalizálás?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "A teljes GEO optimalizálás általában 4-8 hetet vesz igénybe, az oldal méretétől és komplexitásától függően. Az első eredmények már 2-3 hét után láthatóak."
            }
            },
            {
            "@type": "Question",
            "name": "Mi a különbség a SEO és GEO között?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Míg a SEO a hagyományos keresőmotorokra optimalizál, a GEO az AI-alapú keresőkre és chatbotokra fókuszál, strukturált adatokkal és szemantikus jelölésekkel."
            }
            }
        ]
        },
        {
        "@type": "HowTo",
        "name": "Hogyan optimalizáljunk GEO-ra",
        "description": "Lépésről lépésre útmutató a sikeres GEO optimalizáláshoz",
        "totalTime": "PT30M",
        "supply": [
            {
            "@type": "HowToSupply",
            "name": "Schema.org dokumentáció"
            },
            {
            "@type": "HowToSupply",
            "name": "Google Search Console hozzáférés"
            }
        ],
        "step": [
            {
            "@type": "HowToStep",
            "name": "Technikai audit",
            "text": "Ellenőrizd a robots.txt fájlt és a sitemap.xml-t",
            "url": "https://example.com/geo-audit"
            },
            {
            "@type": "HowToStep",
            "name": "Schema implementáció",
            "text": "Add hozzá a megfelelő Schema.org markup-ot",
            "url": "https://example.com/schema-guide"
            }
        ]
        }
    ]
    }
    </script>
            """, language="json")
        
        with tabs[2]:
            st.markdown("""
            ### 3. Forrás hitelesség
            - ✅ Külső hivatkozások megbízható forrásokra
            - ✅ Idézetek és lábjegyzetek
            - ✅ Szerző információk (E-E-A-T)
            - ✅ Publikálási és frissítési dátumok
            """)
            
            st.markdown("#### Példa: Hiteles tartalom jelölések")
            st.code("""
    <article itemscope itemtype="https://schema.org/Article">
        <!-- Szerző információk -->
        <div class="author-box" itemprop="author" itemscope itemtype="https://schema.org/Person">
            <img src="author.jpg" alt="Dr. Nagy János" itemprop="image">
            <div class="author-info">
                <h3 itemprop="name">Dr. Nagy János</h3>
                <p itemprop="jobTitle">SEO szakértő, digitális marketing tanácsadó</p>
                <p itemprop="description">15 éves tapasztalat a keresőoptimalizálásban</p>
                <div class="author-credentials">
                    <span itemprop="alumniOf">BME Informatika</span>
                    <span itemprop="award">Google Partners minősítés</span>
                </div>
                <a href="https://linkedin.com/in/nagyjanos" itemprop="sameAs">LinkedIn profil</a>
            </div>
        </div>
        
        <!-- Publikálási információk -->
        <div class="article-meta">
            <time datetime="2024-01-15" itemprop="datePublished">
                Publikálva: 2024. január 15.
            </time>
            <time datetime="2024-03-20" itemprop="dateModified">
                Frissítve: 2024. március 20.
            </time>
            <span itemprop="publisher" itemscope itemtype="https://schema.org/Organization">
                <span itemprop="name">TechBlog</span>
            </span>
        </div>
        
        <!-- Tartalom hivatkozásokkal -->
        <div itemprop="articleBody">
            <p>A legújabb kutatások szerint <sup><a href="#ref1">[1]</a></sup> a GEO 
            optimalizálás jelentősen növeli az AI platformokon való megjelenést. 
            Egy 2024-es tanulmány <sup><a href="#ref2">[2]</a></sup> kimutatta, hogy...</p>
            
            <blockquote cite="https://research.google/pubs/pub12345">
                <p>"Az AI-alapú keresők 73%-kal több strukturált tartalmat preferálnak"</p>
                <footer>— <cite>Google Research, 2024</cite></footer>
            </blockquote>
        </div>
        
        <!-- Források -->
        <section class="references">
            <h2>Hivatkozások</h2>
            <ol>
                <li id="ref1">
                    Smith, J. et al. (2024). "AI Search Behavior Study". 
                    <i>Journal of Digital Marketing</i>, 45(3), 234-256. 
                    DOI: <a href="https://doi.org/10.1234/jdm.2024.45.234">10.1234/jdm.2024.45.234</a>
                </li>
                <li id="ref2">
                    Brown, K. (2024). "Generative AI and Content Discovery". 
                    <i>Tech Trends Quarterly</i>, 12(1), 45-62.
                    <a href="https://techtrends.com/2024/ai-content">Teljes cikk</a>
                </li>
            </ol>
        </section>
        
        <!-- Fact-checking badge -->
        <div class="fact-check-badge">
            <img src="verified.svg" alt="Ellenőrzött">
            <span>Tényeket ellenőrizte: FactCheck.org</span>
            <time datetime="2024-03-19">2024.03.19</time>
        </div>
    </article>
            """, language="html")
        
        with tabs[3]:
            st.markdown("""
            ### 4. AI-barát formázás
            - ✅ Alt text minden képhez
            - ✅ Figure/figcaption használata
            - ✅ Kód blokkok szintaxis kiemeléssel
            - ✅ Accessibility szempontok (ARIA)
            """)
            
            st.markdown("#### Példa: Teljes AI-barát formázás")
            st.code("""<!-- Képek megfelelő jelöléssel -->
<figure class="ai-optimized-image">
    <img src="dashboard.webp" 
         alt="Google Analytics dashboard 2024 januári forgalmi adatokkal"
         loading="lazy" width="1200" height="600">
    <figcaption>1. ábra: Google Analytics dashboard</figcaption>
</figure>

<!-- ARIA jelölések -->
<nav aria-label="Fő navigáció" role="navigation">
    <ul>
        <li><a href="#home" aria-current="page">Főoldal</a></li>
        <li><a href="#services">Szolgáltatások</a></li>
    </ul>
</nav>

<!-- Form accessibility -->
<form aria-labelledby="contact-form">
    <h3 id="contact-form">Kapcsolat</h3>
    <label for="name">Név <span aria-label="kötelező">*</span></label>
    <input type="text" id="name" required aria-describedby="name-help">
    <div id="name-help">Adja meg teljes nevét</div>
</form>""", language="html")
        
        with tabs[4]:
            st.markdown("""
            ### 5. Tartalom mélység
            - ✅ Átfogó témafeldolgozás (1000+ szó)
            - ✅ Többféle nézőpont bemutatása
            - ✅ Példák és esettanulmányok
            - ✅ Technikai részletesség
            """)
            
            st.markdown("#### Példa: Mély, átfogó tartalom struktúra")
            st.code("""
    <article class="comprehensive-guide">
        <header>
            <h1>GEO Optimalizálás: Teljes körű útmutató 2024</h1>
            <div class="article-stats">
                <span>📖 Olvasási idő: 25 perc</span>
                <span>📝 Szószám: 4,500</span>
                <span>🎯 Nehézségi szint: Középhaladó</span>
            </div>
        </header>
        
        <!-- Vezetői összefoglaló -->
        <section class="executive-summary">
            <h2>Vezetői összefoglaló</h2>
            <div class="key-takeaways">
                <h3>Kulcs megállapítások:</h3>
                <ul>
                    <li>A GEO 45%-kal növelheti az AI-forgalmat</li>
                    <li>ROI átlagosan 180% 6 hónap alatt</li>
                    <li>Implementáció: 4-8 hét</li>
                </ul>
            </div>
        </section>
        
        <!-- Többféle nézőpont -->
        <section class="perspectives">
            <h2>Különböző megközelítések</h2>
            
            <div class="perspective-technical">
                <h3>Technikai szemszög</h3>
                <p>A GEO implementáció technikai oldalról megközelítve elsősorban 
                a strukturált adatok helyes alkalmazásáról szól. A JSON-LD formátumú 
                Schema.org markup használata 73%-kal növeli az AI platformok 
                megértési képességét...</p>
                
                <div class="code-example">
                    <h4>Példa: Optimális Schema struktúra</h4>
                    <pre><code>// 500+ sornyi részletes példakód...</code></pre>
                </div>
            </div>
            
            <div class="perspective-business">
                <h3>Üzleti szemszög</h3>
                <p>Üzleti szempontból a GEO befektetés megtérülése kiváló. 
                Ügyfeleink átlagosan 180%-os ROI-t értek el 6 hónap alatt. 
                A költség-haszon elemzés alapján...</p>
                
                <table class="roi-analysis">
                    <caption>ROI elemzés különböző iparágakban</caption>
                    <!-- Részletes táblázat -->
                </table>
            </div>
            
            <div class="perspective-user">
                <h3>Felhasználói szemszög</h3>
                <p>A felhasználók számára a GEO-optimalizált tartalom 
                könnyebben feldolgozható és relevációbb válaszokat ad...</p>
            </div>
        </section>
        
        <!-- Esettanulmányok -->
        <section class="case-studies">
            <h2>Valós esettanulmányok</h2>
            
            <article class="case-study">
                <h3>Esettanulmány #1: E-commerce webshop</h3>
                <div class="case-metrics">
                    <div class="before-after">
                        <div class="before">
                            <h4>Előtte:</h4>
                            <ul>
                                <li>AI forgalom: 2%</li>
                                <li>Konverzió: 1.2%</li>
                                <li>Bevétel: 450K Ft/hó</li>
                            </ul>
                        </div>
                        <div class="after">
                            <h4>Utána:</h4>
                            <ul>
                                <li>AI forgalom: 18%</li>
                                <li>Konverzió: 3.7%</li>
                                <li>Bevétel: 1.2M Ft/hó</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="implementation-details">
                    <h4>Implementáció részletei:</h4>
                    <ol>
                        <li>Schema.org Product markup implementáció</li>
                        <li>FAQ szekció minden termékhez</li>
                        <li>Részletes használati útmutatók</li>
                        <li>Összehasonlító táblázatok</li>
                    </ol>
                </div>
            </article>
            
            <article class="case-study">
                <h3>Esettanulmány #2: B2B szolgáltató</h3>
                <!-- Még egy részletes esettanulmány -->
            </article>
        </section>
        
        <!-- Technikai mélység -->
        <section class="technical-depth">
            <h2>Technikai implementáció részletesen</h2>
            
            <div class="api-integration">
                <h3>API integráció lépésről lépésre</h3>
                <pre><code class="language-javascript">
    // Teljes API integráció 200+ sor kóddal
    class GEOOptimizer {
        constructor(config) {
            this.apiKey = config.apiKey;
            this.endpoints = {
                analyze: 'https://api.geo-tool.com/analyze',
                optimize: 'https://api.geo-tool.com/optimize'
            };
        }
        
        async analyzeContent(content) {
            // Részletes implementáció...
        }
        
        // További metódusok...
    }
                </code></pre>
            </div>
        </section>
    </article>
            """, language="html")
        
        with tabs[5]:
            st.markdown("""
            ### 6. Frissesség jelek
            - ✅ Aktuális dátumok említése
            - ✅ "Frissítve: YYYY-MM-DD" jelölések
            - ✅ Időszerű információk
            - ✅ Rendszeres tartalom update
            """)
            
            st.markdown("#### Példa: Frissesség jelzések implementálása")
            st.code("""
    <!-- Frissességi meta adatok -->
    <head>
        <meta property="article:published_time" content="2024-01-15T09:00:00+01:00">
        <meta property="article:modified_time" content="2024-03-20T14:30:00+01:00">
        <meta property="article:expiration_time" content="2024-12-31T23:59:59+01:00">
        <meta name="last-modified" content="Wed, 20 Mar 2024 14:30:00 GMT">
        <meta name="revisit-after" content="7 days">
    </head>

    <article>
        <!-- Vizuális frissességi jelzők -->
        <div class="freshness-indicators">
            <div class="update-badge">
                <span class="badge-new">ÚJ</span>
                <time datetime="2024-03-20">Frissítve: 2024. március 20.</time>
            </div>
            
            <div class="content-validity">
                <span class="validity-status">✅ Érvényes</span>
                <span>2024. december 31-ig</span>
            </div>
        </div>
        
        <!-- Időbélyegek a tartalomban -->
        <section class="latest-updates">
            <h2>Legfrissebb változások (2024 Q1)</h2>
            
            <div class="update-log">
                <div class="update-entry">
                    <time datetime="2024-03-20" class="update-date">2024.03.20</time>
                    <h3>Google algoritmus frissítés</h3>
                    <p>A március 19-i Core Update hatásai...</p>
                </div>
                
                <div class="update-entry">
                    <time datetime="2024-03-15" class="update-date">2024.03.15</time>
                    <h3>ChatGPT új funkciók</h3>
                    <p>Az OpenAI bejelentette...</p>
                </div>
            </div>
        </section>
        
        <!-- Trending topics -->
        <section class="trending-now">
            <h2>🔥 Most trending (2024 március)</h2>
            <ul class="trend-list">
                <li data-trend="up">
                    <span class="trend-indicator">📈</span>
                    AI Search Console <span class="new-badge">NEW</span>
                </li>
                <li data-trend="hot">
                    <span class="trend-indicator">🔥</span>
                    Gemini 1.5 Pro integráció
                </li>
            </ul>
        </section>
        
        <!-- Automatikus frissítés értesítő -->
        <div class="auto-update-notice">
            <p>🔄 Ez az oldal automatikusan frissül hetente.</p>
            <p>Következő frissítés: <time datetime="2024-03-27">2024.03.27</time></p>
            <button onclick="subscribeToUpdates()">
                🔔 Értesítés kérése frissítésekről
            </button>
        </div>
        
        <!-- Verziókövetés -->
        <footer class="version-info">
            <dl>
                <dt>Verzió:</dt>
                <dd>2.4.1</dd>
                
                <dt>Utolsó jelentős frissítés:</dt>
                <dd><time datetime="2024-03-01">2024. március 1.</time></dd>
                
                <dt>Kisebb javítások:</dt>
                <dd><time datetime="2024-03-20">2024. március 20.</time></dd>
            </dl>
        </footer>
        
        <!-- Schema.org frissességi markup -->
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "datePublished": "2024-01-15",
            "dateModified": "2024-03-20",
            "expires": "2024-12-31",
            "temporalCoverage": "2024",
            "isBasedOn": {
                "@type": "Dataset",
                "name": "2024 Q1 AI Search Data",
                "temporalCoverage": "2024-01/2024-03"
            }
        }
        </script>
    </article>
            """, language="html")
        
        with tabs[6]:
            st.markdown("""
            ### 7. Interaktivitás
            - ✅ Közvetlen megszólítás
            - ✅ Kérdések a szövegben
            - ✅ Call-to-action elemek
            - ✅ Step-by-step útmutatók
            """)
            
            st.markdown("#### Példa: Interaktív elemek és engagement")
            st.code("""
    <article class="interactive-content">
        <!-- Közvetlen megszólítás -->
        <section class="direct-address">
            <h2>Kezdjük el együtt a GEO optimalizálást!</h2>
            <p>Gondolkodtál már azon, hogy a weboldalad mennyire AI-barát? 
            Most együtt végigmegyünk a folyamaton, lépésről lépésre.</p>
            
            <div class="question-prompt">
                <p>🤔 <strong>Kérdés neked:</strong> Használsz már Schema markup-ot?</p>
                <div class="answer-options">
                    <button onclick="selectAnswer('yes')">✅ Igen, használok</button>
                    <button onclick="selectAnswer('no')">❌ Még nem</button>
                    <button onclick="selectAnswer('unsure')">🤷 Nem tudom</button>
                </div>
            </div>
        </section>
        
        <!-- Interaktív checklist -->
        <section class="interactive-checklist">
            <h2>GEO Audit Checklist - Pipáld ki, amit már megcsináltál!</h2>
            
            <form id="geo-checklist">
                <fieldset>
                    <legend>Alapok</legend>
                    <label>
                        <input type="checkbox" onchange="updateProgress()">
                        <span>Robots.txt AI botok engedélyezve</span>
                    </label>
                    <label>
                        <input type="checkbox" onchange="updateProgress()">
                        <span>Sitemap.xml létezik és naprakész</span>
                    </label>
                </fieldset>
                
                <div class="progress-bar">
                    <div class="progress-fill" id="progress">0%</div>
                </div>
                
                <div class="cta-section">
                    <button type="button" onclick="saveProgress()">
                        💾 Mentés később folytatom
                    </button>
                    <button type="button" onclick="getRecommendations()">
                        🎯 Személyre szabott javaslatok
                    </button>
                </div>
            </form>
        </section>
        
        <!-- Step-by-step guide with progress -->
        <section class="step-guide">
            <h2>Csináld velem: Schema implementáció 5 lépésben</h2>
            
            <div class="steps-container">
                <div class="step active" data-step="1">
                    <div class="step-header">
                        <span class="step-number">1</span>
                        <h3>Schema típus kiválasztása</h3>
                    </div>
                    <div class="step-content">
                        <p>Először válaszd ki, milyen típusú tartalomról van szó:</p>
                        <select onchange="updateSchemaType(this.value)">
                            <option>-- Válassz típust --</option>
                            <option value="article">Cikk/Blog</option>
                            <option value="product">Termék</option>
                            <option value="faq">GYIK</option>
                            <option value="howto">Útmutató</option>
                        </select>
                        <button onclick="nextStep()">Következő →</button>
                    </div>
                </div>
                
                <div class="step" data-step="2">
                    <div class="step-header">
                        <span class="step-number">2</span>
                        <h3>Adatok összegyűjtése</h3>
                    </div>
                    <div class="step-content">
                        <p>Most gyűjtsük össze a szükséges adatokat:</p>
                        <form id="schema-data">
                            <input type="text" placeholder="Cikk címe">
                            <textarea placeholder="Rövid leírás"></textarea>
                            <input type="date" placeholder="Publikálás dátuma">
                        </form>
                        <button onclick="prevStep()">← Vissza</button>
                        <button onclick="nextStep()">Következő →</button>
                    </div>
                </div>
                
                <!-- További lépések... -->
            </div>
            
            <div class="step-progress">
                <div class="progress-dots">
                    <span class="dot active"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                </div>
            </div>
        </section>
        
        <!-- Gamification elemek -->
        <section class="gamification">
            <h2>🏆 GEO Pontjaid</h2>
            
            <div class="score-board">
                <div class="current-score">
                    <span class="score-number">45</span>
                    <span class="score-label">/ 100 pont</span>
                </div>
                
                <div class="achievements">
                    <h3>Elért jelvények:</h3>
                    <div class="badge-list">
                        <div class="badge earned">
                            🎯 <span>Schema Kezdő</span>
                        </div>
                        <div class="badge earned">
                            📝 <span>Tartalom Mester</span>
                        </div>
                        <div class="badge locked">
                            🚀 <span>GEO Guru (Zárolt)</span>
                        </div>
                    </div>
                </div>
                
                <div class="next-goal">
                    <p>Következő cél: <strong>FAQ Schema implementálása</strong></p>
                    <p>Jutalom: +15 pont</p>
                    <button onclick="startChallenge()">Kihívás elfogadása</button>
                </div>
            </div>
        </section>
        
        <!-- Call-to-action elemek -->
        <section class="cta-elements">
            <div class="floating-cta">
                <p>Tetszik amit olvasol?</p>
                <button class="cta-primary">
                    📧 Iratkozz fel a GEO hírlevelünkre
                </button>
            </div>
            
            <div class="inline-cta">
                <p>💡 <strong>Próbáld ki:</strong> Használd a lenti GEO 
                elemző eszközünket, hogy lásd, mennyire AI-barát az oldalad!</p>
                <button onclick="openAnalyzer()">Elemzés indítása →</button>
            </div>
            
            <div class="exit-intent-cta">
                <!-- Megjelenik, ha el akar navigálni -->
                <div class="popup">
                    <h3>Várj! Van egy ajándékunk számodra!</h3>
                    <p>Töltsd le INGYEN a GEO Checklist PDF-et!</p>
                    <button>Letöltés most</button>
                </div>
            </div>
        </section>
    </article>

    <script>
    // Interaktív funkciók
    function updateProgress() {
        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
        const checked = document.querySelectorAll('input[type="checkbox"]:checked');
        const percentage = (checked.length / checkboxes.length) * 100;
        document.getElementById('progress').style.width = percentage + '%';
        document.getElementById('progress').textContent = Math.round(percentage) + '%';
    }

    function nextStep() {
        // Következő lépésre navigálás
    }

    function selectAnswer(answer) {
        // Válasz alapján személyre szabott tartalom
        if (answer === 'no') {
            showContent('schema-beginner-guide');
        } else if (answer === 'yes') {
            showContent('schema-advanced-tips');
        }
    }
    </script>
            """, language="html")
        
        with tabs[7]:
            st.markdown("""
            ### 8. Platform-specifikus optimalizálás
            - ✅ ChatGPT: lépésenkénti útmutatók
            - ✅ Claude: mély, árnyalt tartalom
            - ✅ Gemini: multimédia elemek
            - ✅ Bing: források és hivatkozások
            """)
            
            st.markdown("#### Példa: Multi-platform optimalizált tartalom")
            st.code("""
    <!-- Platform-specifikus tartalom blokkok -->
    <article class="multi-platform-optimized">
        
        <!-- ChatGPT optimalizált szekció -->
        <section class="chatgpt-optimized" data-platform="chatgpt">
            <h2>Hogyan optimalizálj ChatGPT-re? (Lépésről lépésre)</h2>
            
            <div class="numbered-steps">
                <ol class="step-list">
                    <li>
                        <h3>1. lépés: Strukturáld a tartalmat</h3>
                        <p>Használj tiszta heading hierarchiát:</p>
                        <pre><code>&lt;h1&gt; → &lt;h2&gt; → &lt;h3&gt;</code></pre>
                        <div class="step-tip">
                            💡 Tipp: Minden H2 alatt legyen legalább 2 H3
                        </div>
                    </li>
                    
                    <li>
                        <h3>2. lépés: Implementálj FAQ szekciót</h3>
                        <p>Adj hozzá strukturált kérdés-válasz blokkokat:</p>
                        <div class="faq-example">
                            <strong>K: Mi a GEO?</strong>
                            <p>V: A GEO (Generative Engine Optimization)...</p>
                        </div>
                    </li>
                    
                    <li>
                        <h3>3. lépés: Használj példakódokat</h3>
                        <pre><code class="language-html">
    &lt;div class="chatgpt-friendly"&gt;
        &lt;h2&gt;Cím&lt;/h2&gt;
        &lt;ol&gt;
            &lt;li&gt;Első lépés&lt;/li&gt;
            &lt;li&gt;Második lépés&lt;/li&gt;
        &lt;/ol&gt;
    &lt;/div&gt;
                        </code></pre>
                    </li>
                </ol>
            </div>
        </section>
        
        <!-- Claude optimalizált szekció -->
        <section class="claude-optimized" data-platform="claude">
            <h2>Claude optimalizálás: Mélység és kontextus</h2>
            
            <div class="comprehensive-content">
                <div class="context-section">
                    <h3>Történelmi háttér és evolúció</h3>
                    <p>A keresőoptimalizálás története az 1990-es évek végére 
                    nyúlik vissza, amikor a első keresőmotorok megjelentek. 
                    Larry Page és Sergey Brin PageRank algoritmusa forradalmasította...</p>
                    
                    <blockquote class="academic-citation">
                        "A szemantikus web koncepciója, amelyet Tim Berners-Lee 
                        vezetett be 2001-ben, megalapozta a mai AI-alapú keresést"
                        <cite>— Berners-Lee, T. (2001). Scientific American</cite>
                    </blockquote>
                </div>
                
                <div class="nuanced-analysis">
                    <h3>Többrétegű elemzés és kritikai gondolkodás</h3>
                    <p>Míg egyesek szerint a GEO csupán a SEO evolúciója, 
                    érdemes megvizsgálni az ellenvéleményeket is. Kritikusok 
                    szerint a túlzott AI-optimalizálás...</p>
                    
                    <div class="perspectives">
                        <div class="pro-argument">
                            <h4>Támogatók érvelése:</h4>
                            <ul>
                                <li>Jobb felhasználói élmény</li>
                                <li>Pontosabb információ közvetítés</li>
                                <li>Hatékonyabb tartalom discovery</li>
                            </ul>
                        </div>
                        
                        <div class="counter-argument">
                            <h4>Kritikusok szempontjai:</h4>
                            <ul>
                                <li>Túlzott homogenizáció veszélye</li>
                                <li>Kreativitás csökkenése</li>
                                <li>Függőség az AI rendszerektől</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="references">
                    <h3>Tudományos források és hivatkozások</h3>
                    <ol class="reference-list">
                        <li>Smith, J. et al. (2024). "AI Search Patterns". 
                            <i>Journal of Information Science</i>, 45(3), 234-251.</li>
                        <li>Johnson, M. (2023). "The Evolution of Search". 
                            Cambridge University Press.</li>
                    </ol>
                </div>
            </div>
        </section>
        
        <!-- Gemini optimalizált szekció -->
        <section class="gemini-optimized" data-platform="gemini">
            <h2>Gemini optimalizálás: Vizuális és multimédia</h2>
            
            <div class="multimedia-rich">
                <!-- Képgaléria -->
                <div class="image-gallery">
                    <figure>
                        <img src="geo-infographic.webp" 
                            alt="GEO folyamat infografika 8 lépésben"
                            loading="lazy">
                        <figcaption>1. ábra: A GEO implementáció folyamata</figcaption>
                    </figure>
                    
                    <figure>
                        <img src="ai-platforms-comparison.webp" 
                            alt="AI platformok összehasonlító táblázata">
                        <figcaption>2. ábra: Platform-specifikus követelmények</figcaption>
                    </figure>
                </div>
                
                <!-- YouTube videó embed -->
                <div class="video-content">
                    <h3>Videó útmutató</h3>
                    <iframe width="560" height="315" 
                            src="https://www.youtube.com/embed/abc123" 
                            title="GEO optimalizálás gyakorlatban"
                            loading="lazy"
                            allow="accelerometer; autoplay; clipboard-write">
                    </iframe>
                </div>
                
                <!-- Interaktív diagram -->
                <div class="interactive-chart">
                    <canvas id="geo-metrics-chart"></canvas>
                    <script>
                        // Chart.js implementáció
                        const ctx = document.getElementById('geo-metrics-chart');
                        new Chart(ctx, {
                            type: 'radar',
                            data: {
                                labels: ['Struktúra', 'Schema', 'Frissesség', 
                                        'Források', 'Multimédia'],
                                datasets: [{
                                    label: 'Jelenlegi',
                                    data: [65, 45, 80, 55, 30]
                                }]
                            }
                        });
                    </script>
                </div>
                
                <!-- Google termék integráció -->
                <div class="google-integration">
                    <h3>Google Maps integráció</h3>
                    <iframe src="https://maps.google.com/maps?q=Budapest"
                            width="600" height="450"
                            style="border:0;"
                            loading="lazy">
                    </iframe>
                </div>
            </div>
        </section>
        
        <!-- Bing Chat optimalizált szekció -->
        <section class="bing-optimized" data-platform="bing">
            <h2>Bing Chat optimalizálás: Források és aktualitás</h2>
            
            <div class="source-rich-content">
                <!-- Hivatkozások és források -->
                <div class="citations">
                    <p>A legfrissebb kutatások szerint 
                    <sup><a href="https://research.microsoft.com/geo-2024">[1]</a></sup> 
                    a Bing Chat 67%-ban preferálja a jól hivatkozott tartalmakat. 
                    Egy másik tanulmány 
                    <sup><a href="https://techcrunch.com/2024/03/ai-search">[2]</a></sup> 
                    kimutatta...</p>
                    
                    <div class="source-list">
                        <h3>Források:</h3>
                        <ol>
                            <li><a href="https://research.microsoft.com/geo-2024" 
                                rel="nofollow" target="_blank">
                                Microsoft Research: GEO Study 2024
                            </a></li>
                            <li><a href="https://techcrunch.com/2024/03/ai-search" 
                                rel="nofollow" target="_blank">
                                TechCrunch: The Rise of AI Search
                            </a></li>
                        </ol>
                    </div>
                </div>
                
                <!-- Friss hírek és események -->
                <div class="latest-news">
                    <h3>🔥 Legfrissebb fejlemények (2024.03.20)</h3>
                    <ul class="news-list">
                        <li>
                            <time datetime="2024-03-20">Ma</time>
                            <a href="https://bing.com/news/ai-update">
                                Bing új AI funkciók bejelentése
                            </a>
                        </li>
                        <li>
                            <time datetime="2024-03-19">Tegnap</time>
                            <a href="https://reuters.com/tech/search">
                                Reuters: AI keresés piaci elemzés
                            </a>
                        </li>
                    </ul>
                </div>
                
                <!-- Fact-checking -->
                <div class="fact-verification">
                    <h3>✓ Ellenőrzött tények</h3>
                    <table class="fact-table">
                        <tr>
                            <td>Állítás</td>
                            <td>Státusz</td>
                            <td>Forrás</td>
                        </tr>
                        <tr>
                            <td>A GEO 45%-kal növeli a forgalmat</td>
                            <td>✅ Igazolt</td>
                            <td><a href="#">Microsoft Study</a></td>
                        </tr>
                    </table>
                </div>
            </div>
        </section>
        
        <!-- Platform routing script -->
        <script>
        // Platform detection és megfelelő tartalom megjelenítése
        function detectPlatform() {
            const userAgent = navigator.userAgent;
            let platform = 'general';
            
            if (userAgent.includes('ChatGPT')) {
                platform = 'chatgpt';
            } else if (userAgent.includes('Claude')) {
                platform = 'claude';
            } else if (userAgent.includes('Gemini')) {
                platform = 'gemini';
            } else if (userAgent.includes('BingBot')) {
                platform = 'bing';
            }
            
            // Platform-specifikus tartalom kiemelése
            document.querySelectorAll('[data-platform]').forEach(section => {
                if (section.dataset.platform === platform) {
                    section.classList.add('highlighted');
                    section.style.order = '-1'; // Előre helyezés
                }
            });
        }
        
        detectPlatform();
        </script>
    </article>
            """, language="html")

    # 4. PLATFORM STRATÉGIÁK
    with st.expander("📊 **4. PLATFORM-SPECIFIKUS STRATÉGIÁK**"):
        platform_tab = st.tabs(["🤖 ChatGPT", "🧠 Claude", "✨ Gemini", "🔍 Bing Chat"])
        
        with platform_tab[0]:
            st.markdown("### ChatGPT optimalizálás (0-100 pont)")
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.metric("Cél pontszám", "85+", "+60")
                st.markdown("""
                **Mit preferál:**
                - ✅ Számozott lépések
                - ✅ Világos Q&A formátum
                - ✅ Gyakorlati példák kóddal
                - ✅ Strukturált listák
                """)
            
            with col2:
                st.markdown("**Példa implementáció:**")
                st.code("""
    <section class="chatgpt-optimized">
    <h2>Hogyan készíts weboldalt? - Lépésről lépésre</h2>
    <ol>
        <li><strong>Tervezés:</strong> Határozd meg a célokat</li>
        <li><strong>Domain:</strong> Válassz és regisztrálj domaint</li>
        <li><strong>Hosting:</strong> Szerezz megbízható tárhelyet</li>
        <li><strong>Fejlesztés:</strong> Építsd meg az oldalt</li>
        <li><strong>Tesztelés:</strong> Ellenőrizd minden eszközön</li>
    </ol>
    </section>
                """, language="html")
        
        with platform_tab[1]:
            st.markdown("### Claude optimalizálás")
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.metric("Cél pontszám", "85+", "+62")
                st.markdown("""
                **Mit preferál:**
                - ✅ Hosszú tartalom (2000+ szó)
                - ✅ Tudományos hivatkozások
                - ✅ Árnyalt érvelés
                - ✅ Kontextus és háttér
                """)
            
            with col2:
                st.markdown("**Példa implementáció:**")
                st.code("""
    <article class="claude-optimized">
    <section class="context">
        <h2>Történelmi háttér és kontextus</h2>
        <p>A téma megértéséhez fontos ismerni... 
        Kutatások szerint <cite>(Smith et al., 2023)</cite>...</p>
    </section>
    </article>
                """, language="html")
        
        with platform_tab[2]:
            st.markdown("### Gemini optimalizálás")
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.metric("Cél pontszám", "85+", "+71")
                st.markdown("""
                **Mit preferál:**
                - ✅ Gazdag multimédia
                - ✅ Friss, aktuális tartalom
                - ✅ Google integráció
                - ✅ Strukturált adatok
                """)
            
            with col2:
                st.markdown("**Példa implementáció:**")
                st.code("""
    <div class="gemini-optimized">
    <figure>
        <img src="infographic.webp" alt="Részletes infografika">
        <figcaption>2024-es piaci trendek vizualizációja</figcaption>
    </figure>
    <div class="video-embed">
        <iframe src="https://youtube.com/embed/..."></iframe>
    </div>
    </div>
                """, language="html")
        
        with platform_tab[3]:
            st.markdown("### Bing Chat optimalizálás")
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.metric("Cél pontszám", "85+", "+75")
                st.markdown("""
                **Mit preferál:**
                - ✅ Megbízható források
                - ✅ Friss hírek
                - ✅ Külső hivatkozások
                - ✅ Fact-checking
                """)
            
            with col2:
                st.markdown("**Példa implementáció:**")
                st.code("""
    <div class="bing-optimized">
    <p>Források szerint <a href="source1.com">[1]</a>...</p>
    <div class="fact-check">
        ✓ Ellenőrzött tény: 2024.10.15
    </div>
    </div>
                """, language="html")

    # 5. TECHNIKAI IMPLEMENTÁCIÓ
    with st.expander("🔧 **5. TECHNIKAI IMPLEMENTÁCIÓ**"):
        tech_tabs = st.tabs(["Schema.org", "Robots.txt", "Meta tagek", "API példa"])
        
        with tech_tabs[0]:
            st.markdown("### Kötelező Schema.org markup")
            st.code("""
    {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [{
        "@type": "Question",
        "name": "Mi az a GEO?",
        "acceptedAnswer": {
        "@type": "Answer",
        "text": "A GEO a Generative Engine Optimization..."
        }
    }]
    }
            """, language="json")
        
        with tech_tabs[1]:
            st.markdown("### Robots.txt AI botoknak")
            st.code("""
    # AI Botok engedélyezése
    User-agent: GPTBot
    Allow: /

    User-agent: Claude-Web
    Allow: /

    User-agent: anthropic-ai
    Allow: /

    User-agent: CCBot
    Allow: /

    # Sitemaps
    Sitemap: https://example.com/sitemap.xml
            """, language="text")
        
        with tech_tabs[2]:
            st.markdown("### Meta tagek AI-hoz")
            st.code("""
    <meta name="description" content="Átfogó útmutató...">
    <meta name="author" content="Szerző neve">
    <meta name="last-modified" content="2024-01-15">
    <meta property="article:published_time" content="2024-01-01">
    <meta property="article:modified_time" content="2024-01-15">
            """, language="html")
        
        with tech_tabs[3]:
            st.markdown("### Python API példa")
            st.code("""
    from geo_analyzer import GEOAnalyzer

    # Inicializálás
    analyzer = GEOAnalyzer()

    # URL elemzése
    result = analyzer.analyze_url("https://example.com")

    # Eredmények
    print(f"AI Readiness Score: {result['ai_readiness_score']}")
    print(f"ChatGPT Score: {result['platform_scores']['chatgpt']}")
    print(f"Claude Score: {result['platform_scores']['claude']}")
            """, language="python")

    # 6. MÉRÉS ÉS MONITORING
    with st.expander("📈 **6. MÉRÉS ÉS MONITORING**"):
        st.markdown("### KPI-ok és metrikák")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### AI Readiness Score komponensek")
            
            metrics_df = pd.DataFrame({
                'Komponens': [
                    'Strukturáltság',
                    'Q&A formátum',
                    'Szemantikus jelölések',
                    'Forrás hitelesség',
                    'Frissesség',
                    'Tartalom mélység',
                    'Interaktivitás'
                ],
                'Súlyozás': ['25%', '20%', '15%', '15%', '10%', '10%', '5%']
            })
            st.dataframe(metrics_df, use_container_width=True)
        
        with col2:
            st.markdown("#### Platform-specifikus pontok")
            
            # Példa pontszámok vizualizáció
            platform_scores = {
                'ChatGPT': 85,
                'Claude': 78,
                'Gemini': 92,
                'Bing Chat': 71
            }
            
            for platform, score in platform_scores.items():
                st.progress(score/100, text=f"{platform}: {score}/100")

    # 7. GEO CHECKLIST
    with st.expander("✅ **7. GEO CHECKLIST - Hogyan érj el 100%-ot?**"):
        st.markdown("### Progresszív fejlesztési terv")
        
        checklist_tabs = st.tabs(["🟢 Alapok (0→40)", "🟡 Haladó (40→70)", "🔴 Expert (70→100)"])
        
        with checklist_tabs[0]:
            st.markdown("### Alapok (0→40 pont)")
            st.checkbox("H1-H6 hierarchia rendben")
            st.checkbox("Meta title és description optimalizált")
            st.checkbox("Mobile-friendly viewport")
            st.checkbox("Robots.txt AI botok engedélyezve")
            st.checkbox("Sitemap.xml létezik")
            st.progress(0.4, text="40% - Alapszint teljesítve")
        
        with checklist_tabs[1]:
            st.markdown("### Haladó (40→70 pont)")
            st.checkbox("FAQ schema implementálva")
            st.checkbox("3+ strukturált lista/táblázat")
            st.checkbox("5+ külső hivatkozás")
            st.checkbox("Szerző információk")
            st.checkbox("Frissítési dátumok")
            st.progress(0.7, text="70% - Haladó szint teljesítve")
        
        with checklist_tabs[2]:
            st.markdown("### Expert (70→100 pont)")
            st.checkbox("2000+ szó mélységű tartalom")
            st.checkbox("Platform-specifikus optimalizáció")
            st.checkbox("Entity markup teljes")
            st.checkbox("Multimédia elemek alt texttel")
            st.checkbox("Step-by-step útmutatók")
            st.progress(1.0, text="100% - Expert szint teljesítve!")

    # 8. QUICK WINS
    with st.expander("🚀 **8. QUICK WINS - Gyors javítások**"):
        quick_tabs = st.tabs(["⏱️ 15 perc", "⏰ 1 óra", "📅 1 nap"])
        
        with quick_tabs[0]:
            st.markdown("### 15 perces javítások")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.info("**Alt text hozzáadása**\n\n+5 pont\n\nMinden képhez")
            with col2:
                st.info("**FAQ schema**\n\n+10 pont\n\nJSON-LD implementáció")
            with col3:
                st.info("**Frissítési dátum**\n\n+3 pont\n\nMeta és látható")
        
        with quick_tabs[1]:
            st.markdown("### 1 órás javítások")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.warning("**Tartalom strukturálása**\n\n+8 pont\n\nListák hozzáadása")
            with col2:
                st.warning("**Q&A szekció**\n\n+12 pont\n\n5-10 kérdés")
            with col3:
                st.warning("**Schema.org markup**\n\n+15 pont\n\nTeljes implementáció")
        
        with quick_tabs[2]:
            st.markdown("### 1 napos projekt")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.success("**Teljes átírás**\n\n+25 pont\n\nAI-barát formátum")
            with col2:
                st.success("**Platform oldalak**\n\n+20 pont\n\nEgyedi optimalizáció")
            with col3:
                st.success("**Comprehensive guide**\n\n+30 pont\n\n3000+ szó")

    # 9. GYAKORLATI PÉLDA
    with st.expander("📝 **9. GYAKORLATI PÉLDA ELEMZÉS**"):
        st.markdown("### example.com elemzése")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### Jelenlegi állapot")
            st.metric("AI Readiness Score", "16.5/100", "-83.5", delta_color="inverse")
            
            st.markdown("**Platform pontok:**")
            scores = {
                'ChatGPT': 25.0,
                'Claude': 23.6,
                'Gemini': 13.6,
                'Bing Chat': 10.2
            }
            for platform, score in scores.items():
                st.progress(score/100, text=f"{platform}: {score:.1f}")
        
        with col2:
            st.markdown("#### Főbb problémák és javítások")
            
            problems_df = pd.DataFrame({
                'Probléma': [
                    'Nincs FAQ/Q&A tartalom',
                    'Hiányzó schema markup',
                    'Túl rövid tartalom (31 szó)',
                    'Nincs forrás/hivatkozás',
                    'Hiányzó frissességi jelek'
                ],
                'Javítás': [
                    'FAQ schema + Q&A tartalom',
                    'Entity/Organization schema',
                    'Tartalom bővítése 1000+ szóra',
                    'Külső források hozzáadása',
                    'Dátumok és frissítések'
                ],
                'Várható javulás': [
                    '+88%',
                    '+70%',
                    '+61%',
                    '+45%',
                    '+30%'
                ]
            })
            st.dataframe(problems_df, use_container_width=True)

    # 10. ÖSSZEFOGLALÁS
    with st.expander("🎯 **10. ÖSSZEFOGLALÁS ÉS AKCIÓTERV**"):
        st.markdown("### A GEO 3 aranyszabálya")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            #### 1️⃣ Strukturáld
            Az AI-k szeretik a rendezett információt
            """)
        
        with col2:
            st.markdown("""
            #### 2️⃣ Jelöld
            Schema markup = AI-barát metadata
            """)
        
        with col3:
            st.markdown("""
            #### 3️⃣ Hivatkozz
            Hiteles források = megbízható tartalom
            """)
        
        st.divider()
        
        st.markdown("### 8 hetes akcióterv")
        
        timeline_df = pd.DataFrame({
            'Időszak': [
                'Hét 1-2',
                'Hét 3-4',
                'Hét 5-6',
                'Hét 7-8'
            ],
            'Fókusz': [
                'Technikai alapok',
                'Tartalom átdolgozás',
                'Platform tuning',
                'Mérés és finomhangolás'
            ],
            'Főbb feladatok': [
                'Robots.txt, Schema, Meta optimalizálás',
                'FAQ/Q&A, Listák, Források',
                'ChatGPT/Claude/Gemini/Bing specifikus',
                'Audit, Tesztek, Iteratív javítások'
            ],
            'Várható eredmény': [
                '+25 pont',
                '+30 pont',
                '+25 pont',
                '+20 pont'
            ]
        })
        st.dataframe(timeline_df, use_container_width=True)
        
        st.divider()
        
        st.markdown("### Várható ROI")
        
        roi_col1, roi_col2, roi_col3, roi_col4 = st.columns(4)
        
        with roi_col1:
            st.metric("30 nap", "+15-25%", "organic traffic")
        with roi_col2:
            st.metric("60 nap", "+25-40%", "AI visibility")
        with roi_col3:
            st.metric("90 nap", "+30-50%", "overall engagement")
        with roi_col4:
            st.metric("Konverzió", "+10-20%", "conversion rate")

    # FOOTER
    st.markdown("""
    ---
    ### 🔗 Hasznos források

    - [Schema.org dokumentáció](https://schema.org)
    - [Google Rich Results Test](https://search.google.com/test/rich-results)
    - [OpenAI Bot dokumentáció](https://platform.openai.com/docs/gptbot)
    - [Anthropic Claude crawler](https://support.anthropic.com/en/articles/8896518)

    *Ez az oktatóanyag a GEOcheck rendszer elemzési metodológiáján és a 2024-es best practice-eken alapul.*
    """)

# Footer
st.markdown("---")
st.markdown("🚀 **GEOcheck** | AI & ML támogatott generativ engine optimalizált website ellenőrző rendszer | Fejlesztette: Ecsedi Tamás | 2025")