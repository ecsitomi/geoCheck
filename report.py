import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import html

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

def generate_html_report(json_file: str = "ai_readiness_full_report.json", 
                        output_file: str = "report.html") -> None:
    """
    HTML jelentés generálása a GEO elemzés eredményeiből - TELJES VERZIÓ
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

    # Átlagos score számítása
    avg_score = sum(site.get('ai_readiness_score', 0) for site in data) / len(data) if data else 0
    
    # HTML template
    html_content = f"""
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GEO AI Readiness Report - {datetime.now().strftime('%Y-%m-%d')}</title>
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: #333;
            font-size: 2.5rem;
            margin-bottom: 10px;
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
        }}
        
        .summary-card .value {{
            font-size: 2rem;
            font-weight: 700;
            color: #667eea;
        }}
        
        .summary-card .label {{
            font-size: 0.9rem;
            color: #666;
            margin-top: 5px;
        }}
        
        .site-card {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
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
        }}
        
        .score-excellent {{ background: linear-gradient(135deg, #00c851 0%, #00a846 100%); }}
        .score-average {{ background: linear-gradient(135deg, #ffc107 0%, #e0a800 100%); }}
        .score-poor {{ background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%); }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .metric-item {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        
        .metric-title {{
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .metric-value {{
            color: #666;
            font-size: 0.9rem;
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
            border-radius: 10px;
            text-align: center;
        }}
        
        .platform-name {{
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .platform-score {{
            font-size: 2rem;
            font-weight: 700;
            color: #667eea;
        }}
        
        .platform-level {{
            font-size: 0.8rem;
            color: #666;
            margin-top: 5px;
        }}
        
        .chart-container {{
            width: 100%;
            max-width: 500px;
            margin: 20px auto;
        }}
        
        .charts-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin: 30px 0;
        }}
        
        .tabs {{
            display: flex;
            gap: 10px;
            margin: 20px 0;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        .tab {{
            padding: 10px 20px;
            background: none;
            border: none;
            cursor: pointer;
            font-weight: 600;
            color: #666;
            transition: all 0.3s;
        }}
        
        .tab.active {{
            color: #667eea;
            border-bottom: 3px solid #667eea;
        }}
        
        .tab-content {{
            display: none;
            padding: 20px 0;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }}
        
        .check-icon {{ color: #00c851; }}
        .cross-icon {{ color: #ff4444; }}
        
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
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
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
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e0e0e0;
        }}
        
        .ai-metric-label {{
            font-size: 0.8rem;
            color: #666;
            margin-bottom: 5px;
        }}
        
        .ai-metric-value {{
            font-size: 1.2rem;
            font-weight: 600;
            color: #333;
        }}
        
        .fix-item {{
            background: #ffffff;
            padding: 20px;
            margin: 20px 0;
            border-radius: 12px;
            border-left: 4px solid #667eea;
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
        }}
        
        .fix-title::before {{
            content: "🔧";
            margin-right: 8px;
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
            background: #667eea;
            color: white;
            font-size: 0.7rem;
            padding: 2px 8px;
            border-radius: 4px;
            font-family: 'Inter', sans-serif;
        }}
        
        .fix-time {{
            color: #667eea;
            font-weight: 600;
            font-size: 0.9rem;
            margin-top: 10px;
        }}
        
        .keywords-container {{
            background: #f8fafc;
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            border: 1px solid #e2e8f0;
        }}
        
        .keywords-title {{
            font-weight: 600;
            color: #334155;
            margin-bottom: 12px;
            font-size: 1rem;
        }}
        
        .keywords-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        
        .keyword-item {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
            transition: transform 0.2s;
        }}
        
        .keyword-item:hover {{
            transform: scale(1.05);
        }}
        
        .keyword-count {{
            background: rgba(255, 255, 255, 0.3);
            margin-left: 6px;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 0.75rem;
        }}
        
        details {{
            margin: 15px 0;
        }}
        
        summary {{
            cursor: pointer;
            font-weight: 600;
            color: #667eea;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        @media (max-width: 768px) {{
            h1 {{ font-size: 1.8rem; }}
            .site-url {{ font-size: 1.2rem; }}
            .charts-row {{ grid-template-columns: 1fr; }}
            .metrics-grid {{ grid-template-columns: 1fr; }}
            .platform-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 GEO AI Readiness Report</h1>
            <p style="color: #666;">Generative Engine Optimization elemzés - {datetime.now().strftime('%Y. %m. %d. %H:%M')}</p>
            
            <div class="summary">
                <div class="summary-card">
                    <div class="value">{len(data)}</div>
                    <div class="label">Elemzett oldalak</div>
                </div>
                <div class="summary-card">
                    <div class="value">{fmt(avg_score, 1)}</div>
                    <div class="label">Átlagos AI Readiness</div>
                </div>
                <div class="summary-card">
                    <div class="value">{sum(1 for s in data if s.get('ai_readiness_score', 0) >= 70)}</div>
                    <div class="label">Kiváló oldalak</div>
                </div>
                <div class="summary-card">
                    <div class="value">{sum(1 for s in data if s.get('ai_readiness_score', 0) < 50)}</div>
                    <div class="label">Fejlesztendő</div>
                </div>
            </div>
        </header>
"""

    # Minden oldal feldolgozása
    for idx, site in enumerate(data):
        url = site.get("url", "N/A")
        score = site.get("ai_readiness_score", 0)
        uid = f"site_{idx}_{re.sub(r'[^a-zA-Z0-9]', '_', url)}"
        
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
        
        html_content += f"""
        <div class="site-card">
            <div class="site-header">
                <div class="site-url">{url}</div>
                <div class="score-badge {score_class}">{fmt(score, 0)}</div>
            </div>
            
            <!-- Tab navigáció -->
            <div class="tabs">
                <button class="tab active" onclick="showTab(event, '{uid}', 'overview')">📊 Áttekintés</button>
                <button class="tab" onclick="showTab(event, '{uid}', 'ai-metrics')">🤖 AI Metrikák</button>
                <button class="tab" onclick="showTab(event, '{uid}', 'content')">📝 Tartalom</button>
                <button class="tab" onclick="showTab(event, '{uid}', 'platforms')">🎯 Platformok</button>
                <button class="tab" onclick="showTab(event, '{uid}', 'fixes')">🔧 Javítások</button>
            </div>
            
            <!-- Áttekintés tab -->
            <div id="{uid}-overview" class="tab-content active">
                <div class="metrics-grid">
                    <div class="metric-item">
                        <div class="metric-title">📄 Meta adatok</div>
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
                        <div class="metric-title">🤖 Crawlability</div>
                        <div class="metric-value">
                            Robots.txt: {"✅ Engedélyezett" if site.get('robots_txt', {}).get('can_fetch') else "❌ Tiltott"}<br>
                            Sitemap: {"✅ Van" if site.get('sitemap', {}).get('exists') else "❌ Nincs"}<br>
                            HTML méret: {fmt(site.get('html_size_kb', 0), 1)} KB
                        </div>
                    </div>
                    
                    <div class="metric-item">
                        <div class="metric-title">📱 Mobile-friendly</div>
                        <div class="metric-value">
                            Viewport: {"✅" if mobile.get('has_viewport') else "❌"}<br>
                            Responsive képek: {"✅" if mobile.get('responsive_images') else "❌"}
                        </div>
                    </div>
                    
                    <div class="metric-item">
                        <div class="metric-title">🏗️ Struktúra</div>
                        <div class="metric-value">
                            H1 elemek: {meta_data.get('h1_count', 0)}<br>
                            Heading hierarchia: {"✅" if meta_data.get('heading_hierarchy_valid') else "⚠️"}<br>
                            Schema típusok: {sum(schema_data.get('count', {}).values())}
                        </div>
                    </div>
                </div>
                
                <div class="charts-row">
                    <div class="chart-container">
                        <canvas id="headingChart_{uid}"></canvas>
                    </div>
                    <div class="chart-container">
                        <canvas id="schemaChart_{uid}"></canvas>
                    </div>
                </div>
            </div>
            
            <!-- AI Metrikák tab -->
            <div id="{uid}-ai-metrics" class="tab-content">
"""
        
        # AI metrikák megjelenítése
        if ai_summary and not ai_summary.get('error'):
            weighted_avg = ai_summary.get("weighted_average")
            
            html_content += f"""
                <h3>AI Readiness Összefoglaló</h3>
                <div class="ai-metrics-grid">
                    <div class="ai-metric">
                        <div class="ai-metric-label">Összesített</div>
                        <div class="ai-metric-value">{fmt(score, 0)}</div>
                    </div>
                    <div class="ai-metric">
                        <div class="ai-metric-label">Szint</div>
                        <div class="ai-metric-value">{level_from_score(score)}</div>
                    </div>
                </div>
                
                <h4>AI metrika átlag (weighted)</h4>
                <div class="ai-metrics-grid">
                    <div class="ai-metric">
                        <div class="ai-metric-label">Értékelt átlag</div>
                        <div class="ai-metric-value">{fmt(weighted_avg, 1)}</div>
                    </div>
                </div>
                
                <h4>Részletes pontszámok:</h4>
                <div class="ai-metrics-grid">
"""
            scores = ai_summary.get('individual_scores', {})
            for key, value in scores.items():
                html_content += f"""
                    <div class="ai-metric">
                        <div class="ai-metric-label">{key.replace('_', ' ').title()}</div>
                        <div class="ai-metric-value">{value}</div>
                    </div>
"""
            html_content += "</div>"
            
            # AI specifikus metrikák
            if ai_metrics and not ai_metrics.get('error'):
                # Q&A formátum
                qa_format = ai_metrics.get('qa_format', {})
                if qa_format:
                    html_content += f"""
                <h4>Q&A Formátum:</h4>
                <ul>
                    <li>FAQ Schema: {"✅" if qa_format.get('has_faq_schema') else "❌"}</li>
                    <li>Kérdések száma: {qa_format.get('question_patterns_count', 0)}</li>
                    <li>Q&A Score: {fmt(qa_format.get('qa_score', 0), 1)}/100</li>
                </ul>
"""
                
                # Tartalom struktúra
                content_structure = ai_metrics.get('content_structure', {})
                if content_structure:
                    lists = content_structure.get('lists', {})
                    html_content += f"""
                <h4>Tartalom struktúra:</h4>
                <ul>
                    <li>Rendezett listák: {lists.get('ordered', 0)}</li>
                    <li>Nem rendezett listák: {lists.get('unordered', 0)}</li>
                    <li>Táblázatok: {content_structure.get('tables', {}).get('count', 0)}</li>
                    <li>Struktúra score: {fmt(content_structure.get('structure_score', 0), 1)}/100</li>
                </ul>
"""
        else:
            html_content += "<p>AI metrikák nem elérhetők</p>"
            
        html_content += "</div>"
        
        # Tartalom tab
        html_content += f"""
            <!-- Tartalom tab -->
            <div id="{uid}-content" class="tab-content">
"""
        
        if content_quality and not content_quality.get('error'):
            readability = content_quality.get('readability', {})
            keyword_analysis = content_quality.get('keyword_analysis', {})
            content_depth = content_quality.get('content_depth', {})
            
            html_content += f"""
                <h3>Tartalom minőség</h3>
                <div class="metric-item">
                    <div class="metric-title">📖 Olvashatóság</div>
                    <div class="metric-value">
                        Szószám: {readability.get('word_count', 0)}<br>
                        Mondatok: {readability.get('sentence_count', 0)}<br>
                        Flesch score: {fmt(readability.get('flesch_score', 0), 1)}<br>
                        Szint: {readability.get('readability_level', 'N/A')}
                    </div>
                </div>
                
                <div class="metric-item">
                    <div class="metric-title">🔑 Kulcsszavak</div>
                    <div class="metric-value">
                        Összes szó: {keyword_analysis.get('total_words', 0)}<br>
                        Egyedi szavak: {keyword_analysis.get('unique_words', 0)}<br>
                        Szókincs gazdagság: {fmt(keyword_analysis.get('vocabulary_richness', 0), 3)}
                    </div>
                </div>
"""
            
            # Top kulcsszavak
            top_keywords = keyword_analysis.get('top_keywords', [])
            if top_keywords:
                html_content += """
                <div class="keywords-container">
                    <div class="keywords-title">🔑 Top kulcsszavak</div>
                    <ul class="keywords-list">"""
                for word, count in top_keywords[:5]:
                    html_content += f"""
                        <li class="keyword-item">
                            {html.escape(word)}
                            <span class="keyword-count">{count}x</span>
                        </li>"""
                html_content += """
                    </ul>
                </div>"""
            
            # Tartalom mélység
            html_content += f"""
                <div class="metric-item">
                    <div class="metric-title">📊 Tartalom mélység</div>
                    <div class="metric-value">
                        Kategória: {content_depth.get('content_length_category', 'N/A')}<br>
                        Témák száma: {content_depth.get('topic_coverage', 0)}<br>
                        Példák: {content_depth.get('examples_count', 0)}<br>
                        Statisztikák: {content_depth.get('statistics_count', 0)}<br>
                        Külső hivatkozások: {content_depth.get('external_references', 0)}<br>
                        Mélység score: {fmt(content_depth.get('depth_score', 0), 1)}/100
                    </div>
                </div>
"""
        else:
            html_content += "<p>Tartalom elemzés nem elérhető</p>"
            
        html_content += "</div>"
        
        # Platformok tab
        html_content += f"""
            <!-- Platformok tab -->
            <div id="{uid}-platforms" class="tab-content">
"""
        
        if platform_analysis and not platform_analysis.get('error'):
            summary = platform_analysis.get('summary', {})
            if summary and not summary.get('error'):
                html_content += f"""
                <h3>Platform kompatibilitás</h3>
                <div class="alert-box alert-info">
                    <strong>Átlagos kompatibilitás:</strong> {fmt(summary.get('average_compatibility', 0), 1)}/100<br>
                    <strong>Legjobb platform:</strong> {summary.get('best_platform', {}).get('name', 'N/A')} 
                    ({fmt(summary.get('best_platform', {}).get('score', 0), 1)}/100)<br>
                    <strong>Összesített szint:</strong> {summary.get('overall_level', 'N/A')}
                </div>
                
                <div class="platform-grid">
"""
                
                # Platform kártyák
                for platform in ['chatgpt', 'claude', 'gemini', 'bing_chat']:
                    if platform in platform_analysis:
                        p_data = platform_analysis[platform]
                        if not p_data.get('error'):
                            p_score = p_data.get('compatibility_score', 0)
                            p_level = p_data.get('optimization_level', 'N/A')
                            
                            html_content += f"""
                    <div class="platform-card">
                        <div class="platform-name">{platform.replace('_', ' ').title()}</div>
                        <div class="platform-score">{fmt(p_score, 1)}</div>
                        <div class="platform-level">{p_level}</div>
                    </div>
"""
                
                html_content += "</div>"
                
                # Platform specifikus javaslatok
                if platform_suggestions and not platform_suggestions.get('error'):
                    common = platform_suggestions.get('common_optimizations', [])
                    if common:
                        html_content += "<h4>Közös optimalizálási lehetőségek:</h4><ul>"
                        for suggestion in common[:3]:
                            if isinstance(suggestion, dict):
                                html_content += f"<li><strong>{suggestion.get('suggestion', 'N/A')}</strong> - {suggestion.get('description', '')}</li>"
                        html_content += "</ul>"
        else:
            html_content += "<p>Platform elemzés nem elérhető</p>"
            
        html_content += "</div>"
        
        # Javítások tab
        html_content += f"""
            <!-- Javítások tab -->
            <div id="{uid}-fixes" class="tab-content">
"""
        
        if auto_fixes and not auto_fixes.get('error'):
            # Kritikus javítások
            critical = auto_fixes.get('critical_fixes', [])
            if critical:
                html_content += "<h3>🚨 Kritikus javítások</h3>"
                for fix in critical[:3]:
                    html_content += f"""
                <div class="fix-item">
                    <div class="fix-title">{fix.get('issue', 'N/A')}</div>
                    <div class="fix-description">Hatás: {fix.get('impact', 'N/A')}</div>
                    <div class="fix-code">{fix.get('fix_code', '')}</div>
                    <div class="fix-time">⏱️ Időigény: {fix.get('estimated_time', 'N/A')}</div>
                </div>
"""
            
            # SEO javítások
            seo = auto_fixes.get('seo_improvements', [])
            if seo:
                html_content += "<h3>📈 SEO fejlesztések</h3>"
                for improvement in seo[:3]:
                    if 'issue' in improvement:
                        html_content += f"""
                <div class="fix-item">
                    <div class="fix-title">{improvement.get('issue', 'N/A')}</div>
                    <div class="fix-description">{improvement.get('suggestion', '')}</div>
                </div>
"""
            
            # Schema javaslatok
            schema_fixes = auto_fixes.get('schema_suggestions', [])
            if schema_fixes:
                html_content += """
                <details>
                    <summary>🏗️ Schema.org javaslatok</summary>
                    <div style="padding: 10px;">
"""
                for schema_fix in schema_fixes[:2]:
                    html_content += f"""
                    <div class="fix-item">
                        <div class="fix-title">{schema_fix.get('type', 'N/A')}</div>
                        <div class="fix-description">Előny: {schema_fix.get('benefit', 'N/A')}</div>
                    </div>
"""
                html_content += "</div></details>"
        
        # Ha az auto_fixes hibás vagy üres, mutassunk alternatív javaslatokat
        if not auto_fixes or auto_fixes.get('error') or (
            not auto_fixes.get('critical_fixes') and 
            not auto_fixes.get('seo_improvements') and 
            not auto_fixes.get('schema_suggestions')
        ):
            # Hibaüzenet megjelenítése ha van
            error_msg = auto_fixes.get('error', '') if auto_fixes else ''
            if error_msg:
                html_content += f"""
                <div class="alert-box alert-critical">
                    <strong>Auto-fix hiba:</strong> {html.escape(error_msg)}
                </div>
"""
            
            # Implementation guide megjelenítése
            impl_guide = auto_fixes.get('implementation_guide', {}) if auto_fixes else {}
            if impl_guide:
                html_content += "<h3>📋 Implementációs útmutató</h3>"
                
                # Prioritási sorrend
                priority_order = impl_guide.get('priority_order', [])
                if priority_order:
                    html_content += "<h4>Prioritási sorrend:</h4><ol>"
                    for priority in priority_order:
                        html_content += f"<li>{priority}</li>"
                    html_content += "</ol>"
                
                # Időbecslés
                timeline = impl_guide.get('estimated_timeline', {})
                if timeline:
                    html_content += "<h4>Becsült időigény:</h4><ul>"
                    for task, time in timeline.items():
                        task_name = task.replace('_', ' ').title()
                        html_content += f"<li><strong>{task_name}:</strong> {time}</li>"
                    html_content += "</ul>"
                
                # Tesztelési checklist
                testing = impl_guide.get('testing_checklist', [])
                if testing:
                    html_content += """
                    <details>
                        <summary>✅ Tesztelési checklist</summary>
                        <ul style="margin: 10px 0;">
"""
                    for test in testing:
                        html_content += f"<li>{test}</li>"
                    html_content += "</ul></details>"
                
                # Monitoring
                monitoring = impl_guide.get('monitoring', [])
                if monitoring:
                    html_content += """
                    <details>
                        <summary>📊 Monitorozás</summary>
                        <ul style="margin: 10px 0;">
"""
                    for monitor in monitoring:
                        html_content += f"<li>{monitor}</li>"
                    html_content += "</ul></details>"
            
            # Platform prioritások megjelenítése
            platform_priorities = site.get('platform_priorities', [])
            if platform_priorities:
                html_content += "<h3>🎯 Platform prioritások</h3>"
                for priority in platform_priorities:
                    platform_name = priority.get('platform', '').replace('_', ' ').title()
                    score = priority.get('score', 0)
                    priority_level = priority.get('priority', 'N/A')
                    action = priority.get('action', 'N/A')
                    
                    # Színkód a pontszám alapján
                    color_class = badge_class(score)
                    if 'excellent' in color_class:
                        priority_color = '#00c851'
                    elif 'good' in color_class:
                        priority_color = '#ffc107'
                    else:
                        priority_color = '#ff4444'
                    
                    html_content += f"""
                <div class="fix-item" style="border-left-color: {priority_color};">
                    <div class="fix-title">{platform_name} - {fmt(score, 1)} pont</div>
                    <div class="fix-description"><strong>Prioritás:</strong> {priority_level}</div>
                    <div class="fix-description"><strong>Javasolt művelet:</strong> {action}</div>
                </div>
"""
            
            # Platform suggestions megjelenítése
            if platform_suggestions and not platform_suggestions.get('error'):
                common = platform_suggestions.get('common_optimizations', [])
                if common:
                    html_content += "<h3>🔧 Általános optimalizációs javaslatok</h3>"
                    for suggestion in common:
                        if isinstance(suggestion, dict):
                            html_content += f"""
                        <div class="fix-item">
                            <div class="fix-title">{suggestion.get('suggestion', 'N/A')}</div>
                            <div class="fix-description"><strong>Típus:</strong> {suggestion.get('type', 'N/A').title()}</div>
                            <div class="fix-description"><strong>Prioritás:</strong> {suggestion.get('priority', 'N/A').title()}</div>
                            <div class="fix-description"><strong>Leírás:</strong> {suggestion.get('description', 'N/A')}</div>
                            <div class="fix-description"><strong>Érintett platformok:</strong> {suggestion.get('platforms', 0)}</div>
                        </div>
"""
                
                # Platform specifikus javaslatok
                for platform in ['chatgpt', 'claude', 'gemini', 'bing_chat']:
                    platform_suggestions_list = platform_suggestions.get(platform, [])
                    if platform_suggestions_list:
                        platform_name = platform.replace('_', ' ').title()
                        html_content += f"""
                        <details>
                            <summary>🤖 {platform_name} specifikus javaslatok</summary>
                            <div style="padding: 10px;">
"""
                        for suggestion in platform_suggestions_list[:3]:
                            if isinstance(suggestion, dict):
                                html_content += f"""
                            <div class="fix-item">
                                <div class="fix-title">{suggestion.get('suggestion', 'N/A')}</div>
                                <div class="fix-description"><strong>Típus:</strong> {suggestion.get('type', 'N/A').title()}</div>
                                <div class="fix-description"><strong>Prioritás:</strong> {suggestion.get('priority', 'N/A').title()}</div>
                                <div class="fix-description"><strong>Leírás:</strong> {suggestion.get('description', 'N/A')}</div>
                                <div class="fix-code">{suggestion.get('implementation', '')}</div>
                            </div>
"""
                        html_content += "</div></details>"
            
            # Ha még mindig nincs tartalom, akkor alapértelmezett üzenet
            if not impl_guide and not platform_priorities and not (platform_suggestions and platform_suggestions.get('common_optimizations')):
                html_content += "<p>Specifikus javítási javaslatok nem elérhetők, de az elemzési eredmények alapján készíthető fejlesztési terv.</p>"
            
        html_content += "</div></div>"  # tab-content és site-card bezárása

    # Footer
    current_year = datetime.now().year
    html_content += f"""
        <div class="footer">
            <p>© {current_year} GEO Analyzer | AI Readiness Report</p>
            <p style="margin-top: 10px; opacity: 0.8;">Teljes elemzés minden AI platform számára</p>
        </div>
    </div>
    
    <script>
        function showTab(ev, siteId, tabName) {{
            const tabs = document.querySelectorAll(`#${{siteId}}-overview, #${{siteId}}-ai-metrics, #${{siteId}}-content, #${{siteId}}-platforms, #${{siteId}}-fixes`);
            tabs.forEach(tab => tab.classList.remove('active'));
            
            document.getElementById(`${{siteId}}-${{tabName}}`).classList.add('active');
            
            const tabButtons = ev.target.parentElement.querySelectorAll('.tab');
            tabButtons.forEach(btn => btn.classList.remove('active'));
            ev.target.classList.add('active');
        }}
"""

    # JavaScript chart generálás
    for idx, site in enumerate(data):
        url = site.get("url", "N/A")
        uid = f"site_{idx}_{re.sub(r'[^a-zA-Z0-9]', '_', url)}"
        
        meta_data = site.get("meta_and_headings", {})
        headings = meta_data.get("headings", {})
        
        schema_data = site.get("schema", {})
        schema_count = schema_data.get("count", {})
        
        # Headings chart
        if headings:
            heading_labels = list(headings.keys())
            heading_values = list(headings.values())
            
            html_content += f"""
    // Heading Chart - {uid}
    new Chart(document.getElementById('headingChart_{uid}'), {{
        type: 'bar',
        data: {{
            labels: {heading_labels},
            datasets: [{{
                label: 'Heading elemek száma',
                data: {heading_values},
                backgroundColor: [
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(118, 75, 162, 0.8)',
                    'rgba(237, 100, 166, 0.8)',
                    'rgba(255, 159, 64, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)'
                ],
                borderColor: 'rgba(102, 126, 234, 1)',
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
        
        # Schema chart - tényleges megrajzolás
        if schema_count and any(v > 0 for v in schema_count.values()):
            filtered_schema = {k: v for k, v in schema_count.items() if v > 0}
            schema_labels = list(filtered_schema.keys())
            schema_values = list(filtered_schema.values())
            
            html_content += f"""
    // Schema Chart - {uid}
    const schemaCounts_{uid.replace('-', '_')} = {json.dumps(filtered_schema)};
    new Chart(document.getElementById('schemaChart_{uid}'), {{
        type: 'bar',
        data: {{
            labels: Object.keys(schemaCounts_{uid.replace('-', '_')}),
            datasets: [{{
                label: 'Schema típusok',
                data: Object.values(schemaCounts_{uid.replace('-', '_')}),
                backgroundColor: [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
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

    html_content += """
    </script>
</body>
</html>
"""

    # HTML fájl mentése
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ HTML jelentés elkészült: {output_file}")
    print(f"📊 Elemzett oldalak száma: {len(data)}")
    print(f"⭐ Átlagos AI-readiness score: {avg_score:.1f}/100")


def get_score_color(score: int) -> str:
    """Score alapján szín meghatározása"""
    if score >= 90:
        return "#00c851"
    elif score >= 70:
        return "#ffbb33"
    elif score >= 50:
        return "#ff8800"
    else:
        return "#ff4444"


def generate_csv_export(json_file: str = "ai_readiness_full_report.json",
                        output_file: str = "ai_readiness_report.csv") -> None:
    """CSV export generálása"""
    import csv
    
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Hiba: {e}")
        return
    
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            'URL', 'AI Score', 'Title Length', 'Description Length',
            'Has Robots.txt', 'Has Sitemap', 'Mobile Friendly',
            'H1 Count', 'Schema Count', 'PSI Mobile', 'PSI Desktop'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for site in data:
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
                'AI Score': fmt(site.get('ai_readiness_score', 0), 1),
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
            writer.writerow(row)
    
    print(f"✅ CSV export elkészült: {output_file}")


# Példa futtatás
if __name__ == "__main__":
    generate_html_report()
    generate_csv_export()