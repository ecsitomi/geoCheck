import json
import re
from datetime import datetime
from typing import Dict, List, Optional

def generate_html_report(json_file: str = "ai_readiness_full_report.json", 
                        output_file: str = "report.html") -> None:
    """
    HTML jelentés generálása a GEO elemzés eredményeiből
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
        .score-good {{ background: linear-gradient(135deg, #ffbb33 0%, #ff8800 100%); }}
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
        
        @media (max-width: 768px) {{
            h1 {{ font-size: 1.8rem; }}
            .site-url {{ font-size: 1.2rem; }}
            .charts-row {{ grid-template-columns: 1fr; }}
            .metrics-grid {{ grid-template-columns: 1fr; }}
            .alert-box {{ padding: 10px; font-size: 0.9rem; }}
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
                    <div class="value">{avg_score:.1f}</div>
                    <div class="label">Átlagos AI Score</div>
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
        score_class = "score-excellent" if score >= 70 else "score-good" if score >= 50 else "score-poor"
        
        # Meta adatok kinyerése - JAVÍTVA
        meta_data = site.get("meta_and_headings", {})
        title = meta_data.get("title") or "N/A"
        description = meta_data.get("description") or "N/A"
        headings = meta_data.get("headings", {})
        
        # Schema adatok
        schema_data = site.get("schema", {})
        schema_count = schema_data.get("count", {})
        
        # Mobile adatok
        mobile = site.get("mobile_friendly", {})
        
        # PageSpeed adatok
        psi = site.get("pagespeed_insights", {})
        
        # Title és description hosszak biztonságos számítása - JAVÍTVA
        title_len = len(title) if title and title != "N/A" else 0
        desc_len = len(description) if description and description != "N/A" else 0
        
        # Javított meta megjelenítés
        title_status = "✅" if meta_data.get("title_optimal") else ("⚠️" if title_len > 0 else "❌")
        desc_status = "✅" if meta_data.get("description_optimal") else ("⚠️" if desc_len > 0 else "❌ Hiányzik")
        
        html_content += f"""
        <div class="site-card">
            <div class="site-header">
                <div class="site-url">{url}</div>
                <div class="score-badge {score_class}">{score}</div>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-title">📄 Meta adatok</div>
                    <div class="metric-value">
                        Title: {title_status} {title_len} karakter<br>
                        Description: {desc_status} {desc_len} karakter
                    </div>
                </div>
                
                <div class="metric-item">
                    <div class="metric-title">🤖 Robotok & Sitemap</div>
                    <div class="metric-value">
                        Robots.txt: {"✅ Engedélyezett" if site.get('robots_txt', {}).get('can_fetch') else "❌ Tiltott"}<br>
                        Sitemap: {"✅ Van" if site.get('sitemap', {}).get('exists') else "❌ Nincs"}
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
                        Heading hierarchia: {"✅ Helyes" if meta_data.get('heading_hierarchy_valid') else "⚠️ Javítandó"}
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
"""
        
        # JAVÍTVA: Kritikus problémák figyelmeztetése
        critical_issues = []
        if meta_data.get('h1_count', 0) > 1:
            critical_issues.append(f"🚨 Túl sok H1 elem ({meta_data.get('h1_count')} db)")
        if meta_data.get('h1_count', 0) == 0:
            critical_issues.append("🚨 Hiányzik a H1 elem")
        if desc_len == 0:
            critical_issues.append("🚨 Meta description hiányzik")
        if title_len == 0:
            critical_issues.append("🚨 Title tag hiányzik")
        if any(count > 50 for count in headings.values()):
            excessive_heading = max(headings.items(), key=lambda x: x[1])
            critical_issues.append(f"🚨 Túl sok {excessive_heading[0].upper()} elem ({excessive_heading[1]} db)")
        
        if critical_issues:
            html_content += """
            <div class="alert-box alert-critical">
                <div style="font-weight: 600; margin-bottom: 10px;">⚠️ Kritikus problémák</div>
"""
            for issue in critical_issues[:3]:  # Max 3 kritikus probléma
                html_content += f"""
                <div style="margin: 5px 0;">• {issue}</div>
"""
            html_content += "</div>"
        
        # JAVÍTVA: Fejlesztési javaslatok alacsony score esetén
        if score < 70:
            improvements = []
            if not meta_data.get('title_optimal'):
                if title_len == 0:
                    improvements.append("📝 Adj hozzá title tag-et")
                elif title_len < 30:
                    improvements.append("📝 Hosszabbítsd meg a title-t (30-60 karakter)")
                elif title_len > 60:
                    improvements.append("📝 Rövidítsd le a title-t (30-60 karakter)")
            
            if not meta_data.get('description_optimal'):
                if desc_len == 0:
                    improvements.append("📝 Adj hozzá meta description-t")
                elif desc_len < 120:
                    improvements.append("📝 Hosszabbítsd meg a description-t (120-160 karakter)")
                elif desc_len > 160:
                    improvements.append("📝 Rövidítsd le a description-t (120-160 karakter)")
            
            if sum(schema_data.get('count', {}).values()) == 0:
                improvements.append("🏗️ Adj hozzá Schema.org markup-ot")
            
            if not mobile.get('responsive_images'):
                improvements.append("📱 Használj responsive képeket")
            
            if meta_data.get('h1_count', 0) != 1:
                improvements.append("🏗️ Pontosan 1 H1 elem használata javasolt")
            
            if improvements:
                html_content += """
            <div class="alert-box alert-info">
                <div style="font-weight: 600; margin-bottom: 10px;">💡 Fejlesztési javaslatok</div>
"""
                for improvement in improvements[:4]:  # Max 4 javaslat
                    html_content += f"""
                <div style="margin: 5px 0;">• {improvement}</div>
"""
                html_content += "</div>"
        
        html_content += "</div>"  # site-card bezárása
        
        # PageSpeed Insights táblázat
        if psi:
            html_content += """
            <table>
                <thead>
                    <tr>
                        <th>PageSpeed Metrika</th>
                        <th>Mobile</th>
                        <th>Desktop</th>
                    </tr>
                </thead>
                <tbody>
"""
            mobile_psi = psi.get('mobile', {})
            desktop_psi = psi.get('desktop', {})
            
            metrics = ['performance', 'accessibility', 'best-practices', 'seo']
            metric_names = {
                'performance': '⚡ Performance',
                'accessibility': '♿ Accessibility', 
                'best-practices': '✅ Best Practices',
                'seo': '🔍 SEO'
            }
            
            for metric in metrics:
                mobile_score = mobile_psi.get(metric, 'N/A') if mobile_psi else 'N/A'
                desktop_score = desktop_psi.get(metric, 'N/A') if desktop_psi else 'N/A'
                
                # JAVÍTVA: Csak számértékekhez adjunk színt
                mobile_color = get_score_color(mobile_score) if isinstance(mobile_score, (int, float)) else '#666'
                desktop_color = get_score_color(desktop_score) if isinstance(desktop_score, (int, float)) else '#666'
                
                html_content += f"""
                    <tr>
                        <td>{metric_names.get(metric, metric)}</td>
                        <td style="color: {mobile_color}; font-weight: 600;">{mobile_score}</td>
                        <td style="color: {desktop_color}; font-weight: 600;">{desktop_score}</td>
                    </tr>
"""
            
            html_content += """
                </tbody>
            </table>
"""
        
        # Schema.org részletek - JAVÍTVA: szűrjük a None/Unknown típusokat
        valid_schemas = [
            detail for detail in schema_data.get("details", [])
            if detail.get('type') and detail.get('type') not in ['None', 'Unknown', '']
        ]
        
        if valid_schemas:
            html_content += """
            <details style="margin-top: 20px;">
                <summary style="cursor: pointer; font-weight: 600; color: #667eea;">📋 Schema.org részletek</summary>
                <div style="margin-top: 10px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
"""
            for detail in valid_schemas[:5]:  # Max 5 schema
                schema_type = detail.get('type', 'Unknown')
                html_content += f"""
                    <div style="margin: 5px 0;">
                        • <strong>{schema_type}</strong>
                        {' 🖼️' if detail.get('has_image') else ''}
                        {' ⭐' if detail.get('has_rating') else ''}
                    </div>
"""
            html_content += """
                </div>
            </details>
"""
        elif schema_data.get("count") and sum(schema_data.get("count", {}).values()) > 0:
            html_content += """
            <div class="alert-box alert-warning">
                <div style="font-weight: 600;">📋 Schema.org részletek</div>
                <div style="margin-top: 5px;">Schema markup található, de típus információ nem elérhető</div>
            </div>
"""
        
        html_content += "</div>"

    # Footer
    html_content += """
        <div class="footer">
            <p>© 2024 GEO Analyzer | AI Readiness Report</p>
            <p style="margin-top: 10px; opacity: 0.8;">Készült Chart.js vizualizációval</p>
        </div>
    </div>
    
    <script>
"""

    # JavaScript chart generálás
    for idx, site in enumerate(data):
        url = site.get("url", "N/A")
        uid = f"site_{idx}_{re.sub(r'[^a-zA-Z0-9]', '_', url)}"
        
        meta_data = site.get("meta_and_headings", {})
        headings = meta_data.get("headings", {})
        
        schema_data = site.get("schema", {})
        schema_count = schema_data.get("count", {})
        
        # Headings chart - JAVÍTVA: figyelmeztetés túl sok heading esetén
        if headings:
            heading_labels = list(headings.keys())
            heading_values = list(headings.values())
            
            # Ellenőrizzük, hogy van-e túl sok heading
            excessive_headings = any(count > 50 for count in heading_values)
            chart_warning = "⚠️ Túl sok heading elem!" if excessive_headings else ""
            
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
                    text: 'Heading Struktúra {chart_warning}'
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
        
        # Schema chart - JAVÍTVA: csak akkor mutassunk, ha van értelmes adat
        if schema_count and any(v > 0 for v in schema_count.values()):
            # Csak a nem-nulla értékeket mutatjuk
            filtered_schema = {k: v for k, v in schema_count.items() if v > 0}
            schema_labels = list(filtered_schema.keys())
            schema_values = list(filtered_schema.values())
            
            html_content += f"""
    // Schema Chart - {uid}
    new Chart(document.getElementById('schemaChart_{uid}'), {{
        type: 'doughnut',
        data: {{
            labels: {schema_labels},
            datasets: [{{
                label: 'Schema típusok',
                data: {schema_values},
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
                    text: 'Schema.org Típusok'
                }},
                legend: {{
                    position: 'bottom'
                }}
            }}
        }}
    }});
"""
        else:
            # Ha nincs schema, üres chart helyett üzenet
            html_content += f"""
    // Schema Chart - {uid} (nincs schema adat)
    new Chart(document.getElementById('schemaChart_{uid}'), {{
        type: 'doughnut',
        data: {{
            labels: ['Nincs Schema.org'],
            datasets: [{{
                data: [1],
                backgroundColor: ['rgba(200, 200, 200, 0.5)'],
                borderWidth: 0
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: true,
            plugins: {{
                title: {{
                    display: true,
                    text: 'Schema.org Típusok - Nincs adat'
                }},
                legend: {{
                    display: false
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
                'AI Score': site.get('ai_readiness_score', 0),
                'Title Length': title_len,
                'Description Length': desc_len,
                'Has Robots.txt': site.get('robots_txt', {}).get('can_fetch', False),
                'Has Sitemap': site.get('sitemap', {}).get('exists', False),
                'Mobile Friendly': site.get('mobile_friendly', {}).get('has_viewport', False),
                'H1 Count': meta.get('h1_count', 0),
                'Schema Count': sum(schema.get('count', {}).values()),
                'PSI Mobile': psi.get('mobile', {}).get('performance', 'N/A') if psi else 'N/A',
                'PSI Desktop': psi.get('desktop', {}).get('performance', 'N/A') if psi else 'N/A'
            }
            writer.writerow(row)
    
    print(f"✅ CSV export elkészült: {output_file}")


# Példa futtatás
if __name__ == "__main__":
    generate_html_report()
    generate_csv_export()