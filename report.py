import json
import csv
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import html

# --------------------------------
# Súgó szövegek (Mit jelent melyik mutató?)
# --------------------------------

HELP_TEXTS = {
    # Főmutatók
    "ai_readiness_score": "Összesített 0–100 pontszám amely megmutatja mennyire alkalmas a tartalom AI platformoknak. Tartalmazza: meta adatok, schema markup, mobilbarátság, tartalom minőség, olvashatóság és AI-kompatibilitás mérését.",
    
    # Meta adatok
    "meta_title": "Title tag hossza és optimalizáltsága. Ideális hossz: 30-60 karakter. A title az egyik legfontosabb SEO és AI-readiness tényező.",
    "meta_description": "Meta description hossza és megléte. Ideális hossz: 120-160 karakter. Rövid összefoglaló a tartalom tartalmáról.",
    "meta_keywords": "Meta kulcsszavak jelenléte és relevanciája a tartalomhoz képest.",
    "og_tags": "Open Graph meta tag-ek jelenléte (og:title, og:description, og:image). Fontosak a közösségi média megosztásokhoz.",
    "twitter_card": "Twitter Card meta tag-ek jelenléte. Optimalizálja a Twitter-en való megjelenést.",
    
    # Technikai SEO
    "crawlability": "Robots.txt státusza, sitemap megléte, HTML méret (ideálisan <500KB). Meghatározza hogy a keresőmotorok mennyire könnyen tudják feldolgozni az oldalt.",
    "mobile_friendly": "Viewport meta tag, reszponzív képek és mobilbarát design megléte. Ma már alapvető követelmény.",
    "schema_markup": "Schema.org strukturált adatok típusai és száma. Segíti a keresőmotorokat és AI rendszereket a tartalom megértésében.",
    "google_validation": "Google strukturált adatok validátor eredménye. Ellenőrzi hogy a schema markup helyes-e.",
    
    # Tartalom minőség  
    "content_quality": "Tartalom mélysége, olvashatóság, kulcsszó sűrűség, szemantikai gazdagság összesített értékelése.",
    "readability": "Szöveg olvashatósága - mondathossz, szóhasználat komplexitása, bekezdések struktúrája.",
    "word_count": "Szavak száma a tartalomban. Hosszabb tartalmak általában jobban teljesítenek AI platformokon.",
    "headings_structure": "H1-H6 címsorok hierarchiája és eloszlása. Jól strukturált tartalom könnyebben feldolgozható.",
    
    # AI Enhanced mutatók
    "ai_content_evaluation": "Valós AI (OpenAI GPT) értékelés a tartalom minőségéről és AI-platformokhoz való alkalmasságról.",
    "ai_readability": "AI-alapú olvashatóság elemzés (OpenAI GPT). Clarity: világosság és érthetőség (0-100). Engagement: bevonó erő és érdekesség (0-100). Structure: logikai felépítés és szervezettség (0-100). AI Friendliness: mennyire könnyen dolgozható fel AI által (0-100).",
    "ai_factual_check": "AI-alapú faktualitás ellenőrzés (OpenAI GPT). Factual Score: összesített faktualitás pontszám (0-100). Citations: hivatkozások és források száma. Numbers with Units: számszerű adatok mértékegységekkel (megbízhatóság jele). Confidence: AI bizonyossági szint az értékelésben.",
    "platform_compatibility": "Platform kompatibilitás számítás: Főszám = Hybrid Score (hagyományos algoritmus + ML átlaga). AI Score = Valós AI értékelés (OpenAI GPT). Hybrid Score = (Hagyományos Score + ML Score) / 2. AI Enhanced esetén: Final Score = (40% hagyományos + 40% ML + 20% AI).",
    
    # Platform specifikus
    "chatgpt_score": "ChatGPT kompatibilitás számítás: lépésenkénti útmutatók (+15), listák (+10), gyakorlati példák (+15), Q&A formátum (+20), világos struktúra (+15). Hybrid = (Hagyományos + ML) / 2.",
    "claude_score": "Claude kompatibilitás számítás: részletes kontextus (+20), hivatkozások (+15), árnyalt magyarázatok (+15), szakmai terminológia (+10), hosszú forma tartalom (+15). Hybrid = (Hagyományos + ML) / 2.",
    "gemini_score": "Google Gemini kompatibilitás számítás: friss információk (+15), strukturált adatok (+20), multimédia támogatás (+10), schema markup (+15), mobile-friendly (+15). Hybrid = (Hagyományos + ML) / 2.",
    "bing_chat_score": "Bing Chat kompatibilitás számítás: külső források (+20), hivatkozások (+15), időszerű információk (+15), news tartalom (+10), fact-checking elemek (+15). Hybrid = (Hagyományos + ML) / 2.",
    
    # Teljesítmény
    "pagespeed_mobile": "PageSpeed Insights mobil teljesítmény pontszám (0-100). A gyors betöltés javítja a felhasználói élményt.",
    "pagespeed_desktop": "PageSpeed Insights asztali teljesítmény pontszám (0-100).",
    "core_web_vitals": "Google Core Web Vitals mutatók: LCP (betöltés), FID (interaktivitás), CLS (vizuális stabilitás).",
    "lcp": "Largest Contentful Paint - A legnagyobb tartalom elem betöltési ideje. Ideális: <2.5s, Javítandó: 2.5-4s, Gyenge: >4s",
    "fid": "First Input Delay - Az első felhasználói interakció késleltetése. Ideális: <100ms, Javítandó: 100-300ms, Gyenge: >300ms", 
    "cls": "Cumulative Layout Shift - Vizuális stabilitás mérése. Ideális: <0.1, Javítandó: 0.1-0.25, Gyenge: >0.25",
    "pagespeed_performance": "PageSpeed Insights teljesítmény pontszám. 90-100: Jó, 50-89: Javítandó, 0-49: Gyenge",
    "pagespeed_seo": "PageSpeed Insights SEO pontszám. A technikai SEO tényezők értékelése.",
    
    # AI Összefoglaló
    "ai_summary": "OpenAI GPT-4 által generált intelligens összefoglaló az elemzési eredményekről. Átfogó értékelés és konkrét fejlesztési javaslatok.",
    "ai_recommendations": "OpenAI GPT-4 által készített konkrét, végrehajtható javaslatok a GEO (Generative Engine Optimization) eredmények javítására.",
    
    # Fejlett mutatók
    "weighted_average": "AI-metrikák súlyozott átlaga. Nem azonos az AI Readiness-szel, de jól jelzi az AI-barát tartalom minőségét.",
    "enhancement_status": "Enhanced vs Standard elemzés státusza. Enhanced verzió valós AI értékelést tartalmaz.",
    "cache_status": "Cache találat információ - ha az eredmény cache-ből származik, gyorsabb de esetleg nem a legfrissebb.",
    
    # AI metrikák részletes
    "ai_summary_score": "Összesített AI-readiness pontszám 0-100 skálán. Az összes AI-specifikus mutató súlyozott átlaga.",
    "ai_level": "AI-readiness minősítési szint: Fejlesztendő (0-40), Közepes (40-60), Jó (60-80), Kiváló (80-100).",
    "structure": "Tartalom strukturáltsága: listák, táblázatok, bekezdések, címsorok hierarchiája. Jól strukturált tartalom könnyebben feldolgozható AI számára.",
    "qa_format": "Kérdés-válasz formátum jelenléte. AI platformok preferálják a Q&A struktúrájú tartalmat, mivel könnyen feldolgozható.",
    "entities": "Entitások és szemantikai jelölések (schema markup, személyek, helyek, szervezetek). Segítik az AI-t a tartalom megértésében.",
    "freshness": "Tartalom frissessége: dátum információk, aktuális események, időbélyegek. Friss tartalom magasabb prioritást kap.",
    "citations": "Hivatkozások és források jelenléte. AI platformok előnyben részesítik a megalapozott, hivatkozásokkal támogatott tartalmat.",
    "formatting": "AI-barát formázás: jól olvasható struktúra, világos bekezdések, megfelelő sortörések és kiemelések.",
    "depth": "Tudás mélység: részletesség, példák száma, téma lefedettség. Mélyebb tartalom több értéket nyújt AI felhasználóknak.",
    "conversational": "Beszélgetés-szerű elemek: kérdések, közvetlenség, interaktív stílus. AI chatbotok számára természetesebb a párbeszédes forma.",
    
    # Schema Enhanced metrikák
    "schema_enhanced": "Fejlett schema elemzés állapota. Enhanced verzió Google validátort és hatékonyság mérést is tartalmaz.",
    "google_validation": "Google strukturált adatok validátor eredménye. Rich Results: jogosult-e a gazdagított keresési eredményekre (csillagok, képek, árak stb.). Schema Count: hány darab schema markup elem található az oldalon. Valid: megfelelnek-e a Google irányelveknek.",
    "rich_results": "Rich Results jogosultság: Az oldal schema markup-ja megfelel-e a Google követelményeinek ahhoz, hogy gazdagított keresési eredményként jelenjen meg (csillagos értékelések, képek, árak, FAQ-k stb.).",
    "schema_count": "Schema elemek száma: Hány darab strukturált adat (JSON-LD, Microdata, RDFa) található az oldalon. Több schema elem jobb lefedettséget biztosít.",
    "schema_recommendations": "Schema markup fejlesztési javaslatok. Konkrét lépések a strukturált adatok optimalizálásához.",
    "schema_effectiveness": "Schema markup hatékonysági elemzés. Effectiveness Score: összesített hatékonyság pontszám (0-100). AI Understanding: mennyivel javítja az AI megértést a schema markup (0-100). CTR Impact: becsült kattintási arány javulás százalékban (+X%).",
    
    # Tartalom metrikák
    "keyword_analysis": "Kulcsszó használat elemzése: szókincs gazdagság, kulcsszó sűrűség, releváns kifejezések azonosítása.",
    "content_depth": "Tartalom mélységi elemzése: téma lefedettség, példák száma, részletezettség, statisztikák és adatok megléte.",
    "authority_signals": "Tekintélyi jelzők: hivatkozások, forrásanyagok, szakértői tartalom, megbízhatósági mutatók.",
    "semantic_richness": "Szemantikai gazdagság: entitások, kapcsolatok, témakörök szélessége, kontextuális információk.",
    
    # Hibaüzenetek és státuszok
    "error_status": "Hiba történt az elemzés során. Részletek a hibaüzenetben.",
    "analysis_method": "Milyen módszerrel történt az elemzés: valós AI API vagy heurisztikus fallback."
}

def help_icon(key: str) -> str:
    """Súgó ikon generálása tooltip-pel"""
    help_text = HELP_TEXTS.get(key, "")
    if not help_text:
        return ""
    
    escaped_text = html.escape(help_text)
    return f'<span class="help-icon ms-1" data-bs-toggle="tooltip" data-bs-placement="top" title="{escaped_text}">❓</span>'

# Helper függvények
def level_from_score(score: float) -> str:
    """AI Readiness szint meghatározása pontszám alapján"""
    if score is None: 
        return "Ismeretlen"
    if score >= 85: return "Kiváló"
    if score >= 60: return "Jó"
    if score >= 40: return "Közepes"
    return "Fejlesztendő"

def badge_class(score: float) -> str:
    """CSS osztály meghatározása pontszám alapján"""
    if score is None: 
        return "score-average"
    if score >= 85: return "score-excellent"
    if score >= 60: return "score-good"
    if score >= 40: return "score-average"
    return "score-poor"

def fmt(x, digits=1):
    """Biztonságos formázás"""
    try:
        return f"{float(x):.{digits}f}"
    except Exception:
        return "—"

def detect_enhanced_analysis(data: List[Dict]) -> Dict:
    """Automatikus enhanced vs standard felismerés"""
    if not data:
        return {"is_enhanced": False, "enhancement_stats": {}}
    
    valid_results = [r for r in data if isinstance(r, dict) and 'ai_readiness_score' in r and 'error' not in r]
    
    # Enhanced jellemzők keresése
    ai_enhanced_count = len([r for r in valid_results if r.get('ai_content_evaluation')])
    schema_enhanced_count = len([r for r in valid_results if r.get('schema', {}).get('validation_status') == 'enhanced'])
    cached_count = len([r for r in valid_results if r.get('cached')])
    
    # Enhanced akkor, ha legalább 1 AI evaluation vagy enhanced schema van
    is_enhanced = ai_enhanced_count > 0 or schema_enhanced_count > 0
    
    enhancement_stats = {
        "ai_enhanced_count": ai_enhanced_count,
        "ai_enhanced_percentage": round((ai_enhanced_count / len(valid_results)) * 100, 1) if valid_results else 0,
        "schema_enhanced_count": schema_enhanced_count,
        "schema_enhanced_percentage": round((schema_enhanced_count / len(valid_results)) * 100, 1) if valid_results else 0,
        "cached_count": cached_count,
        "cache_hit_rate": round((cached_count / len(valid_results)) * 100, 1) if valid_results else 0,
        "total_enhanced": ai_enhanced_count + schema_enhanced_count,
        "enhancement_adoption": round(((ai_enhanced_count + schema_enhanced_count) / (len(valid_results) * 2)) * 100, 1) if valid_results else 0
    }
    
    return {
        "is_enhanced": is_enhanced,
        "enhancement_stats": enhancement_stats
    }

def generate_html_report(json_file: str = "ai_readiness_full_report.json", 
                        output_file: str = "report.html") -> None:
    """
    Enhanced HTML jelentés generálása - automatikus enhanced/standard felismeréssel
    """
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Hiba: {json_file} nem található!")
        return
    except json.JSONDecodeError:
        print(f"❌ Hiba: {json_file} nem érvényes JSON!")
        return

    # Enhanced analysis detektálása
    # Ha a data dict és tartalmaz results kulcsot, akkor azt használjuk
    if isinstance(data, dict) and 'results' in data:
        results_data = data['results']
    elif isinstance(data, list):
        results_data = data
    else:
        results_data = [data] if isinstance(data, dict) else []
        
    detection_result = detect_enhanced_analysis(results_data)
    is_enhanced = detection_result["is_enhanced"]
    enhancement_stats = detection_result["enhancement_stats"]
    
    # Valid results
    valid_results = [r for r in results_data if isinstance(r, dict) and 'ai_readiness_score' in r and 'error' not in r]
    avg_score = sum(r['ai_readiness_score'] for r in valid_results) / len(valid_results) if valid_results else 0
    
    # Report címek és stílus
    report_title = "🚀 GEOcheck 🚀"
    primary_color = "#667eea" if is_enhanced else "#4facfe"
    secondary_color = "#764ba2" if is_enhanced else "#00f2fe"
    
    # HTML template
    html_content = f"""
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_title} - {datetime.now().strftime('%Y-%m-%d')}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%);
            background-attachment: fixed;
            background-size: 100% 100%;
            background-repeat: no-repeat;
            min-height: 100vh;
            height: 100%;
            padding-left: 10%;
            padding-right: 10%;
            padding-top: 20px;
            padding-bottom: 20px;
        }}

        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            width: 100vw;
            height: 100vh;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
            background-attachment: fixed;
            background-size: 60px 60px;
            pointer-events: none;
            z-index: 0;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            max-width: 1200px; /* vagy ugyanaz, mint a container */
            margin: 0 auto 30px auto; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            {f'border-left: 5px solid {secondary_color};' if is_enhanced else ''}
        }}
        
        h1 {{
            color: #333;
            font-size: 3.5rem;
            font-weight: bold;
            margin-bottom: 20px;
        }}
        
        .enhanced-badge {{
            background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-block;
            margin-left: 10px;
            position: relative;
        }}
        
        .enhanced-badge::before {{
            content: "🤖";
            margin-right: 5px;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .summary-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }}
        
        .summary-card.enhanced {{
            background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%);
            color: white;
        }}
        
        .summary-card .value {{
            font-size: 2rem;
            font-weight: 700;
            color: {primary_color};
        }}
        
        .summary-card.enhanced .value {{
            color: white;
        }}
        
        .summary-card .label {{
            font-size: 0.9rem;
            color: #666;
            margin-top: 5px;
        }}
        
        .summary-card.enhanced .label {{
            color: rgba(255,255,255,0.9);
        }}
        
        .site-card {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            {f'border-left: 5px solid {secondary_color};' if is_enhanced else ''}
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        

        
        .site-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .site-url {{
            font-size: 1.5rem;
            font-weight: 600;
            color: #333;
        }}
        
        .enhancement-badges {{
            display: flex;
            gap: 8px;
            margin: 10px 0;
            flex-wrap: wrap;
        }}
        
        .enhancement-badge {{
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        
        .badge-ai {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .badge-schema {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }}
        
        .badge-cache {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }}
        
        .score-badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 80px;
            height: 80px;
            border-radius: 50%;
            font-size: 1.5rem;
            font-weight: 700;
            color: white;
            position: relative;
        }}
        
        .score-excellent {{ 
            background: linear-gradient(135deg, #00c851 0%, #00a846 100%); 
            box-shadow: 0 8px 25px rgba(0, 200, 81, 0.3);
        }}
        .score-good {{ 
            background: linear-gradient(135deg, #4caf50 0%, #45a049 100%); 
            box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3);
        }}
        .score-average {{ 
            background: linear-gradient(135deg, #ffc107 0%, #e0a800 100%); 
            box-shadow: 0 8px 25px rgba(255, 193, 7, 0.3);
        }}
        .score-poor {{ 
            background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%); 
            box-shadow: 0 8px 25px rgba(255, 68, 68, 0.3);
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .metric-item {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid {primary_color};
            transition: transform 0.2s;
        }}
        
        .metric-item:hover {{
            transform: translateY(-2px);
        }}
        
        .metric-item.ai-enhanced {{
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            border-left-color: #ff6b6b;
        }}
        
        /* AI Összefoglaló speciális stílusok */
        .ai-summary-card {{
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-left-color: #2196f3;
            grid-column: 1 / -1; /* Teljes szélesség */
        }}
        
        .ai-recommendations-card {{
            background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
            border-left-color: #9c27b0;
            grid-column: 1 / -1; /* Teljes szélesség */
        }}
        
        .ai-summary-content, .ai-recommendations-content {{
            line-height: 1.6;
            max-height: 300px;
            overflow-y: auto;
            padding-right: 10px;
        }}
        
        .ai-summary-content::-webkit-scrollbar, .ai-recommendations-content::-webkit-scrollbar {{
            width: 6px;
        }}
        
        .ai-summary-content::-webkit-scrollbar-thumb, .ai-recommendations-content::-webkit-scrollbar-thumb {{
            background: rgba(0,0,0,0.2);
            border-radius: 3px;
        }}
        
        .metric-title {{
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .metric-value {{
            color: #666;
            font-size: 0.9rem;
            line-height: 1.5;
        }}
        
        /* Súgó tooltip stílusok */
        .help-icon {{
            cursor: help;
            color: #6c757d;
            font-size: 0.8rem;
            opacity: 0.7;
            transition: opacity 0.2s;
        }}
        
        .help-icon:hover {{
            opacity: 1;
            color: {primary_color};
        }}
        
        /* Bootstrap tooltip testreszabás */
        .tooltip {{
            font-size: 0.8rem;
        }}
        
        .tooltip-inner {{
            max-width: 300px;
            text-align: left;
            background-color: #333;
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
        }}
        
        .platform-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .platform-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .platform-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        }}
        
        .platform-card.ai-enhanced {{
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        }}
        
        .platform-name {{
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .platform-score {{
            font-size: 2rem;
            font-weight: 700;
            color: {primary_color};
        }}
        
        .platform-level {{
            font-size: 0.8rem;
            color: #666;
            margin-top: 5px;
        }}
        
        .ai-scores {{
            background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }}
        
        .ai-score-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .ai-score-item {{
            text-align: center;
            background: rgba(255,255,255,0.15);
            padding: 15px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }}
        
        .ai-score-value {{
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        
        .ai-score-label {{
            font-size: 0.8rem;
            opacity: 0.9;
        }}
        
        .chart-container {{
            width: 100%;
            max-width: 500px;
            margin: 20px auto;
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .charts-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin: 30px 0;
        }}
        
        .tabs {{
            display: flex;
            gap: 2px;
            margin: 20px 0;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 0;
            flex-wrap: wrap;
        }}
        
        .tab {{
            padding: 8px 12px;
            background: none;
            border: none;
            cursor: pointer;
            font-weight: 600;
            color: #666;
            transition: all 0.3s;
            border-radius: 8px 8px 0 0;
            white-space: nowrap;
            font-size: 0.85rem;
            flex-shrink: 0;
        }}
        
        .tab:hover {{
            background: rgba(102, 126, 234, 0.1);
            color: {primary_color};
        }}
        
        .tab.active {{
            color: {primary_color};
            background: {primary_color};
            background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%);
            color: white;
        }}
        
        .tab-content {{
            display: none;
            padding: 20px 0;
            animation: fadeIn 0.3s ease-in;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        th {{
            background: {primary_color};
            color: white;
            font-weight: 600;
        }}
        
        .check-icon {{ color: #00c851; font-weight: bold; }}
        .cross-icon {{ color: #ff4444; font-weight: bold; }}
        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 50px;
            padding: 20px;
        }}
        
        .alert-box {{
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid;
        }}
        
        .alert-critical {{
            background: #f8d7da;
            border-color: #dc3545;
            color: #721c24;
        }}
        
        .alert-info {{
            background: #d1ecf1;
            border-color: #17a2b8;
            color: #0c5460;
        }}
        
        .alert-warning {{
            background: #fff3cd;
            border-color: #ffc107;
            color: #856404;
        }}
        
        .alert-success {{
            background: #d4edda;
            border-color: #28a745;
            color: #155724;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, {primary_color} 0%, {secondary_color} 100%);
            transition: width 0.3s;
        }}
        
        .ai-metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin: 15px 0;
        }}
        
        .ai-metric {{
            background: #fff;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e0e0e0;
            transition: transform 0.2s;
        }}
        
        .ai-metric:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .ai-metric-label {{
            font-size: 0.8rem;
            color: #666;
            margin-bottom: 5px;
        }}
        
        .ai-metric-value {{
            font-size: 1.4rem;
            font-weight: 600;
            color: #333;
        }}
        
        .fix-item {{
            background: #ffffff;
            padding: 20px;
            margin: 20px 0;
            border-radius: 12px;
            border-left: 4px solid {primary_color};
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .fix-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        }}
        
        .fix-title {{
            font-weight: 700;
            color: #333;
            margin-bottom: 12px;
            font-size: 1.1rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .fix-description {{
            color: #666;
            margin-bottom: 15px;
            font-size: 0.95rem;
            line-height: 1.5;
        }}
        
        .fix-code {{
            background: #2d3748;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 8px;
            font-family: 'SF Mono', 'Monaco', 'Consolas', 'Courier New', monospace;
            font-size: 0.9rem;
            margin: 15px 0;
            overflow-x: auto;
            border: 1px solid #4a5568;
            position: relative;
        }}
        
        .fix-code::before {{
            content: "CODE";
            position: absolute;
            top: -8px;
            right: 10px;
            background: {primary_color};
            color: white;
            font-size: 0.7rem;
            padding: 2px 8px;
            border-radius: 4px;
            font-family: 'Inter', sans-serif;
        }}
        
        .fix-time {{
            color: {primary_color};
            font-weight: 600;
            font-size: 0.9rem;
            margin-top: 10px;
        }}

        header {{
            background: linear-gradient(120deg, #f8f8f8 65%, #fbc2eb 100%);
            text-align: center;
            }}

        .card-bg {{
            background: linear-gradient(120deg, #f8f8f8 70%, #fbc2eb 100%);
            }}

        header, .site-card {{
            width: 100%;
            max-width: 1200px; /* vagy ugyanaz, mint a container */
            margin: 0 auto 30px auto; 
        }}
        
        details {{
            margin: 15px 0;
        }}
        
        summary {{
            cursor: pointer;
            font-weight: 600;
            color: {primary_color};
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
            transition: background 0.2s;
        }}
        
        summary:hover {{
            background: #e9ecef;
        }}
        
        @media (max-width: 768px) {{
            h1 {{ font-size: 1.8rem; }}
            .site-url {{ font-size: 1.2rem; }}
            .charts-row {{ grid-template-columns: 1fr; }}
            .metrics-grid {{ grid-template-columns: 1fr; }}
            .platform-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .tabs {{ justify-content: flex-start; gap: 1px; }}
            .tab {{ padding: 6px 8px; font-size: 0.8rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{report_title}</h1>
            <p style="color: #666;">
                Generative Engine Optimization elemzés - {datetime.now().strftime('%Y. %m. %d. %H:%M')}
                {f'<span class="enhanced-badge">OpenAI által ellenőrzött</span>' if is_enhanced else ''}
            </p>
            
            
            </div>
        </header>
"""

    # Minden oldal feldolgozása
    for idx, site in enumerate(results_data):
        if not isinstance(site, dict):
            continue
            
        url = site.get("url", "N/A")
        score = site.get("ai_readiness_score", 0)
        uid = f"site_{idx}_{re.sub(r'[^a-zA-Z0-9]', '_', url)}"
        
        # Enhanced jelzők
        has_ai_eval = bool(site.get('ai_content_evaluation'))
        has_schema_enhanced = site.get('schema', {}).get('validation_status') == 'enhanced'
        was_cached = site.get('cached', False)
        
        # Score szín meghatározása
        score_class = badge_class(score)
        
        # Adatok kinyerése
        meta_data = site.get("meta_and_headings", {})
        schema_data = site.get("schema", {})
        mobile = site.get("mobile_friendly", {})
        psi = site.get("pagespeed_insights", {})
        ai_metrics = site.get("ai_metrics", {})
        ai_summary = site.get("ai_metrics_summary", {})
        content_quality = site.get("content_quality", {})
        platform_analysis = site.get("platform_analysis", {})
        platform_suggestions = site.get("platform_suggestions", {})
        auto_fixes = site.get("auto_fixes", {})
        
        # Enhanced adatok
        ai_content_eval = site.get("ai_content_evaluation", {})
        ai_readability = site.get("ai_readability", {})
        ai_factual = site.get("ai_factual_check", {})
        
        html_content += f"""
        <div class="site-card card-bg">
            <div class="site-header">
                <div>
                    <div class="site-url">{html.escape(url)} URL elemzése</div>
                    <div class="enhancement-badges">"""
        
        # Enhancement badges
        if has_ai_eval:
            html_content += '<span class="enhancement-badge badge-ai">🤖 AI & ML ellenőrzés</span>'
        if has_schema_enhanced:
            html_content += f'<span class="enhancement-badge badge-schema" title="{html.escape(HELP_TEXTS.get("schema_enhanced", ""))}">🏗️ Schema & Google validálás</span>'
        if was_cached:
            html_content += '<span class="enhancement-badge badge-cache">💾 Cached</span>'
            
        html_content += f"""
                    </div>
                </div>
                <div class="score-badge {score_class}">{fmt(score, 0)}{help_icon("ai_readiness_score")}</div>
            </div>
            
            <!-- Tab navigáció -->
            <div class="tabs">
                <button class="tab active" onclick="showTab(event, '{uid}', 'ai-summary')" title="OpenAI GPT-4 által készített intelligens összefoglaló és javaslatok">🧠 AI Összefoglaló</button>
                <button class="tab" onclick="showTab(event, '{uid}', 'overview')" title="URL site és html adatok ellenőrzése">📊 HTML adatok</button>
                <button class="tab" onclick="showTab(event, '{uid}', 'ai-metrics')" title="URL tartalmának AI metrikai mérése ">🤖 AI Metrikák</button>"""
        
        # Enhanced tabok hozzáadása
        if has_ai_eval:
            html_content += f'\n                <button class="tab" onclick="showTab(event, \'{uid}\', \'ai-enhanced\')" title="URL szöveges tartalomának AI olvashatósági elemzése">🚀 AI Olvashatóság</button>'
        if has_schema_enhanced:
            html_content += f'\n                <button class="tab" onclick="showTab(event, \'{uid}\', \'schema-enhanced\')" title="Fejlett Schema validálás, Google elemzés és hatékonyság mérés">🏗️ Schema validálás</button>'
            
        html_content += f"""
                <button class="tab" onclick="showTab(event, '{uid}', 'content')" title="URL szöveges tartalomának AI technikai elemzése">📝 AI Tartalom</button>
                <button class="tab" onclick="showTab(event, '{uid}', 'platforms')" title="URL platform AI elemzése">🎯 AI Platformok</button>
                <button class="tab" onclick="showTab(event, '{uid}', 'pagespeed')" title="Összetett Google speed teszt">⚡ Pagespeed</button>
                <button class="tab" onclick="showTab(event, '{uid}', 'fixes')" title="URL javítások és javaslatok">🔧 Javítások</button>
            </div>
            
            <!-- AI Összefoglaló tab -->
            <div id="{uid}-ai-summary" class="tab-content active">
                <div class="metrics-grid">
"""

        # AI összefoglaló generálása
        summary = "Az AI összefoglaló még nincs generálva. Kattints a 'Frissítés' gombra az AI elemzéshez."
        recommendations = "Az AI javaslatok még nincsenek elkészítve. Az AI összefoglaló generálása után itt jelennek meg a konkrét fejlesztési javaslatok."
        
        # Opcionálisan próbáljuk meg generálni (csak ha van API kulcs)
        try:
            import os
            force_generation = os.getenv("FORCE_AI_GENERATION") == "1"
            
            if (os.getenv("OPENAI_API_KEY") and 
                (force_generation or not json_file.startswith('test_'))):
                from ai_summary import generate_ai_summary_from_file
                summary, recommendations = generate_ai_summary_from_file(json_file)
        except Exception as e:
            # Ha hiba van, marad az alapértelmezett szöveg
            if force_generation:
                summary = f"Hiba az AI összefoglaló generálása során: {str(e)}"
                recommendations = "Az AI javaslatok generálása sikertelen volt."
        
        html_content += f"""
                    <div class="metric-item ai-summary-card">
                        <div class="metric-title">
                            📝 AI Összefoglaló{help_icon("ai_summary")}                            
                        </div>
                        <div class="metric-value ai-summary-content" id="ai-summary-content-{uid}">
                            {html.escape(summary).replace(chr(10), '<br>')}
                        </div>
                    </div>
                    
                    <div class="metric-item ai-recommendations-card">
                        <div class="metric-title">💡 AI Javaslatok{help_icon("ai_recommendations")}</div>
                        <div class="metric-value ai-recommendations-content" id="ai-recommendations-content-{uid}">
                            {html.escape(recommendations).replace(chr(10), '<br>')}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Áttekintés tab -->
            <div id="{uid}-overview" class="tab-content">
                <div class="metrics-grid">
                    <div class="metric-item">
                        <div class="metric-title">📄 Meta adatok{help_icon("meta_title")}</div>
                        <div class="metric-value">
"""
        
        # Meta adatok megjelenítése
        title = meta_data.get("title")
        description = meta_data.get("description")
        title_len = len(title) if title else 0
        desc_len = len(description) if description else 0
        title_status = "✅" if meta_data.get("title_optimal") else ("⚠️" if title_len > 0 else "❌")
        desc_status = "✅" if meta_data.get("description_optimal") else ("⚠️" if desc_len > 0 else "❌")
        
        html_content += f"""
                            Title: {title_status} {title_len} karakter<br>
                            Description: {desc_status} {desc_len} karakter<br>
                            OG Tags: {"✅" if meta_data.get('has_og_tags') else "❌"}<br>
                            Twitter Card: {"✅" if meta_data.get('has_twitter_card') else "❌"}
                        </div>
                    </div>
                    
                    <div class="metric-item">
                        <div class="metric-title">🤖 Crawlability{help_icon("crawlability")}</div>
                        <div class="metric-value">
                            Robots.txt: {"✅ Engedélyezett" if site.get('robots_txt', {}).get('can_fetch') else "❌ Tiltott"}<br>
                            Sitemap: {"✅ Van" if site.get('sitemap', {}).get('exists') else "❌ Nincs"}<br>
                            HTML méret: {fmt(site.get('html_size_kb', 0), 1)} KB
                        </div>
                    </div>
                    
                    <div class="metric-item">
                        <div class="metric-title">📱 Mobile-friendly{help_icon("mobile_friendly")}</div>
                        <div class="metric-value">
                            Viewport: {"✅" if mobile.get('has_viewport') else "❌"}<br>
                            Responsive képek: {"✅" if mobile.get('responsive_images') else "❌"}
                        </div>
                    </div>
                    
                    <div class="metric-item {'ai-enhanced' if has_schema_enhanced else ''}">
                        <div class="metric-title">🏗️ Struktúra {'(Enhanced)' if has_schema_enhanced else ''}{help_icon("schema_markup")}</div>
                        <div class="metric-value">
                            H1 elemek: {meta_data.get('h1_count', 0)}<br>
                            Heading hierarchia: {"✅" if meta_data.get('heading_hierarchy_valid') else "⚠️"}<br>
                            Schema elemek: {schema_data.get('count', 0)}<br>"""
        
        # Enhanced schema info
        if has_schema_enhanced:
            schema_score = schema_data.get('schema_completeness_score', 0)
            google_validation = schema_data.get('google_validation', {})
            html_content += f"""
                            Schema Completeness: {fmt(schema_score, 1)}/100<br>
                            Google Validation: {"✅" if google_validation.get('is_valid') else "❌"}"""
        
        html_content += """
                        </div>
                    </div>
                </div>
"""
        
        # Charts
        html_content += f"""
                <div class="charts-row">
                    <div class="chart-container">
                        <canvas id="headingChart_{uid}"></canvas>
                    </div>
                    <div class="chart-container">
                        <canvas id="schemaChart_{uid}"></canvas>
                    </div>
                </div>
            </div>
"""
        
        # AI Enhanced tab (ha van)
        if has_ai_eval and ai_content_eval:
            html_content += f"""
            <!-- AI Enhanced tab -->
            <div id="{uid}-ai-enhanced" class="tab-content">
                <h3>🚀 AI-alapú tartalom értékelés</h3>
                
                <div class="metrics-grid">
                    <div class="metric-item ai-enhanced">
                        <div class="metric-title">🎯 AI Pontszámok{help_icon("ai_content_evaluation")}</div>
                        <div class="metric-value">
                            Overall AI Score: {fmt(ai_content_eval.get('overall_ai_score', 0), 0)}/100<br>"""
            
            ai_platform_scores = ai_content_eval.get('ai_quality_scores', {})
            for platform, score in ai_platform_scores.items():
                html_content += f"                            {platform.title()}: {fmt(score, 0)}/100<br>"
            
            html_content += """
                        </div>
                    </div>"""
            
            # AI Readability ha van
            if ai_readability and not ai_readability.get('error'):
                html_content += f"""
                    <div class="metric-item ai-enhanced">
                        <div class="metric-title">📖 AI Olvashatóság{help_icon("ai_readability")}</div>
                        <div class="metric-value">
                            Clarity: {fmt(ai_readability.get('clarity_score', 0), 0)}/100<br>
                            Engagement: {fmt(ai_readability.get('engagement_score', 0), 0)}/100<br>
                            Structure: {fmt(ai_readability.get('structure_score', 0), 0)}/100<br>
                            AI Friendliness: {fmt(ai_readability.get('ai_friendliness', 0), 0)}/100
                        </div>
                    </div>"""
            
            # AI Factual Check ha van
            if ai_factual and not ai_factual.get('error'):
                html_content += f"""
                    <div class="metric-item ai-enhanced">
                        <div class="metric-title">✅ Faktualitás{help_icon("ai_factual_check")}</div>
                        <div class="metric-value">
                            Factual Score: {fmt(ai_factual.get('factual_score', 0), 0)}/100<br>
                            Citations: {ai_factual.get('accuracy_indicators', {}).get('citations_present', 0)}<br>
                            Numbers with Units: {ai_factual.get('accuracy_indicators', {}).get('numbers_with_units', 0)}<br>
                            Confidence: {ai_factual.get('confidence_level', 'N/A')}
                        </div>
                    </div>"""
            
            html_content += "</div>"
            
            # AI javaslatok
            ai_recommendations = ai_content_eval.get('ai_recommendations', [])
            if ai_recommendations:
                html_content += "<h4>💡 AI Javaslatok:</h4><ul>"
                for rec in ai_recommendations:
                    html_content += f"<li>{html.escape(str(rec))}</li>"
                html_content += "</ul>"
            
            html_content += "</div>"
        
        # Schema Enhanced tab (ha van)
        if has_schema_enhanced:
            html_content += f"""
            <!-- Schema Enhanced tab -->
            <div id="{uid}-schema-enhanced" class="tab-content">
                <h3>🏗️ Enhanced Schema Validáció</h3>
                
                <div class="metrics-grid">"""
            
            google_validation = schema_data.get('google_validation', {})
            if google_validation:
                html_content += f"""
                    <div class="metric-item ai-enhanced">
                        <div class="metric-title">🔍 Google Validation{help_icon("google_validation")}</div>
                        <div class="metric-value">
                            Valid: {"✅" if google_validation.get('is_valid') else "❌"}<br>
                            Overall Score: {fmt(google_validation.get('overall_score', 0), 0)}/100<br>
                            Rich Results: {"✅" if google_validation.get('rich_results_eligible') else "❌"}<br>
                            Schema Count: {google_validation.get('schema_count', 0)}
                        </div>
                    </div>"""
            
            # Schema ajánlások
            recommendations = schema_data.get('recommendations', [])
            if recommendations:
                html_content += f"""
                    <div class="metric-item ai-enhanced">
                        <div class="metric-title">💡 Schema Ajánlások{help_icon("schema_recommendations")}</div>
                        <div class="metric-value">
                            Ajánlások száma: {len(recommendations)}<br>"""
                
                for rec in recommendations[:3]:
                    if isinstance(rec, dict):
                        html_content += f"                            • {rec.get('schema_type', 'N/A')} ({rec.get('priority', 'medium')} prioritás)<br>"
                
                html_content += """
                        </div>
                    </div>"""
            
            # Effectiveness eredmények
            effectiveness = schema_data.get('effectiveness_analysis')
            if effectiveness and isinstance(effectiveness, dict):
                html_content += f"""
                    <div class="metric-item ai-enhanced">
                        <div class="metric-title">📈 Schema Effectiveness{help_icon("schema_effectiveness")}</div>
                        <div class="metric-value">
                            Effectiveness Score: {fmt(effectiveness.get('effectiveness_score', 0), 0)}/100<br>
                            AI Understanding: {fmt(effectiveness.get('ai_understanding_improvement', 0), 0)}/100<br>
                            CTR Impact: +{fmt(effectiveness.get('ctr_impact_estimate', 0), 1)}%
                        </div>
                    </div>"""
            
            html_content += "</div></div>"
        
        # AI Metrikák tab (meglévő logika megtartva, de enhanced)
        html_content += f"""
            <!-- AI Metrikák tab -->
            <div id="{uid}-ai-metrics" class="tab-content">
"""
        
        if ai_summary and not ai_summary.get('error'):
            weighted_avg = ai_summary.get("weighted_average")
            
            html_content += f"""
                <h3>AI Readiness Összefoglaló</h3>
                <div class="ai-metrics-grid">
                    <div class="ai-metric">
                        <div class="ai-metric-label">Összesített{help_icon("ai_summary_score")}</div>
                        <div class="ai-metric-value">{fmt(score, 0)}</div>
                    </div>
                    <div class="ai-metric">
                        <div class="ai-metric-label">Szint{help_icon("ai_level")}</div>
                        <div class="ai-metric-value">{level_from_score(score)}</div>
                    </div>
                    <div class="ai-metric">
                        <div class="ai-metric-label">AI Weighted{help_icon("weighted_average")}</div>
                        <div class="ai-metric-value">{fmt(weighted_avg, 0)}</div>
                    </div>
                </div>
                
                <h4>Részletes pontszámok:</h4>
                <div class="ai-metrics-grid">
"""
            scores = ai_summary.get('individual_scores', {})
            
            # AI metrikák megjelenítése tooltip-ekkel
            ai_metric_labels = {
                "structure": "Structure",
                "qa_format": "Q&A Format", 
                "entities": "Entities",
                "freshness": "Freshness",
                "citations": "Citations",
                "formatting": "Formatting",
                "depth": "Depth",
                "conversational": "Conversational"
            }
            
            for key, value in scores.items():
                display_label = ai_metric_labels.get(key, key.replace('_', ' ').title())
                html_content += f"""
                    <div class="ai-metric">
                        <div class="ai-metric-label">{display_label}{help_icon(key)}</div>
                        <div class="ai-metric-value">{fmt(value, 0)}</div>
                    </div>
"""
            html_content += "</div>"
        else:
            html_content += "<p>AI metrikák nem elérhetők</p>"
            
        html_content += "</div>"
        
        # Tartalom tab - részletes tartalom minőségi elemzés
        html_content += f"""
            <!-- Tartalom tab -->
            <div id="{uid}-content" class="tab-content">
                <h3>📝 Tartalom minőség</h3>
                <div class="metrics-grid">"""
        
        # Content Quality adatok megjelenítése
        if content_quality:
            readability = content_quality.get('readability', {})
            keyword_analysis = content_quality.get('keyword_analysis', {})
            content_depth = content_quality.get('content_depth', {})
            authority_signals = content_quality.get('authority_signals', {})
            semantic_richness = content_quality.get('semantic_richness', {})
            
            html_content += f"""
                    <div class="metric-item">
                        <div class="metric-title">📖 Olvashatóság{help_icon("readability")}</div>
                        <div class="metric-value">
                            Szó szám: {readability.get('word_count', 0)}<br>
                            Mondatok: {readability.get('sentence_count', 0)}<br>
                            Átlag mondat hossz: {fmt(readability.get('avg_sentence_length', 0), 1)}<br>
                            Flesch pontszám: {readability.get('flesch_score', 0)}<br>
                            Szint: {readability.get('readability_level', 'N/A')}<br>
                            Pontszám: {fmt(readability.get('readability_score', 0), 1)}/100
                        </div>
                    </div>
                    
                    <div class="metric-item">
                        <div class="metric-title">🔍 Kulcsszó elemzés{help_icon("keyword_analysis")}</div>
                        <div class="metric-value">
                            Össz szó: {keyword_analysis.get('total_words', 0)}<br>
                            Egyedi szavak: {keyword_analysis.get('unique_words', 0)}<br>
                            Szókincs gazdagság: {fmt(keyword_analysis.get('vocabulary_richness', 0) * 100, 1)}%<br>
                            Top kulcsszavak:<br>"""
            
            # Top kulcsszavak megjelenítése
            top_keywords = keyword_analysis.get('top_keywords', [])[:5]
            for keyword_data in top_keywords:
                if isinstance(keyword_data, list) and len(keyword_data) >= 2:
                    keyword, count = keyword_data[0], keyword_data[1]
                    html_content += f"                            • {keyword}: {count}x<br>"
            
            html_content += f"""
                        </div>
                    </div>
                    
                    <div class="metric-item">
                        <div class="metric-title">📊 Tartalom mélység{help_icon("content_depth")}</div>
                        <div class="metric-value">
                            Kategória: {content_depth.get('content_length_category', 'N/A')}<br>
                            Témakör lefedettség: {content_depth.get('topic_coverage', 0)}<br>
                            Minőségi mutatók: {content_depth.get('quality_indicators', 0)}<br>
                            Példák száma: {content_depth.get('examples_count', 0)}<br>
                            Statisztikák: {content_depth.get('statistics_count', 0)}<br>
                            Mélység pontszám: {fmt(content_depth.get('depth_score', 0), 1)}/100
                        </div>
                    </div>
                    
                    <div class="metric-item">
                        <div class="metric-title">🎖️ Tekintély jelzők{help_icon("authority_signals")}</div>
                        <div class="metric-value">
                            Szerző info: {"✅" if authority_signals.get('has_author_info') else "❌"}<br>
                            Publikálási dátum: {"✅" if authority_signals.get('has_publication_dates') else "❌"}<br>
                            Kapcsolat info: {authority_signals.get('contact_information', 0)}<br>
                            Szakmai terminológia: {authority_signals.get('professional_terminology', 0)}<br>
                            Tekintély pontszám: {fmt(authority_signals.get('authority_score', 0), 1)}/100
                        </div>
                    </div>
                    
                    <div class="metric-item">
                        <div class="metric-title">🧠 Szemantikai gazdagság{help_icon("semantic_richness")}</div>
                        <div class="metric-value">
                            Entitások:<br>
                            • Személyek: {semantic_richness.get('entities', {}).get('persons', 0)}<br>
                            • Helyek: {semantic_richness.get('entities', {}).get('places', 0)}<br>
                            • Dátumok: {semantic_richness.get('entities', {}).get('dates', 0)}<br>
                            Szakértelem:<br>
                            • Technológia: {semantic_richness.get('domain_expertise', {}).get('technology', 0)}<br>
                            • Üzlet: {semantic_richness.get('domain_expertise', {}).get('business', 0)}<br>
                            Szemantikai pontszám: {fmt(semantic_richness.get('semantic_score', 0), 1)}/100
                        </div>
                    </div>
                    
                    <div class="metric-item">
                        <div class="metric-title">📈 Összesített minőség{help_icon("content_quality")}</div>
                        <div class="metric-value">
                            <strong>Teljes pontszám: {fmt(content_quality.get('overall_quality_score', 0), 1)}/100</strong>
                        </div>
                    </div>"""
        else:
            html_content += '<div class="metric-item"><div class="metric-title">❌ Nincs adat</div><div class="metric-value">Tartalom minőségi adatok nem elérhetők</div></div>'
            
        
        html_content += f"""
                </div>
            </div>
            
            <!-- Platformok tab -->
            <div id="{uid}-platforms" class="tab-content">
                <h3>🎯 Platform kompatibilitás{help_icon("platform_compatibility")}</h3>"""
        
        # Platform Analysis adatok megjelenítése
        if platform_analysis:
            html_content += '<div class="platform-grid">'
            
            for platform_name, platform_data in platform_analysis.items():
                if platform_name == 'summary' or not isinstance(platform_data, dict):
                    continue
                    
                platform_score = platform_data.get('compatibility_score', 0)
                optimization_level = platform_data.get('optimization_level', 'N/A')
                ai_enhanced = platform_data.get('ai_enhanced', False)
                ai_score = platform_data.get('ai_score', 0)
                hybrid_score = platform_data.get('hybrid_score', 0)
                ai_suggestions = platform_data.get('ai_suggestions', [])
                
                html_content += f"""
                    <div class="platform-card {'ai-enhanced' if ai_enhanced else ''}">
                        <div class="platform-name">
                            {platform_name.upper()} {'🤖' if ai_enhanced else ''}{help_icon(f"{platform_name.lower()}_score")}
                        </div>
                        <div class="platform-score">{fmt(platform_score, 0)}</div>
                        <div class="platform-level">{optimization_level}</div>
                        <div style="margin-top: 10px; font-size: 0.8rem;">
                            AI Score: {fmt(ai_score, 0)}/100<br>
                            Hybrid Score: {fmt(hybrid_score, 0)}/100
                        </div>"""
                
                # AI javaslatok megjelenítése
                if ai_suggestions and len(ai_suggestions) > 0:
                    html_content += '<div style="margin-top: 10px; font-size: 0.8rem;"><strong>Javaslatok:</strong><ul style="margin: 5px 0; padding-left: 15px;">'
                    for suggestion in ai_suggestions[:3]:  # Max 3 javaslat
                        html_content += f'<li>{html.escape(str(suggestion))}</li>'
                    html_content += '</ul></div>'
                
                html_content += '</div>'
            
            html_content += '</div>'
            
            # Platform összesítés
            platform_summary = platform_analysis.get('summary', {})
            if platform_summary:
                html_content += f"""
                <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 10px;">
                    <h4>📊 Platform Összesítés</h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 10px;">
                        <div>
                            <strong>Átlag kompatibilitás:</strong> {fmt(platform_summary.get('average_traditional', 0), 1)}/100
                        </div>
                        <div>
                            <strong>Átlag hybrid pontszám:</strong> {fmt(platform_summary.get('average_hybrid', 0), 1)}/100
                        </div>
                        <div>
                            <strong>Legjobb platform:</strong> {platform_summary.get('best_platform', {}).get('name', 'N/A')} 
                            ({fmt(platform_summary.get('best_platform', {}).get('score', 0), 1)})
                        </div>
                        <div>
                            <strong>Fejlesztési potenciál:</strong> +{fmt(platform_summary.get('improvement_potential', 0), 1)} pont
                        </div>
                    </div>
                </div>"""
        else:
            html_content += '<p>Platform elemzési adatok nem elérhetők</p>'
        
        # Platform javaslatok megjelenítése (BELÜL a Platformok tab-ban)
        if platform_suggestions:
            html_content += '<div style="margin-top: 20px;"><h4>💡 Platform-specifikus javaslatok</h4>'
            
            for platform_name, suggestions in platform_suggestions.items():
                if platform_name == 'common_optimizations' or not isinstance(suggestions, list):
                    continue
                    
                if suggestions:
                    html_content += f'<div style="margin: 15px 0; padding: 15px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 10px; border-left: 4px solid {primary_color};">'
                    html_content += f'<h5 style="margin-bottom: 10px; color: #333;">🎯 {platform_name.upper()} optimalizálás</h5>'
                    html_content += '<ul style="margin: 0; padding-left: 20px;">'
                    
                    for suggestion in suggestions[:4]:  # Max 4 javaslat platformonként
                        if isinstance(suggestion, dict):
                            suggestion_text = suggestion.get('suggestion', 'N/A')
                            priority = suggestion.get('priority', 'medium')
                            description = suggestion.get('description', '')
                            
                            priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(priority, '⚪')
                            html_content += f'<li style="margin: 5px 0;"><strong>{priority_icon} {suggestion_text}</strong>'
                            if description:
                                html_content += f'<br><small style="color: #666;">{html.escape(description)}</small>'
                            html_content += '</li>'
                    
                    html_content += '</ul></div>'
            
            # Közös optimalizálások
            common_opts = platform_suggestions.get('common_optimizations', [])
            if common_opts:
                html_content += '<div style="margin: 15px 0; padding: 15px; background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); border-radius: 10px; border-left: 4px solid #2196f3;">'
                html_content += '<h5 style="margin-bottom: 10px; color: #1976d2;">🌟 Közös optimalizálások (minden platformra)</h5>'
                html_content += '<ul style="margin: 0; padding-left: 20px;">'
                
                for opt in common_opts[:3]:
                    if isinstance(opt, dict):
                        suggestion_text = opt.get('suggestion', 'N/A')
                        platforms = opt.get('platforms', 0)
                        html_content += f'<li style="margin: 5px 0;"><strong>{suggestion_text}</strong> <span style="color: #666;">({platforms} platformra vonatkozik)</span></li>'
                
                html_content += '</ul></div>'
            
            html_content += '</div>'
            
        # Platformok tab lezárása
        html_content += '</div>'
            
        # PageSpeed Insights tab kezdése
        html_content += f"""
            <!-- PageSpeed Insights tab -->
            <div id="{uid}-pagespeed" class="tab-content">
                <h3>⚡ PageSpeed Insights eredmények</h3>"""
        
        # PageSpeed Insights adatok megjelenítése
        pagespeed_data = site.get('pagespeed_insights', {})
        if pagespeed_data:
            mobile_data = pagespeed_data.get('mobile', {})
            desktop_data = pagespeed_data.get('desktop', {})
            
            html_content += '<div class="metrics-grid" style="grid-template-columns: 1fr 1fr; gap: 20px;">'
            
            # Mobil eredmények
            if mobile_data:
                mobile_perf = mobile_data.get('performance', 0)
                mobile_seo = mobile_data.get('seo', 0)
                mobile_vitals = mobile_data.get('core_web_vitals', {})
                
                perf_class = 'score-good' if mobile_perf >= 90 else 'score-average' if mobile_perf >= 50 else 'score-poor'
                seo_class = 'score-good' if mobile_seo >= 90 else 'score-average' if mobile_seo >= 50 else 'score-poor'
                
                html_content += f"""
                <div class="metric-item" style="background: linear-gradient(135deg, #e3f2fd 0%, #f1f8ff 100%);">
                    <div class="metric-title">📱 Mobil teljesítmény{help_icon("pagespeed_mobile")}</div>
                    <div class="metric-value">
                        <div style="margin-bottom: 15px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <span>Teljesítmény{help_icon("pagespeed_performance")}</span>
                                <span class="{perf_class}" style="padding: 4px 8px; border-radius: 12px; font-weight: bold;">{mobile_perf}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span>SEO{help_icon("pagespeed_seo")}</span>
                                <span class="{seo_class}" style="padding: 4px 8px; border-radius: 12px; font-weight: bold;">{mobile_seo}</span>
                            </div>
                        </div>
                        
                        <div style="border-top: 1px solid #ddd; padding-top: 15px;">
                            <strong>Core Web Vitals{help_icon("core_web_vitals")}</strong>"""
                
                if mobile_vitals:
                    lcp = mobile_vitals.get('lcp', 'N/A')
                    fid = mobile_vitals.get('fid', 'N/A')
                    cls = mobile_vitals.get('cls', 'N/A')
                    
                    # LCP értékelés
                    lcp_status = "✅"
                    if isinstance(lcp, str) and lcp != 'N/A':
                        try:
                            lcp_val = float(lcp.replace('s', '').replace(' ', ''))
                            lcp_status = "✅" if lcp_val <= 2.5 else "⚠️" if lcp_val <= 4.0 else "❌"
                        except:
                            pass
                    
                    # FID értékelés
                    fid_status = "✅"
                    if isinstance(fid, str) and fid != 'N/A':
                        try:
                            fid_val = float(fid.replace('ms', '').replace(' ', ''))
                            fid_status = "✅" if fid_val <= 100 else "⚠️" if fid_val <= 300 else "❌"
                        except:
                            pass
                    
                    # CLS értékelés
                    cls_status = "✅"
                    if isinstance(cls, (str, float, int)) and str(cls) != 'N/A':
                        try:
                            cls_val = float(str(cls))
                            cls_status = "✅" if cls_val <= 0.1 else "⚠️" if cls_val <= 0.25 else "❌"
                        except:
                            pass
                    
                    html_content += f"""
                            <div style="margin-top: 8px; font-size: 0.9rem;">
                                <div style="display: flex; justify-content: space-between; margin: 4px 0;">
                                    <span>LCP{help_icon("lcp")}</span>
                                    <span>{lcp_status} {lcp}</span>
                                </div>
                                <div style="display: flex; justify-content: space-between; margin: 4px 0;">
                                    <span>FID{help_icon("fid")}</span>
                                    <span>{fid_status} {fid}</span>
                                </div>
                                <div style="display: flex; justify-content: space-between; margin: 4px 0;">
                                    <span>CLS{help_icon("cls")}</span>
                                    <span>{cls_status} {cls}</span>
                                </div>
                            </div>"""
                else:
                    html_content += '<div style="margin-top: 8px; color: #666;">Nincs adat</div>'
                
                html_content += """
                        </div>
                    </div>
                </div>"""
            
            # Desktop eredmények
            if desktop_data:
                desktop_perf = desktop_data.get('performance', 0)
                desktop_seo = desktop_data.get('seo', 0)
                desktop_vitals = desktop_data.get('core_web_vitals', {})
                
                perf_class = 'score-good' if desktop_perf >= 90 else 'score-average' if desktop_perf >= 50 else 'score-poor'
                seo_class = 'score-good' if desktop_seo >= 90 else 'score-average' if desktop_seo >= 50 else 'score-poor'
                
                html_content += f"""
                <div class="metric-item" style="background: linear-gradient(135deg, #f3e5f5 0%, #faf2ff 100%);">
                    <div class="metric-title">🖥️ Desktop teljesítmény{help_icon("pagespeed_desktop")}</div>
                    <div class="metric-value">
                        <div style="margin-bottom: 15px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <span>Teljesítmény{help_icon("pagespeed_performance")}</span>
                                <span class="{perf_class}" style="padding: 4px 8px; border-radius: 12px; font-weight: bold;">{desktop_perf}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span>SEO{help_icon("pagespeed_seo")}</span>
                                <span class="{seo_class}" style="padding: 4px 8px; border-radius: 12px; font-weight: bold;">{desktop_seo}</span>
                            </div>
                        </div>
                        
                        <div style="border-top: 1px solid #ddd; padding-top: 15px;">
                            <strong>Core Web Vitals{help_icon("core_web_vitals")}</strong>"""
                
                if desktop_vitals:
                    lcp = desktop_vitals.get('lcp', 'N/A')
                    fid = desktop_vitals.get('fid', 'N/A')
                    cls = desktop_vitals.get('cls', 'N/A')
                    
                    # LCP értékelés
                    lcp_status = "✅"
                    if isinstance(lcp, str) and lcp != 'N/A':
                        try:
                            lcp_val = float(lcp.replace('s', '').replace(' ', ''))
                            lcp_status = "✅" if lcp_val <= 2.5 else "⚠️" if lcp_val <= 4.0 else "❌"
                        except:
                            pass
                    
                    # FID értékelés
                    fid_status = "✅"
                    if isinstance(fid, str) and fid != 'N/A':
                        try:
                            fid_val = float(fid.replace('ms', '').replace(' ', ''))
                            fid_status = "✅" if fid_val <= 100 else "⚠️" if fid_val <= 300 else "❌"
                        except:
                            pass
                    
                    # CLS értékelés
                    cls_status = "✅"
                    if isinstance(cls, (str, float, int)) and str(cls) != 'N/A':
                        try:
                            cls_val = float(str(cls))
                            cls_status = "✅" if cls_val <= 0.1 else "⚠️" if cls_val <= 0.25 else "❌"
                        except:
                            pass
                    
                    html_content += f"""
                            <div style="margin-top: 8px; font-size: 0.9rem;">
                                <div style="display: flex; justify-content: space-between; margin: 4px 0;">
                                    <span>LCP{help_icon("lcp")}</span>
                                    <span>{lcp_status} {lcp}</span>
                                </div>
                                <div style="display: flex; justify-content: space-between; margin: 4px 0;">
                                    <span>FID{help_icon("fid")}</span>
                                    <span>{fid_status} {fid}</span>
                                </div>
                                <div style="display: flex; justify-content: space-between; margin: 4px 0;">
                                    <span>CLS{help_icon("cls")}</span>
                                    <span>{cls_status} {cls}</span>
                                </div>
                            </div>"""
                else:
                    html_content += '<div style="margin-top: 8px; color: #666;">Nincs adat</div>'
                
                html_content += """
                        </div>
                    </div>
                </div>"""
            
            html_content += '</div>'  # metrics-grid lezárása
            
            # Összesítő információk
            if mobile_data and desktop_data:
                avg_perf = (mobile_data.get('performance', 0) + desktop_data.get('performance', 0)) / 2
                avg_seo = (mobile_data.get('seo', 0) + desktop_data.get('seo', 0)) / 2
                
                html_content += f"""
                <div style="margin-top: 30px; padding: 20px; background: linear-gradient(135deg, #fff3e0 0%, #fffbf7 100%); border-radius: 15px; border-left: 5px solid #ff9800;">
                    <h4 style="color: #ff9800; margin-bottom: 15px;">📊 Összesítő</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div>
                            <strong>Átlagos teljesítmény:</strong> 
                            <span style="font-size: 1.2rem; font-weight: bold; color: {'#4caf50' if avg_perf >= 80 else '#ff9800' if avg_perf >= 60 else '#f44336'};">
                                {fmt(avg_perf, 0)} pont
                            </span>
                        </div>
                        <div>
                            <strong>Átlagos SEO:</strong> 
                            <span style="font-size: 1.2rem; font-weight: bold; color: {'#4caf50' if avg_seo >= 80 else '#ff9800' if avg_seo >= 60 else '#f44336'};">
                                {fmt(avg_seo, 0)} pont
                            </span>
                        </div>
                    </div>
                    
                    <div style="margin-top: 15px; padding: 15px; background: rgba(255,255,255,0.7); border-radius: 8px;">
                        <strong>💡 Javaslatok:</strong>
                        <ul style="margin: 10px 0; padding-left: 20px;">
                            <li>A mobil teljesítmény kulcsfontosságú a SEO és felhasználói élmény szempontjából</li>
                            <li>Core Web Vitals optimalizálása javítja a Google rangsorolást</li>
                            <li>90+ pontszám elérése minden kategóriában az ideális cél</li>
                        </ul>
                    </div>
                </div>"""
        else:
            html_content += '<p style="color: #666; text-align: center; padding: 40px;">PageSpeed Insights adatok nem elérhetők</p>'
            
        # PageSpeed Insights tab lezárása
        html_content += '</div>'
            
        # Javítások tab kezdése
        html_content += f"""
            <!-- Javítások tab -->
            <div id="{uid}-fixes" class="tab-content">
                <h3>🔧 Automatikus javítási javaslatok</h3>"""
        
        # Auto Fixes adatok megjelenítése
        if auto_fixes:
            # Kritikus javítások
            critical_fixes = auto_fixes.get('critical_fixes', [])
            if critical_fixes:
                html_content += '<div style="margin-bottom: 20px;"><h4 style="color: #dc3545;">🚨 Kritikus javítások</h4>'
                for fix in critical_fixes:
                    if isinstance(fix, dict):
                        issue = fix.get('issue', 'N/A')
                        severity = fix.get('severity', 'N/A')
                        impact = fix.get('impact', 'N/A')
                        fix_code = fix.get('fix_code', '')
                        explanation = fix.get('explanation', '')
                        estimated_time = fix.get('estimated_time', '')
                        implementation = fix.get('implementation', '')
                        
                        html_content += f"""
                        <div class="fix-item" style="border-left-color: #dc3545; background: #f8d7da;">
                            <div class="fix-title">🚨 {html.escape(issue)}</div>
                            <div style="margin: 10px 0; color: #666;">
                                <strong>Súlyosság:</strong> {html.escape(severity)}<br>
                                <strong>Hatás:</strong> {html.escape(impact)}<br>
                                <strong>Magyarázat:</strong> {html.escape(explanation)}<br>
                                <strong>Becsült idő:</strong> {html.escape(estimated_time)}<br>
                                <strong>Megvalósítás:</strong> {html.escape(implementation)}
                            </div>"""
                        
                        if fix_code:
                            html_content += f"""
                            <div style="background: #fff; border: 1px solid #ddd; border-radius: 4px; padding: 10px; margin: 10px 0;">
                                <strong>Javítás kódja:</strong>
                                <pre style="background: #f8f9fa; padding: 8px; border-radius: 3px; margin: 5px 0; overflow-x: auto;"><code>{html.escape(fix_code)}</code></pre>
                            </div>"""
                        
                        html_content += '</div>'
                    else:
                        # Fallback régi formátumra
                        html_content += f'<div class="fix-item" style="border-left-color: #dc3545; background: #f8d7da;">'
                        html_content += f'<div class="fix-title">{html.escape(str(fix))}</div></div>'
                html_content += '</div>'
            
            # SEO javítások
            seo_improvements = auto_fixes.get('seo_improvements', [])
            if seo_improvements:
                html_content += '<div style="margin-bottom: 20px;"><h4 style="color: #28a745;">🎯 SEO javítások</h4>'
                for improvement in seo_improvements:
                    if isinstance(improvement, dict):
                        issue = improvement.get('issue', 'N/A')
                        suggestion = improvement.get('suggestion', 'N/A')
                        impact = improvement.get('impact', 'N/A')
                        fix_code = improvement.get('fix_code', '')
                        
                        html_content += f"""
                        <div class="fix-item" style="border-left-color: #28a745;">
                            <div class="fix-title">📝 {html.escape(issue)}</div>
                            <div style="margin: 10px 0; color: #666;">
                                <strong>Javaslat:</strong> {html.escape(suggestion)}<br>
                                <strong>Hatás:</strong> {html.escape(impact)}
                            </div>"""
                        
                        if fix_code:
                            html_content += f'<div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 10px; font-family: monospace; font-size: 0.8rem; overflow-x: auto;"><strong>Javasolt kód:</strong><br>{html.escape(fix_code)}</div>'
                        
                        html_content += '</div>'
                html_content += '</div>'
            
            # Schema javaslatok
            schema_suggestions = auto_fixes.get('schema_suggestions', [])
            if schema_suggestions:
                html_content += '<div style="margin-bottom: 20px;"><h4 style="color: #667eea;">🏗️ Schema.org javaslatok</h4>'
                for suggestion in schema_suggestions:
                    if isinstance(suggestion, dict):
                        schema_type = suggestion.get('type', 'N/A')
                        priority = suggestion.get('priority', 'medium')
                        benefit = suggestion.get('benefit', 'N/A')
                        code = suggestion.get('code', '')
                        
                        priority_color = {'high': '#dc3545', 'medium': '#ffc107', 'low': '#28a745'}.get(priority, '#6c757d')
                        
                        html_content += f"""
                        <div class="fix-item" style="border-left-color: {priority_color};">
                            <div class="fix-title">🏷️ {html.escape(schema_type)} <span style="color: {priority_color}; font-size: 0.8rem;">({priority} prioritás)</span></div>
                            <div style="margin: 10px 0; color: #666;">
                                <strong>Előny:</strong> {html.escape(benefit)}
                            </div>"""
                        
                        if code:
                            html_content += f'<details style="margin-top: 10px;"><summary style="cursor: pointer; color: #667eea;">🔍 Schema kód megtekintése</summary><div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 10px; font-family: monospace; font-size: 0.8rem; overflow-x: auto;">{html.escape(code)}</div></details>'
                        
                        html_content += '</div>'
                html_content += '</div>'
            
            # Tartalom optimalizálások
            content_optimizations = auto_fixes.get('content_optimizations', [])
            if content_optimizations:
                html_content += '<div style="margin-bottom: 20px;"><h4 style="color: #fd7e14;">📝 Tartalom optimalizálások</h4>'
                for optimization in content_optimizations:
                    if isinstance(optimization, dict):
                        issue = optimization.get('issue', 'N/A')
                        benefit = optimization.get('benefit', 'N/A')
                        suggestion = optimization.get('suggestion', 'N/A')
                        example_code = optimization.get('example_code', '')
                        ai_platforms = optimization.get('ai_platforms', [])
                        
                        html_content += f"""
                        <div class="fix-item" style="border-left-color: #fd7e14;">
                            <div class="fix-title">✏️ {html.escape(issue)}</div>
                            <div style="margin: 10px 0; color: #666;">
                                <strong>Javaslat:</strong> {html.escape(suggestion)}<br>
                                <strong>Előny:</strong> {html.escape(benefit)}"""
                        
                        if ai_platforms:
                            platforms_text = ', '.join(ai_platforms)
                            html_content += f'<br><strong>AI platformok:</strong> {html.escape(platforms_text)}'
                        
                        html_content += '</div>'
                        
                        if example_code:
                            html_content += f'<details style="margin-top: 10px;"><summary style="cursor: pointer; color: #fd7e14;">🔍 Példa kód megtekintése</summary><div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 10px; font-family: monospace; font-size: 0.8rem; overflow-x: auto;">{html.escape(example_code)}</div></details>'
                        
                        html_content += '</div>'
                html_content += '</div>'
            
            # AI readiness javítások
            ai_readiness_fixes = auto_fixes.get('ai_readiness_fixes', [])
            if ai_readiness_fixes:
                html_content += '<div style="margin-bottom: 20px;"><h4 style="color: #6f42c1;">🤖 AI Readiness javítások</h4>'
                for fix in ai_readiness_fixes:
                    if isinstance(fix, dict):
                        platform = fix.get('platform', 'N/A')
                        current_score = fix.get('current_score', 0)
                        target_score = fix.get('target_score', 0)
                        quick_wins = fix.get('quick_wins', [])
                        estimated_improvement = fix.get('estimated_improvement', 'N/A')
                        
                        if platform != 'general_ai_optimization':
                            html_content += f"""
                            <div class="fix-item" style="border-left-color: #6f42c1;">
                                <div class="fix-title">🎯 {platform.upper()} optimalizálás</div>
                                <div style="margin: 10px 0; color: #666;">
                                    <strong>Jelenlegi pontszám:</strong> {fmt(current_score, 1)}/100<br>
                                    <strong>Célpont:</strong> {fmt(target_score, 1)}/100<br>
                                    <strong>Becsült javulás:</strong> {html.escape(estimated_improvement)}
                                </div>"""
                            
                            if quick_wins:
                                html_content += '<div style="margin-top: 10px;"><strong>Gyors nyerések:</strong><ul style="margin: 5px 0; padding-left: 20px;">'
                                for win in quick_wins:
                                    html_content += f'<li>{html.escape(str(win))}</li>'
                                html_content += '</ul></div>'
                            
                            html_content += '</div>'
            
            
        else:
            html_content += '<p>Automatikus javítási javaslatok nem elérhetők</p>'
            
        # Javítások tab lezárása
        html_content += '</div>'
            
        # Site card lezárása
        html_content += '</div>'

        #Body lezárása
        html_content += '</div>'

    # Footer
    current_year = datetime.now().year
    html_content += f"""
        <div class="footer">
            <p>© {current_year} GEOcheck | Fejlesztette: Ecsedi Tamás</p>
            <p style="margin-top: 10px; opacity: 0.8;">
                {'🚀 AI & ML támogatott generativ engine optimalizált website ellenőrző rendszer' if is_enhanced else '📊 AI & ML támogatott generativ engine optimalizált website ellenőrző rendszer'}
            </p>
            {f'<p style="margin-top: 5px; opacity: 0.7; font-size: 0.9rem;">geocheck.streamlit.app</p>'}
        </div>
    </div>
    
    
    <script>
        function showTab(event, siteId, tabName) {{
            // Minden tab-content elrejtése az adott site-hoz
            const allTabs = document.querySelectorAll('[id^="' + siteId + '-"]');
            allTabs.forEach(tab => tab.classList.remove('active'));
            
            // A célzott tab megjelenítése
            const targetTab = document.getElementById(siteId + '-' + tabName);
            if (targetTab) {{
                targetTab.classList.add('active');
            }}
            
            // Tab gombok aktív állapotának frissítése
            const tabButtons = event.target.parentElement.querySelectorAll('.tab');
            tabButtons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Megakadályozzuk az alapértelmezett viselkedést
            event.preventDefault();
            return false;
        }}
        
        function refreshAISummary(siteId) {{
            const summaryElement = document.getElementById('ai-summary-content-' + siteId);
            const recommendationsElement = document.getElementById('ai-recommendations-content-' + siteId);
            
            if (summaryElement) {{
                summaryElement.innerHTML = '<div style="text-align: center; padding: 20px;"><div class="spinner-border spinner-border-sm" role="status"></div> AI összefoglaló generálása...</div>';
            }}
            if (recommendationsElement) {{
                recommendationsElement.innerHTML = '<div style="text-align: center; padding: 20px;"><div class="spinner-border spinner-border-sm" role="status"></div> AI javaslatok generálása...</div>';
            }}
            
            // Itt később AJAX hívás lesz egy AI endpoint-hoz
            // Egyelőre egy placeholder üzenet
            setTimeout(() => {{
                if (summaryElement) {{
                    summaryElement.innerHTML = 'Az AI összefoglaló frissítése még nem implementált. Ez egy jövőbeli funkció lesz, amely valós időben frissíti az AI elemzést.';
                }}
                if (recommendationsElement) {{
                    recommendationsElement.innerHTML = 'Az AI javaslatok frissítése még nem implementált. A funkció egy külön API endpoint-ot fog használni az OpenAI-val való kommunikációhoz.';
                }}
            }}, 2000);
        }}
    </script>
    
    <script>
        // Chart.js kódok kezdete
"""

    # JavaScript chart generálás
    for idx, site in enumerate(results_data):
        if not isinstance(site, dict):
            continue
            
        url = site.get("url", "N/A")
        uid = f"site_{idx}_{re.sub(r'[^a-zA-Z0-9]', '_', url)}"
        
        meta_data = site.get("meta_and_headings", {})
        headings = meta_data.get("headings", {})
        
        schema_data = site.get("schema", {})
        schema_count_raw = schema_data.get("count", {})
        
        # Schema count lehet int vagy dict típusú - normalizáljuk
        if isinstance(schema_count_raw, int):
            schema_count = {"Schema elemek": schema_count_raw} if schema_count_raw > 0 else {}
        elif isinstance(schema_count_raw, dict):
            schema_count = schema_count_raw
        else:
            schema_count = {}
        
        # Headings chart
        if headings:
            heading_labels = list(headings.keys())
            heading_values = list(headings.values())
            
            html_content += f"""
    // Heading Chart - {uid}
    new Chart(document.getElementById('headingChart_{uid}'), {{
        type: 'bar',
        data: {{
            labels: {json.dumps(heading_labels)},
            datasets: [{{
                label: 'Heading elemek száma',
                data: {json.dumps(heading_values)},
                backgroundColor: [
                    '{primary_color}80',
                    '{secondary_color}80',
                    'rgba(237, 100, 166, 0.8)',
                    'rgba(255, 159, 64, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)'
                ],
                borderColor: '{primary_color}',
                borderWidth: 1
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: true,
            plugins: {{
                title: {{
                    display: true,
                    text: 'Heading Struktúra'
                }},
                legend: {{
                    display: false
                }}
            }},
            scales: {{
                y: {{
                    beginAtZero: true,
                    ticks: {{
                        stepSize: 1
                    }}
                }}
            }}
        }}
    }});
"""
        
        # Schema chart
        if schema_count and any(v > 0 for v in schema_count.values()):
            filtered_schema = {k: v for k, v in schema_count.items() if v > 0}
            
            html_content += f"""
    // Schema Chart - {uid}
    new Chart(document.getElementById('schemaChart_{uid}'), {{
        type: 'doughnut',
        data: {{
            labels: Object.keys({json.dumps(filtered_schema)}),
            datasets: [{{
                label: 'Schema típusok',
                data: Object.values({json.dumps(filtered_schema)}),
                backgroundColor: [
                    '{primary_color}',
                    '{secondary_color}',
                    'rgba(255, 206, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)',
                    'rgba(255, 159, 64, 0.8)',
                    'rgba(231, 76, 60, 0.8)'
                ],
                borderColor: 'white',
                borderWidth: 2
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: true,
            plugins: {{
                title: {{
                    display: true,
                    text: 'Schema típusok'
                }},
                legend: {{
                    position: 'bottom'
                }}
            }}
        }}
    }});
"""

    html_content += """
    
    // Tooltip-ek inicializálása
    document.addEventListener('DOMContentLoaded', function() {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl, {
                html: true,
                placement: 'top',
                trigger: 'hover focus'
            });
        });
    });
    
    </script>
    </div>  <!-- Close container -->
</body>
</html>
"""

    # HTML fájl mentése
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    report_type = "Enhanced" if is_enhanced else "Standard"
    print(f"✅ {report_type} HTML jelentés elkészült: {output_file}")
    print(f"📊 Elemzett oldalak száma: {len(data)}")
    print(f"⭐ Átlagos AI-readiness score: {avg_score:.1f}/100")
    if is_enhanced:
        print(f"🤖 AI Enhanced eredmények: {enhancement_stats['ai_enhanced_count']} ({enhancement_stats['ai_enhanced_percentage']}%)")
        print(f"🏗️ Schema Enhanced eredmények: {enhancement_stats['schema_enhanced_count']} ({enhancement_stats['schema_enhanced_percentage']}%)")
        if enhancement_stats['cached_count'] > 0:
            print(f"💾 Cache találatok: {enhancement_stats['cached_count']} ({enhancement_stats['cache_hit_rate']}%)")


def generate_csv_export(json_file: str = "ai_readiness_full_report.json",
                        output_file: str = "ai_readiness_report.csv") -> None:
    """Enhanced CSV export generálása"""
    
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Hiba: {e}")
        return
    
    # Data normalizálás
    if isinstance(data, dict) and 'results' in data:
        results_data = data['results']
    elif isinstance(data, list):
        results_data = data
    else:
        results_data = [data] if isinstance(data, dict) else []
    
    # Enhanced felismerés
    detection_result = detect_enhanced_analysis(results_data)
    is_enhanced = detection_result["is_enhanced"]
    
    # Enhanced fieldnames
    fieldnames = [
        'URL', 'AI Score', 'Title Length', 'Description Length',
        'Has Robots.txt', 'Has Sitemap', 'Mobile Friendly',
        'H1 Count', 'Schema Count', 'PSI Mobile', 'PSI Desktop'
    ]
    
    if is_enhanced:
        fieldnames.extend([
            'AI Enhanced', 'AI Overall Score', 'Schema Enhanced', 
            'Schema Completeness', 'Cached', 'Google Validation'
        ])
    
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for site in results_data:
            if not isinstance(site, dict):
                continue
                
            meta = site.get("meta_and_headings", {})
            schema = site.get("schema", {})
            psi = site.get("pagespeed_insights", {})
            
            # Biztonságos hossz számítás
            title = meta.get('title')
            description = meta.get('description')
            title_len = len(title) if title else 0
            desc_len = len(description) if description else 0
            
            row = {
                'URL': site.get('url', 'N/A'),
                'AI Score': fmt(site.get('ai_readiness_score', 0), 0),
                'Title Length': title_len,
                'Description Length': desc_len,
                'Has Robots.txt': site.get('robots_txt', {}).get('can_fetch', False),
                'Has Sitemap': site.get('sitemap', {}).get('exists', False),
                'Mobile Friendly': site.get('mobile_friendly', {}).get('has_viewport', False),
                'H1 Count': meta.get('h1_count', 0),
                'Schema Count': sum(schema.get('count', {}).values()),
                'PSI Mobile': fmt(psi.get('mobile', {}).get('performance', 0), 1) if psi else '—',
                'PSI Desktop': fmt(psi.get('desktop', {}).get('performance', 0), 1) if psi else '—'
            }
            
            # Enhanced mezők hozzáadása
            if is_enhanced:
                ai_content_eval = site.get('ai_content_evaluation', {})
                row.update({
                    'AI Enhanced': bool(ai_content_eval),
                    'AI Overall Score': fmt(ai_content_eval.get('overall_ai_score', 0), 0) if ai_content_eval else '—',
                    'Schema Enhanced': schema.get('validation_status') == 'enhanced',
                    'Schema Completeness': fmt(schema.get('schema_completeness_score', 0), 1),
                    'Cached': site.get('cached', False),
                    'Google Validation': schema.get('google_validation', {}).get('is_valid', False)
                })
            
            writer.writerow(row)
    
    report_type = "Enhanced" if is_enhanced else "Standard"
    print(f"✅ {report_type} CSV export elkészült: {output_file}")


# Példa futtatás
if __name__ == "__main__":
    generate_html_report()
    generate_csv_export()
