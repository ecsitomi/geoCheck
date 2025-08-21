import streamlit as st
import json
import os
from main import analyze_urls, GEOAnalyzer
from report import generate_html_report, generate_csv_export
import time

st.set_page_config(
    page_title="GEO Analyzer",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 GEO AI Readiness Analyzer")
st.markdown("**Generative Engine Optimization** elemzés eszköz")

# Sidebar beállítások
st.sidebar.header("⚙️ Beállítások")

# API kulcs beállítás
api_key = st.sidebar.text_input(
    "Google PageSpeed API kulcs:",
    type="password",
    help="Opcionális - PageSpeed Insights-hoz szükséges"
)

# Elemzési opciók
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
                st.text(f"{i}. {url}")
            if len(url_list) > 10:
                st.text(f"... és még {len(url_list) - 10} URL")

with col2:
    st.header("📊 Előző elemzések")
    
    # Korábbi jelentések listázása
    json_files = [f for f in os.listdir('.') if f.endswith('_report.json')]
    html_files = [f for f in os.listdir('.') if f.endswith('.html') and 'report' in f]
    
    if json_files:
        st.subheader("JSON jelentések:")
        for file in json_files[:5]:
            if st.button(f"📁 {file}", key=f"json_{file}"):
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                st.json(data)
    
    if html_files:
        st.subheader("HTML jelentések:")
        for file in html_files[:5]:
            st.markdown(f"📄 [{file}](./{file})")

# Elemzés indítása
st.header("🚀 Elemzés indítása")

if st.button("▶️ Elemzés kezdése", type="primary", disabled=not bool(url_list)):
    if not url_list:
        st.error("❌ Nem adtál meg URL-eket!")
    else:
        # Progress bar és status
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Időmérés kezdése
            start_time = time.time()
            
            status_text.text("🔍 Elemzés inicializálása...")
            progress_bar.progress(10)
            
            # Fájlnév generálás timestamp-pel
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            json_filename = f"geo_analysis_{timestamp}.json"
            html_filename = f"geo_report_{timestamp}.html"
            
            status_text.text("📊 URL-ek elemzése folyamatban...")
            progress_bar.progress(20)
            
            # Elemzés futtatása
            analyze_urls(
                url_list=url_list,
                api_key=api_key if not skip_pagespeed else None,
                output_file=json_filename,
                parallel=parallel_processing
            )
            
            progress_bar.progress(70)
            status_text.text("📋 HTML jelentés generálása...")
            
            # HTML jelentés
            generate_html_report(json_filename, html_filename)
            
            progress_bar.progress(90)
            status_text.text("📊 CSV export...")
            
            # CSV export
            csv_filename = f"geo_export_{timestamp}.csv"
            generate_csv_export(json_filename, csv_filename)
            
            progress_bar.progress(100)
            
            # Sikeres befejezés
            elapsed_time = time.time() - start_time
            status_text.text(f"✅ Elemzés befejezve! ({elapsed_time:.1f} másodperc)")
            
            # Eredmények megjelenítése
            st.success("🎉 Elemzés sikeres!")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                with open(json_filename, 'rb') as f:
                    st.download_button(
                        "📊 JSON letöltés",
                        f,
                        file_name=json_filename,
                        mime="application/json"
                    )
            
            with col2:
                with open(html_filename, 'rb') as f:
                    st.download_button(
                        "📄 HTML jelentés",
                        f,
                        file_name=html_filename,
                        mime="text/html"
                    )
            
            with col3:
                with open(csv_filename, 'rb') as f:
                    st.download_button(
                        "📈 CSV export",
                        f,
                        file_name=csv_filename,
                        mime="text/csv"
                    )
            
            # Összefoglaló megjelenítése
            with open(json_filename, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            st.header("📈 Összefoglaló")
            
            col1, col2, col3, col4 = st.columns(4)
            
            valid_results = [r for r in results if 'ai_readiness_score' in r]
            
            with col1:
                st.metric("Elemzett oldalak", len(results))
            
            with col2:
                if valid_results:
                    avg_score = sum(r['ai_readiness_score'] for r in valid_results) / len(valid_results)
                    st.metric("Átlagos AI Score", f"{avg_score:.1f}/100")
            
            with col3:
                excellent_count = sum(1 for r in valid_results if r['ai_readiness_score'] >= 70)
                st.metric("Kiváló oldalak", excellent_count)
            
            with col4:
                poor_count = sum(1 for r in valid_results if r['ai_readiness_score'] < 50)
                st.metric("Fejlesztendő", poor_count)
            
            # Részletes eredmények
            if valid_results:
                st.subheader("🏆 Legjobb eredmények")
                sorted_results = sorted(valid_results, key=lambda x: x['ai_readiness_score'], reverse=True)
                
                for i, result in enumerate(sorted_results[:5], 1):
                    score = result['ai_readiness_score']
                    url = result['url']
                    
                    # Szín a score alapján
                    if score >= 70:
                        color = "🟢"
                    elif score >= 50:
                        color = "🟡"
                    else:
                        color = "🔴"
                    
                    st.write(f"{color} **{i}.** {url} - **{score}/100**")
            
        except Exception as e:
            st.error(f"❌ Hiba történt az elemzés során: {str(e)}")
            status_text.text("❌ Elemzés megszakítva")

# Információs szekció
with st.expander("ℹ️ Információ a GEO Analyzer-ról"):
    st.markdown("""
    ### Mi az a GEO (Generative Engine Optimization)?
    
    A **Generative Engine Optimization** az AI-alapú keresőmotorok (mint ChatGPT, Bard, Claude) számára való optimalizálás.
    
    ### Mit ellenőriz az alkalmazás?
    
    ✅ **Technikai SEO**
    - Robots.txt és Sitemap
    - Meta title és description optimalizálása
    - Heading struktúra (H1-H6)
    - Mobile-friendly design
    
    ✅ **Strukturált adatok**
    - Schema.org markup
    - Open Graph meta tagek
    - Twitter Card támogatás
    
    ✅ **AI-readiness**
    - Tartalom strukturáltsága
    - Gépi olvashatóság
    - AI-barát formázás
    
    ✅ **Teljesítmény**
    - PageSpeed Insights pontszámok
    - Core Web Vitals metrikák
    
    ### Hogyan használd?
    
    1. Add meg az elemezni kívánt URL-eket
    2. Opcionálisan állítsd be a Google PageSpeed API kulcsot
    3. Indítsd el az elemzést
    4. Töltsd le a jelentéseket (JSON/HTML/CSV)
    
    ### API kulcs beszerzése
    
    A PageSpeed Insights API kulcshoz menj a [Google Cloud Console](https://console.cloud.google.com/)-ra és engedélyezd a PageSpeed Insights API-t.
    """)

# Footer
st.markdown("---")
st.markdown("🚀 **GEO Analyzer** | Készítette: Ecsedi Tamás | 2025")