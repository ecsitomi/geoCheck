import json

def generate_html_report(json_file="ai_readiness_full_report.json", output_file="report.html"):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    html_content = """
<!DOCTYPE html>
<html lang="hu">
<head>
<meta charset="UTF-8">
<title>AI Readiness Report</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body { font-family: Arial, sans-serif; margin: 20px; background-color:#f4f4f9; }
h1 { text-align:center; color:#333; }
.chart-container { width: 80%; margin: auto; }
.table-container { width: 90%; margin: auto; margin-top: 40px; }
table { border-collapse: collapse; width: 100%; background:white; }
th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
th { background-color: #eee; }
</style>
</head>
<body>
<h1>AI Readiness Report</h1>
"""

    for site in data:
        url = site.get("url")
        score = site.get("ai_readiness_score", 0)
        html_content += f"<h2>{url}</h2>\n"
        html_content += f"<p><strong>AI Readiness Score:</strong> {score}/100</p>\n"

        # Robots, Sitemap, Mobile
        html_content += "<ul>"
        html_content += f"<li>Robots.txt: {site.get('robots_txt', {}).get('can_fetch')}</li>"
        html_content += f"<li>Sitemap.xml: {site.get('sitemap', {}).get('exists')}</li>"
        html_content += f"<li>Mobile-friendly: {site.get('mobile_friendly')}</li>"
        html_content += "</ul>\n"

        # Headings
        headings = site.get("headings", {})
        html_content += "<div class='chart-container'><canvas id='headingChart{0}'></canvas></div>\n".format(url.replace('.', '_'))

        # Schema
        schema = site.get("schema_count", {})
        html_content += "<div class='chart-container'><canvas id='schemaChart{0}'></canvas></div>\n".format(url.replace('.', '_'))

        # PageSpeed Insights
        psi = site.get("pagespeed_insights", {})
        if psi:
            html_content += "<div class='chart-container'><canvas id='psiMobile{0}'></canvas></div>\n".format(url.replace('.', '_'))
            html_content += "<div class='chart-container'><canvas id='psiDesktop{0}'></canvas></div>\n".format(url.replace('.', '_'))

        # Table for meta
        html_content += "<div class='table-container'>"
        html_content += "<table><tr><th>Title</th><th>Description</th></tr>"
        html_content += f"<tr><td>{site.get('title')}</td><td>{site.get('description')}</td></tr>"
        html_content += "</table></div>"

    # JavaScript for charts
    html_content += "<script>\n"
    for site in data:
        url = site.get("url")
        uid = url.replace('.', '_')

        # Headings chart
        headings = site.get("headings", {})
        html_content += f"""
new Chart(document.getElementById('headingChart{uid}'), {{
    type: 'bar',
    data: {{
        labels: {list(headings.keys())},
        datasets: [{{
            label: 'Headings Count',
            data: {list(headings.values())},
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        }}]
    }},
    options: {{ scales: {{ y: {{ beginAtZero: true }} }} }}
}});
"""

        # Schema chart
        schema = site.get("schema_count", {})
        html_content += f"""
new Chart(document.getElementById('schemaChart{uid}'), {{
    type: 'pie',
    data: {{
        labels: {list(schema.keys())},
        datasets: [{{
            label: 'Schema Count',
            data: {list(schema.values())},
            backgroundColor: [
                'rgba(255, 99, 132, 0.6)',
                'rgba(54, 162, 235, 0.6)',
                'rgba(255, 206, 86, 0.6)',
                'rgba(75, 192, 192, 0.6)'
            ],
            borderColor: 'white',
            borderWidth: 1
        }}]
    }}
}});
"""

        # PageSpeed Insights Mobile
        psi_mobile = site.get("pagespeed_insights", {}).get("mobile", {})
        if psi_mobile:
            html_content += f"""
new Chart(document.getElementById('psiMobile{uid}'), {{
    type: 'bar',
    data: {{
        labels: {list(psi_mobile.keys())},
        datasets: [{{
            label: 'Mobile PSI Score',
            data: {list(psi_mobile.values())},
            backgroundColor: 'rgba(255, 159, 64, 0.6)',
            borderColor: 'rgba(255, 159, 64, 1)',
            borderWidth: 1
        }}]
    }},
    options: {{ scales: {{ y: {{ beginAtZero: true, max:100 }} }} }}
}});
"""

        # PageSpeed Insights Desktop
        psi_desktop = site.get("pagespeed_insights", {}).get("desktop", {})
        if psi_desktop:
            html_content += f"""
new Chart(document.getElementById('psiDesktop{uid}'), {{
    type: 'bar',
    data: {{
        labels: {list(psi_desktop.keys())},
        datasets: [{{
            label: 'Desktop PSI Score',
            data: {list(psi_desktop.values())},
            backgroundColor: 'rgba(153, 102, 255, 0.6)',
            borderColor: 'rgba(153, 102, 255, 1)',
            borderWidth: 1
        }}]
    }},
    options: {{ scales: {{ y: {{ beginAtZero: true, max:100 }} }} }}
}});
"""

    html_content += "</script>\n</body>\n</html>"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML report generated: {output_file}")

# --- Példa futtatás ---
if __name__ == "__main__":
    generate_html_report()
