import streamlit as st
import json
import os
from main import analyze_urls_enhanced, GEOAnalyzer
from report import generate_html_report, generate_csv_export
from advanced_reporting import AdvancedReportGenerator  
import time

st.set_page_config(
    page_title="Enhanced GEO Analyzer",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Enhanced GEO AI Readiness Analyzer")
st.markdown("**Generative Engine Optimization** elemzés eszköz - AI-Enhanced verzió")

# Sidebar beállítások
st.sidebar.header("⚙️ Beállítások")

# API kulcs beállítás
api_key = st.sidebar.text_input(
    "Google PageSpeed API kulcs:",
    type="password",
    help="Opcionális - PageSpeed Insights-hoz szükséges"
)

# Enhanced beállítások
st.sidebar.subheader("🤖 AI Enhancement")

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

# Elemzési opciók
st.sidebar.subheader("📊 Elemzési beállítások")

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

st.sidebar.subheader("🚀 Fejlett funkciók")

generate_advanced_reports = st.sidebar.checkbox(
    "Fejlett jelentések generálása",
    value=True,
    help="Executive, technikai és action plan jelentések"
)

report_type = st.sidebar.selectbox(
    "Jelentés típusa:",
    ["executive", "technical", "action_plan", "competitor"],
    help="Milyen típusú részletes jelentést szeretnél?"
)

enable_ai_fixes = st.sidebar.checkbox(
    "Automatikus javítási javaslatok",
    value=True,
    help="AI-alapú optimalizálási javaslatok generálása"
)

platform_focus = st.sidebar.multiselect(
    "AI platform fókusz:",
    ["ChatGPT", "Claude", "Gemini", "Bing Chat"],
    default=["ChatGPT", "Claude"],
    help="Melyik AI platformokra optimalizálj?"
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
            cleanup_result = analyzer.cleanup_cache()
            st.sidebar.success(f"Törölve: {cleanup_result.get('cleaned_files', 0)} fájl")
        except Exception as e:
            st.sidebar.error(f"Tisztítás hiba: {e}")

# Főoldal
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📝 URL-ek megadása")
    
    # URL input módok
    input_method = st.radio(
        "URL megadás módja:",
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
    
    # URL előnézet
    if url_list:
        st.success(f"✅ {len(url_list)} URL betöltve")
        with st.expander("URL lista előnézete"):
            for i, url in enumerate(url_list[:10], 1):
                ai_icon = "🤖" if use_ai_evaluation else "📊"
                cache_icon = "💾" if use_cache else "🔄"
                st.text(f"{i}. {ai_icon}{cache_icon} {url}")
            if len(url_list) > 10:
                st.text(f"... és még {len(url_list) - 10} URL")

with col2:
    st.header("📊 Előző elemzések")
    
    # Enhanced jelentések listázása
    json_files = [f for f in os.listdir('.') if f.endswith('_report.json')]
    enhanced_files = [f for f in json_files if 'enhanced' in f]
    html_files = [f for f in os.listdir('.') if f.endswith('.html') and 'report' in f]
    
    if enhanced_files:
        st.subheader("🤖 Enhanced jelentések:")
        for file in enhanced_files[:5]:
            if st.button(f"📁 {file}", key=f"enhanced_{file}"):
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Enhanced adatok megjelenítése
                valid_results = [r for r in data if 'ai_readiness_score' in r and 'error' not in r]
                ai_enhanced_count = len([r for r in valid_results if r.get('ai_content_evaluation')])
                
                st.json({
                    "total_sites": len(data),
                    "valid_results": len(valid_results),
                    "ai_enhanced_results": ai_enhanced_count,
                    "avg_score": sum(r['ai_readiness_score'] for r in valid_results) / len(valid_results) if valid_results else 0
                })
    
    if json_files and not enhanced_files:
        st.subheader("📊 Standard jelentések:")
        for file in json_files[:5]:
            if st.button(f"📁 {file}", key=f"json_{file}"):
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                st.json(data[:2] if isinstance(data, list) else data)  # Csak mintát mutatunk
    
    if html_files:
        st.subheader("📄 HTML jelentések:")
        for file in html_files[:5]:
            st.markdown(f"📄 [{file}](./{file})")

# Elemzés indítása
st.header("🚀 Enhanced Elemzés indítása")

# Elemzés konfigurációjának megjelenítése
if url_list:
    config_col1, config_col2, config_col3 = st.columns(3)
    
    with config_col1:
        st.metric("URL-ek száma", len(url_list))
        st.metric("Párhuzamos szálak", max_workers if parallel_processing else 1)
    
    with config_col2:
        st.metric("AI Enhancement", "✅" if use_ai_evaluation else "❌")
        st.metric("Cache", "✅" if use_cache else "❌")
    
    with config_col3:
        st.metric("PageSpeed", "❌" if skip_pagespeed else "✅")
        st.metric("Force Refresh", "✅" if force_refresh else "❌")

if st.button("▶️ Enhanced Elemzés kezdése", type="primary", disabled=not bool(url_list)):
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
            
            status_text.text("🤖 Enhanced URL-ek elemzése folyamatban...")
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
            status_text.text("📋 Enhanced HTML jelentés generálása...")
            
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
            status_text.text(f"✅ Enhanced elemzés befejezve! ({elapsed_time:.1f} másodperc)")
            
            # Download gombok
            col1, col2, col3 = st.columns(3)
            
            with col1:
                with open(json_filename, 'rb') as f:
                    st.download_button(
                        "🤖 Enhanced JSON",
                        f,
                        file_name=json_filename,
                        mime="application/json"
                    )
            
            with col2:
                with open(html_filename, 'rb') as f:
                    st.download_button(
                        "📄 Enhanced HTML",
                        f,
                        file_name=html_filename,
                        mime="text/html"
                    )
            
            with col3:
                with open(csv_filename, 'rb') as f:
                    st.download_button(
                        "📈 Enhanced CSV",
                        f,
                        file_name=csv_filename,
                        mime="text/csv"
                    )
            
            # Enhanced összefoglaló megjelenítése
            with open(json_filename, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            st.header("📈 Enhanced Összefoglaló")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            valid_results = [r for r in results if 'ai_readiness_score' in r and 'error' not in r]
            ai_enhanced_results = [r for r in valid_results if r.get('ai_content_evaluation')]
            schema_enhanced_results = [r for r in valid_results if r.get('schema', {}).get('validation_status') == 'enhanced']
            
            with col1:
                st.metric("Elemzett oldalak", len(results))
            
            with col2:
                if valid_results:
                    avg_score = sum(r['ai_readiness_score'] for r in valid_results) / len(valid_results)
                    st.metric("Átlagos AI Score", f"{avg_score:.1f}/100")
            
            with col3:
                st.metric("AI Enhanced", len(ai_enhanced_results))
            
            with col4:
                st.metric("Schema Enhanced", len(schema_enhanced_results))
            
            with col5:
                excellent_count = sum(1 for r in valid_results if r['ai_readiness_score'] >= 70)
                st.metric("Kiváló oldalak", excellent_count)
            
            # Részletes enhanced eredmények
            if valid_results:
                st.subheader("🏆 Enhanced Legjobb eredmények")
                sorted_results = sorted(valid_results, key=lambda x: x['ai_readiness_score'], reverse=True)
                
                for i, result in enumerate(sorted_results[:5], 1):
                    score = result['ai_readiness_score']
                    url = result['url']
                    
                    # Enhanced ikonok
                    ai_icon = "🤖" if result.get('ai_content_evaluation') else "📊"
                    schema_icon = "🏗️" if result.get('schema', {}).get('validation_status') == 'enhanced' else "📋"
                    cache_icon = "💾" if result.get('cached') else "🔄"
                    
                    # Szín a score alapján
                    if score >= 80:
                        color = "🟢"
                    elif score >= 60:
                        color = "🟡"
                    else:
                        color = "🔴"
                    
                    st.write(f"{color} **{i}.** {ai_icon}{schema_icon}{cache_icon} {url} - **{score}/100**")
                    
                    # Enhanced részletek
                    if result.get('ai_content_evaluation'):
                        ai_overall = result['ai_content_evaluation'].get('overall_ai_score', 0)
                        st.caption(f"   AI Overall Score: {ai_overall:.1f}/100")
                    
                    if result.get('schema', {}).get('validation_status') == 'enhanced':
                        schema_score = result['schema'].get('schema_completeness_score', 0)
                        st.caption(f"   Schema Completeness: {schema_score:.1f}/100")
            
            # Cache statisztikák megjelenítése
            if use_cache:
                st.subheader("💾 Cache Teljesítmény")
                try:
                    analyzer = GEOAnalyzer(use_cache=True)
                    cache_stats = analyzer.get_cache_stats()
                    
                    cache_col1, cache_col2, cache_col3 = st.columns(3)
                    with cache_col1:
                        st.metric("Cache fájlok", cache_stats.get('total_files', 0))
                    with cache_col2:
                        st.metric("Érvényes cache", cache_stats.get('valid_files', 0))
                    with cache_col3:
                        st.metric("Cache méret", f"{cache_stats.get('total_size_mb', 0)} MB")
                        
                except Exception as e:
                    st.warning(f"Cache statisztikák nem elérhetők: {e}")
            
        except Exception as e:
            st.error(f"❌ Hiba történt az enhanced elemzés során: {str(e)}")
            status_text.text("❌ Enhanced elemzés megszakítva")
            import traceback
            st.code(traceback.format_exc())

# Információs szekció
with st.expander("ℹ️ Enhanced GEO Analyzer információk"):
    st.markdown("""
    ### 🚀 Újdonságok az Enhanced verzióban:
    
    **🤖 AI-alapú tartalom értékelés:**
    - Valódi AI-alapú tartalom minőség értékelés
    - Platform-specifikus AI optimalizálás
    - Szemantikai releváncia mérés
    - Faktualitás ellenőrzés
    
    **💾 Intelligens Cache rendszer:**
    - Automatikus eredmény cache-elés
    - Gyorsabb újrafuttatás
    - Intelligent invalidation
    - Cache statisztikák és tisztítás
    
    **🏗️ Enhanced Schema validáció:**
    - Google Rich Results Test szimuláció
    - Schema effectiveness mérés
    - Dinamikus schema ajánlások
    - AI-alapú schema generálás
    
    **📊 Platform-specifikus fejlesztések:**
    - Machine Learning alapú scoring
    - Hibrid pontszámítás (heurisztikus + AI)
    - Platform-specifikus A/B testing lehetőség
    - Enhanced competitive analysis
    
    ### Mi az a GEO (Generative Engine Optimization)?
    
    A **Generative Engine Optimization** az AI-alapú keresőmotorok (mint ChatGPT, Claude, Gemini) számára való optimalizálás.
    
    ### Mit ellenőriz az Enhanced alkalmazás?
    
    ✅ **Minden eredeti funkció plus:**
    - AI-alapú tartalom minőség értékelés
    - Enhanced schema validáció és effectiveness
    - Platform-specifikus AI scoring
    - Intelligent caching és performance optimization
    
    ### Hogyan használd az Enhanced verziót?
    
    1. **AI Enhancement:** Kapcsold be a fejlett AI értékelést
    2. **Cache:** Használd a cache-t a gyorsabb elemzésért  
    3. **URL-ek:** Add meg az elemezni kívánt URL-eket
    4. **Elemzés:** Indítsd el az enhanced elemzést
    5. **Eredmények:** Töltsd le a részletes jelentéseket
    
    ### Enhanced API kulcsok
    
    Az Enhanced verzió jelenleg szimulálja az AI API hívásokat a költséghatékonyság érdekében.
    Valós implementációban Claude/OpenAI API kulcsok szükségesek.
    """)

# Footer
st.markdown("---")
st.markdown("🚀 **Enhanced GEO Analyzer** | AI-Powered Analysis | Készítette: Ecsedi Tamás | 2025")