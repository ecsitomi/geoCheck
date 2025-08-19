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
        
        @media (max-width: 768px) {{
            h1 {{ font-size: 1.8rem; }}
            .site-url {{ font-size: 1.2rem; }}
            .charts-row {{ grid-template-columns: 1fr; }}
            .metrics-grid {{ grid-template-columns: 1fr; }}
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
        
        # Title és description hosszak biztonságos számítása
        title_len = len(title) if title and title != "N/A" else 0
        desc_len = len(description) if description and description != "N/A" else 0
        
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
                        Title: {"✅" if meta_data.get("title_optimal") else "⚠️"} {title_len} karakter<br>
                        Description: {"✅" if meta_data.get("description_optimal") else "⚠️"} {desc_len} karakter
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
                
                mobile_color = get_score_color(mobile_score) if isinstance(mobile_score, (int, float)) else ''
                desktop_color = get_score_color(desktop_score) if isinstance(desktop_score, (int, float)) else ''
                
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
        
        # Schema.org részletek
        if schema_data.get("details"):
            html_content += """
            <details style="margin-top: 20px;">
                <summary style="cursor: pointer; font-weight: 600; color: #667eea;">📋 Schema.org részletek</summary>
                <div style="margin-top: 10px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
"""
            for detail in schema_data.get("details", [])[:5]:  # Max 5 schema
                html_content += f"""
                    <div style="margin: 5px 0;">
                        • {detail.get('type', 'Unknown')} 
                        {' 🖼️' if detail.get('has_image') else ''}
                        {' ⭐' if detail.get('has_rating') else ''}
                    </div>
"""
            html_content += """
                </div>
            </details>
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
        
        # Schema chart
        if schema_count and any(schema_count.values()):
            schema_labels = list(schema_count.keys())
            schema_values = list(schema_count.values())
            
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
            # Ha nincs schema, üres chart
            html_content += f"""
    // Schema Chart - {uid} (nincs adat)
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
                    text: 'Schema.org Típusok'
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