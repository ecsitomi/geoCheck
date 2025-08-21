import json
import re
from datetime import datetime
from typing import Dict, List
import html

# -----------------------------
# Helper functions (stable API)
# -----------------------------

def level_from_score(score: float) -> str:
    """AI Readiness szint meghatározása pontszám alapján"""
    if score is None:
        return "Ismeretlen"
    if score >= 85: return "Kiváló"
    if score >= 60: return "Jó"
    if score >= 40: return "Közepes"
    return "Fejlesztendő"

def badge_class(score: float) -> str:
    """CSS osztály meghatározása pontszám alapján (Bootstrap színekhez igazítva)"""
    if score is None:
        return "bg-warning-subtle text-warning-emphasis"
    if score >= 85: return "bg-success text-white"
    if score >= 60: return "bg-teal text-white"   # custom via inline CSS
    if score >= 40: return "bg-warning text-dark"
    return "bg-danger text-white"

def fmt(x, digits=1):
    """Biztonságos formázás egységes kijelzéshez"""
    try:
        return f"{float(x):.{digits}f}"
    except Exception:
        return "—"

def detect_enhanced_analysis(data: List[Dict]) -> Dict:
    """Automatikus enhanced vs standard felismerés"""
    if not data:
        return {"is_enhanced": False, "enhancement_stats": {}}
    valid_results = [r for r in data if isinstance(r, dict) and 'ai_readiness_score' in r and 'error' not in r]
    ai_enhanced_count = len([r for r in valid_results if r.get('ai_content_evaluation')])
    schema_enhanced_count = len([r for r in valid_results if r.get('schema', {}).get('validation_status') == 'enhanced'])
    cached_count = len([r for r in valid_results if r.get('cached')])
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
    return {"is_enhanced": is_enhanced, "enhancement_stats": enhancement_stats}

# --------------------------------
# Explanations (Mi mit jelent?)
# --------------------------------

EXPLAIN = {
    "ai_readiness_score": "Összesített 0–100 pontszám. Források: tartalomszerkezet, entitásjelölés, frissesség, hivatkozások, formázás, mélység és beszélgetősség.",
    "weighted_average": "AI-metrikák súlyozott átlaga. Nem azonos az AI Readiness-szel, de jól jelzi az AI-barát tartalom minőségét.",
    "meta_title": "Title tag hossza és optimalizáltsága. Ajánlott 30–60 karakter.",
    "meta_description": "Meta description hossza és megléte. Ajánlott 120–160 karakter.",
    "crawlability": "Robots.txt és sitemap megléte, HTML-méret (KB).",
    "mobile": "Viewport, reszponzív képek és mobilbarát megjelenés.",
    "schema": "Schema.org típusok száma és Google validáció.",
    "headings": "H1–H6 címsorok eloszlása, hierarchia épsége.",
    "ai_enhanced": "Speciális AI értékelések (olvashatóság, faktualitás, platform-kompatibilitás).",
    "content_quality": "Olvashatóság, kulcsszavak, mélység, tekintély, szemantikai gazdagság, összminőség.",
    "platforms": "ChatGPT, Claude, Gemini, Bing Chat kompatibilitás és AI javaslatok.",
    "psi": "PageSpeed Insights (mobil/desktop) teljesítménypontszámok, ha elérhetőek."
}

def help_icon(title_key: str):
    text = html.escape(EXPLAIN.get(title_key, ""))
    return f'<span class="ms-1" data-bs-toggle="tooltip" title="{text}">❓</span>' if text else ""

# --------------------------------
# HTML report (Bootstrap 5)
# --------------------------------

def generate_html_report(json_file: str = "ai_readiness_full_report.json",
                         output_file: str = "report.html") -> None:
    """
    Bootstrap-alapú, reszponzív HTML jelentés.
    A függvény aláírása és az output fájlnév megegyezik a korábbival.
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

    detection = detect_enhanced_analysis(data)
    is_enhanced = detection["is_enhanced"]
    enhancement_stats = detection["enhancement_stats"]

    valid_results = [r for r in data if isinstance(r, dict) and 'ai_readiness_score' in r and 'error' not in r]
    avg_score = sum(r.get('ai_readiness_score', 0) for r in valid_results) / len(valid_results) if valid_results else 0.0

    report_title = "Enhanced GEO AI Readiness Report" if is_enhanced else "GEO AI Readiness Report"

    primary = "#0d6efd"  # Bootstrap primary
    secondary = "#6610f2"

    # HTML head (Bootstrap + Chart.js)
    html_head = f"""
<!doctype html>
<html lang="hu">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(report_title)} – {datetime.now().strftime('%Y-%m-%d')}</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  body {{ background: linear-gradient(135deg, {primary} 0%, {secondary} 100%); }}
  .container-max {{ max-width: 1400px; }}
  .card-blur {{ backdrop-filter: blur(6px); }}
  .score-badge {{ font-weight:700; font-size:1.1rem; }}
  .bg-teal {{ background-color: #20c997 !important; }}
  .metric-label small{{ color:#6c757d; }}
  .nav-tabs .nav-link.active{{ font-weight:600; }}
  .kpi {{ font-size:1.75rem; font-weight:700; }}
  .muted {{ color:#6c757d; }}
  .chip {{ border-radius:50rem; padding:.25rem .6rem; font-size:.8rem; }}
  .sticky-header {{ position: sticky; top: 0; z-index: 1020; }}
</style>
</head>
<body class="bg-light">
<div class="container container-max py-4">
"""

    # Header
    header_html = f"""
<header class="sticky-header">
  <div class="card shadow-sm border-0">
    <div class="card-body d-flex flex-wrap align-items-center gap-3">
      <div class="flex-grow-1">
        <h1 class="h3 mb-1">{html.escape(report_title)}</h1>
        <div class="text-muted">Generative Engine Optimization elemzés – {datetime.now().strftime('%Y. %m. %d. %H:%M')}</div>
      </div>
      {"<span class='chip bg-primary text-white'><i class='bi bi-robot me-1'></i>AI Enhanced</span>" if is_enhanced else ""}
      <a href="ai_readiness_report.csv" class="btn btn-outline-primary"><i class="bi bi-download me-1"></i>CSV letöltés</a>
      <button class="btn btn-secondary" data-bs-toggle="modal" data-bs-target="#glossaryModal"><i class="bi bi-question-circle me-1"></i>Mi mit jelent?</button>
    </div>
  </div>
</header>
"""

    # Summary KPIs
    summary_html = f"""
<section class="my-3">
  <div class="row g-3">
    <div class="col-6 col-md-3">
      <div class="card border-0 shadow-sm">
        <div class="card-body">
          <div class="muted">Elemzett oldalak</div>
          <div class="kpi">{len(data)}</div>
        </div>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="card border-0 shadow-sm">
        <div class="card-body">
          <div class="muted">Átlagos AI Readiness {help_icon("ai_readiness_score")}</div>
          <div class="kpi">{fmt(avg_score,1)}</div>
        </div>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="card border-0 shadow-sm">
        <div class="card-body">
          <div class="muted">Kiváló (≥85)</div>
          <div class="kpi">{sum(1 for s in valid_results if s.get('ai_readiness_score',0)>=85)}</div>
        </div>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="card border-0 shadow-sm">
        <div class="card-body">
          <div class="muted">Fejlesztendő (&lt;40)</div>
          <div class="kpi">{sum(1 for s in valid_results if s.get('ai_readiness_score',0)<40)}</div>
        </div>
      </div>
    </div>
  </div>
  {"".join([
    f"<div class='mt-3 d-flex flex-wrap gap-2'>"
    f"<span class='chip bg-primary text-white'><i class='bi bi-cpu me-1'></i>AI enhanced: {enhancement_stats.get('ai_enhanced_count',0)}</span>"
    f"<span class='chip bg-info text-dark'><i class='bi bi-diagram-3 me-1'></i>Schema enhanced: {enhancement_stats.get('schema_enhanced_count',0)}</span>"
    f"<span class='chip bg-secondary text-white'><i class='bi bi-hdd-network me-1'></i>Cache hit: {enhancement_stats.get('cache_hit_rate',0)}%</span>"
    f"</div>"
  ]) if is_enhanced else ""}
</section>
"""

    # Accordion for sites
    sites_html = '<div class="accordion" id="sitesAccordion">'
    for idx, site in enumerate(data):
        if not isinstance(site, dict):
            continue
        url = site.get("url", "N/A")
        uid = f"site_{idx}_{re.sub(r'[^a-zA-Z0-9]', '_', url)}"
        score = site.get("ai_readiness_score", 0)
        score_class = badge_class(score)

        meta = site.get("meta_and_headings", {}) or {}
        schema = site.get("schema", {}) or {}
        mobile = site.get("mobile_friendly", {}) or {}
        ai_summary = site.get("ai_metrics_summary", {}) or {}
        content_quality = site.get("content_quality", {}) or {}
        ai_eval = site.get("ai_content_evaluation", {}) or {}
        ai_readability = site.get("ai_readability", {}) or {}
        ai_factual = site.get("ai_factual_check", {}) or {}
        psi = site.get("pagespeed_insights", {}) or {}

        has_ai_eval = bool(ai_eval)
        has_schema_enhanced = schema.get("validation_status") == "enhanced"
        was_cached = bool(site.get("cached"))

        # Quick metrics
        title = meta.get("title")
        desc = meta.get("description")
        title_len = len(title) if title else 0
        desc_len = len(desc) if desc else 0

        heading_counts = {
            "H1": meta.get("h1", meta.get("headings", {}).get("h1", 0) if isinstance(meta.get("headings"), dict) else 0),
            "H2": meta.get("h2", meta.get("headings", {}).get("h2", 0) if isinstance(meta.get("headings"), dict) else 0),
            "H3": meta.get("h3", meta.get("headings", {}).get("h3", 0) if isinstance(meta.get("headings"), dict) else 0),
            "H4": meta.get("h4", meta.get("headings", {}).get("h4", 0) if isinstance(meta.get("headings"), dict) else 0),
            "H5": meta.get("h5", meta.get("headings", {}).get("h5", 0) if isinstance(meta.get("headings"), dict) else 0),
            "H6": meta.get("h6", meta.get("headings", {}).get("h6", 0) if isinstance(meta.get("headings"), dict) else 0),
        }

        schema_count = schema.get("count", {}) or {}

        # Header with chips
        chips = []
        if has_ai_eval: chips.append("<span class='chip bg-primary text-white'><i class='bi bi-robot'></i> AI</span>")
        if has_schema_enhanced: chips.append("<span class='chip bg-info text-dark'><i class='bi bi-diagram-3'></i> Schema</span>")
        if was_cached: chips.append("<span class='chip bg-secondary text-white'><i class='bi bi-hdd-network'></i> Cache</span>")
        chips_html = " ".join(chips)

        sites_html += f"""
  <div class="accordion-item">
    <h2 class="accordion-header" id="head-{uid}">
      <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-{uid}" aria-expanded="false" aria-controls="collapse-{uid}">
        <div class="d-flex w-100 align-items-center justify-content-between">
          <div class="me-3 text-truncate"><strong>{html.escape(url)}</strong></div>
          <div class="d-flex align-items-center gap-2">
            {chips_html}
            <span class="badge {score_class} score-badge">{fmt(score,0)}</span>
          </div>
        </div>
      </button>
    </h2>
    <div id="collapse-{uid}" class="accordion-collapse collapse" aria-labelledby="head-{uid}" data-bs-parent="#sitesAccordion">
      <div class="accordion-body">
        <ul class="nav nav-tabs" id="tabs-{uid}" role="tablist">
          <li class="nav-item" role="presentation">
            <button class="nav-link active" id="ov-{uid}" data-bs-toggle="tab" data-bs-target="#tab-ov-{uid}" type="button" role="tab">Áttekintés</button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="ai-{uid}" data-bs-toggle="tab" data-bs-target="#tab-ai-{uid}" type="button" role="tab">AI metrikák</button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="ct-{uid}" data-bs-toggle="tab" data-bs-target="#tab-ct-{uid}" type="button" role="tab">Tartalom</button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="pl-{uid}" data-bs-toggle="tab" data-bs-target="#tab-pl-{uid}" type="button" role="tab">Platformok</button>
          </li>
          {"<li class='nav-item' role='presentation'><button class='nav-link' id='se-{uid}' data-bs-toggle='tab' data-bs-target='#tab-se-{uid}' type='button' role='tab'>Schema</button></li>" if has_schema_enhanced else ""}
        </ul>

        <div class="tab-content pt-3" id="tab-content-{uid}">
          <!-- Overview -->
          <div class="tab-pane fade show active" id="tab-ov-{uid}" role="tabpanel">
            <div class="row g-3">
              <div class="col-md-4">
                <div class="card border-0 shadow-sm h-100">
                  <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                      <div class="metric-label">Meta adatok {help_icon("meta_title")}</div>
                      <span class="chip bg-light text-muted">HTML: {fmt(site.get('html_size_kb',0),1)} KB</span>
                    </div>
                    <hr class="my-2"/>
                    <div class="row small">
                      <div class="col-6">Title: <strong>{title_len}</strong> { "✅" if meta.get("title_optimal") else ("⚠️" if title_len else "❌") }</div>
                      <div class="col-6">Description: <strong>{desc_len}</strong> { "✅" if meta.get("description_optimal") else ("⚠️" if desc_len else "❌") }</div>
                      <div class="col-6 mt-1">OG tags: {"✅" if meta.get("has_og_tags") else "❌"}</div>
                      <div class="col-6 mt-1">Twitter Card: {"✅" if meta.get("has_twitter_card") else "❌"}</div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="col-md-4">
                <div class="card border-0 shadow-sm h-100">
                  <div class="card-body">
                    <div class="metric-label">Crawlability {help_icon("crawlability")}</div>
                    <hr class="my-2"/>
                    <div class="d-flex flex-column gap-1 small">
                      <div>Robots.txt: {"✅ Engedélyezett" if site.get("robots_txt", {}).get("can_fetch") else "❌ Tiltott"}</div>
                      <div>Sitemap: {"✅ Van" if site.get("sitemap", {}).get("exists") else "❌ Nincs"}</div>
                      <div>Mobilbarát: {"✅" if mobile.get("has_viewport") else "❌"}</div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="col-md-4">
                <div class="card border-0 shadow-sm h-100">
                  <div class="card-body">
                    <div class="metric-label">Címsorok {help_icon("headings")}</div>
                    <hr class="my-2"/>
                    <canvas id="head-chart-{uid}" height="160"></canvas>
                  </div>
                </div>
              </div>
            </div>

            <div class="row g-3 mt-1">
              <div class="col-md-6">
                <div class="card border-0 shadow-sm h-100">
                  <div class="card-body">
                    <div class="metric-label">Schema {help_icon("schema")}</div>
                    <hr class="my-2"/>
                    <div class="small">Google Validation: {"✅" if (schema.get("google_validation") or {}).get("is_valid") else "❌"} | Típusok: {sum((schema.get("count") or {}).values())}</div>
                    <canvas id="schema-chart-{uid}" height="180"></canvas>
                  </div>
                </div>
              </div>

              <div class="col-md-6">
                <div class="card border-0 shadow-sm h-100">
                  <div class="card-body">
                    <div class="metric-label">PageSpeed (ha van) {help_icon("psi")}</div>
                    <hr class="my-2"/>
                    <div class="d-flex gap-3 align-items-center">
                      <div class="flex-fill">
                        <div class="small">Mobil</div>
                        <div class="progress" role="progressbar" aria-label="PSI mobile">
                          <div class="progress-bar bg-success" style="width:{fmt((psi.get('mobile') or {}).get('performance',0),0)}%">{fmt((psi.get('mobile') or {}).get('performance',0),0)}%</div>
                        </div>
                      </div>
                      <div class="flex-fill">
                        <div class="small">Asztali</div>
                        <div class="progress" role="progressbar" aria-label="PSI desktop">
                          <div class="progress-bar bg-info" style="width:{fmt((psi.get('desktop') or {}).get('performance',0),0)}%">{fmt((psi.get('desktop') or {}).get('performance',0),0)}%</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- AI Metrics -->
          <div class="tab-pane fade" id="tab-ai-{uid}" role="tabpanel">
            <div class="row g-3">
              <div class="col-lg-5">
                <div class="card border-0 shadow-sm h-100">
                  <div class="card-body">
                    <div class="metric-label">AI Readiness összefoglaló {help_icon("ai_readiness_score")}</div>
                    <hr class="my-2"/>
                    <div class="row text-center">
                      <div class="col-6">
                        <div class="small text-muted">Összesített</div>
                        <div class="kpi">{fmt(score,0)}</div>
                      </div>
                      <div class="col-6">
                        <div class="small text-muted">Szint</div>
                        <div class="kpi">{level_from_score(score)}</div>
                      </div>
                    </div>
                    <div class="row g-2 mt-2">
                      <div class="col-12 small text-muted">AI Weighted átlag {help_icon("weighted_average")}:</div>
                      <div class="col-12">
                        <div class="progress" role="progressbar" aria-label="Weighted average">
                          <div class="progress-bar" style="width:{fmt(ai_summary.get('weighted_average',0),0)}%">{fmt(ai_summary.get('weighted_average',0),1)}%</div>
                        </div>
                      </div>
                    </div>
                    <div class="mt-3 small">
                      <strong>Erősségek:</strong> {", ".join(ai_summary.get("top_strengths", [])) or "—"}<br>
                      <strong>Fejlesztendő:</strong> {", ".join(ai_summary.get("improvement_areas", [])) or "—"}
                    </div>
                  </div>
                </div>
              </div>

              <div class="col-lg-7">
                <div class="card border-0 shadow-sm h-100">
                  <div class="card-body">
                    <div class="metric-label">AI Enhanced {help_icon("ai_enhanced")}</div>
                    <hr class="my-2"/>
                    {"<div class='small text-muted'>Nincs AI Enhanced adat.</div>" if not has_ai_eval else ""}
                    {"".join([
                      f"<div class='row g-2'>"
                      f"<div class='col-6 col-md-3'><div class='card text-center border-0 bg-light'><div class='card-body p-2'><div class='small text-muted'>Overall</div><div class='kpi'>{fmt(ai_eval.get('overall_ai_score',0),1)}</div></div></div></div>"
                      + "".join([f"<div class='col-6 col-md-3'><div class='card text-center border-0 bg-light'><div class='card-body p-2'><div class='small text-muted'>{html.escape(k.title())}</div><div class='kpi'>{fmt(v,1)}</div></div></div></div>" for k,v in (ai_eval.get('ai_quality_scores') or {}).items()])
                      + "</div>"
                    ]) if has_ai_eval else ""}
                    {"".join([
                      "<div class='row g-2 mt-2'>"
                      f"<div class='col-6'><div class='card border-0 bg-light'><div class='card-body p-2 small'><strong>Olvashatóság</strong><br>Clarity: {fmt(ai_readability.get('clarity_score',0),1)} | Engagement: {fmt(ai_readability.get('engagement_score',0),1)} | Structure: {fmt(ai_readability.get('structure_score',0),1)} | AI-friendly: {fmt(ai_readability.get('ai_friendliness',0),1)}</div></div></div>"
                      f"<div class='col-6'><div class='card border-0 bg-light'><div class='card-body p-2 small'><strong>Faktualitás</strong><br>Score: {fmt(ai_factual.get('factual_score',0),1)} | Hivatkozások: {(ai_factual.get('accuracy_indicators') or {}).get('citations_present',0)} | Szám+Mérték: {(ai_factual.get('accuracy_indicators') or {}).get('numbers_with_units',0)} | Bizalom: {html.escape(str(ai_factual.get('confidence_level','N/A')))}</div></div></div>"
                      "</div>"
                    ]) if (ai_readability or ai_factual) else ""}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Content -->
          <div class="tab-pane fade" id="tab-ct-{uid}" role="tabpanel">
            <div class="row g-3">
              <div class="col-md-4">
                <div class="card border-0 shadow-sm h-100">
                  <div class="card-body">
                    <div class="metric-label">Olvashatóság</div>
                    <hr class="my-2"/>
                    <div class="small">
                      Szószám: {(content_quality.get('readability') or {}).get('word_count',0)}<br>
                      Mondatok: {(content_quality.get('readability') or {}).get('sentence_count',0)}<br>
                      Átlag mondathossz: {fmt((content_quality.get('readability') or {}).get('avg_sentence_length',0),1)}<br>
                      Flesch: {(content_quality.get('readability') or {}).get('flesch_score',0)}<br>
                      Szint: {(content_quality.get('readability') or {}).get('readability_level','N/A')}<br>
                      Pontszám: {fmt((content_quality.get('readability') or {}).get('readability_score',0),1)}/100
                    </div>
                  </div>
                </div>
              </div>

              <div class="col-md-4">
                <div class="card border-0 shadow-sm h-100">
                  <div class="card-body">
                    <div class="metric-label">Kulcsszavak</div>
                    <hr class="my-2"/>
                    <div class="small">
                      Össz: {(content_quality.get('keyword_analysis') or {}).get('total_words',0)} | Egyedi: {(content_quality.get('keyword_analysis') or {}).get('unique_words',0)}<br>
                      Szókincs: {fmt(((content_quality.get('keyword_analysis') or {}).get('vocabulary_richness',0) or 0)*100,1)}%<br>
                      Top kulcsszavak:
                      <ul class="mb-0">
                        { "".join([f"<li>{html.escape(str(k[0]))}: {k[1]}×</li>" for k in ((content_quality.get('keyword_analysis') or {}).get('top_keywords',[])[:5]) if isinstance(k,(list,tuple)) and len(k)>=2]) or "<li>—</li>" }
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              <div class="col-md-4">
                <div class="card border-0 shadow-sm h-100">
                  <div class="card-body">
                    <div class="metric-label">Összesített minőség</div>
                    <hr class="my-2"/>
                    <div class="kpi">{fmt(content_quality.get('overall_quality_score',0),1)}/100</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Platforms -->
          <div class="tab-pane fade" id="tab-pl-{uid}" role="tabpanel">
            <div class="row g-3">
              {"".join([
                f"<div class='col-6 col-md-3'><div class='card border-0 shadow-sm h-100'>"
                f"<div class='card-body text-center'>"
                f"<div class='small text-muted'>{html.escape(name.upper())}</div>"
                f"<div class='kpi'>{fmt((pdata or {}).get('compatibility_score',0),0)}</div>"
                f"<div class='small'>Szint: {html.escape((pdata or {}).get('optimization_level','N/A'))}</div>"
                f"</div></div></div>"
                for name, pdata in (site.get('platform_analysis') or {}).items()
                if isinstance(pdata, dict) and name not in ('summary',)
              ]) or "<div class='small text-muted ps-3'>Nincs platform adat.</div>"}
            </div>
          </div>

          <!-- Schema enhanced (if any) -->
          {"".join([
            f"<div class='tab-pane fade' id='tab-se-{uid}' role='tabpanel'>"
            f"<div class='card border-0 shadow-sm'><div class='card-body'>"
            f"<div class='metric-label'>Google Validation</div><hr class='my-2'/>"
            f"<div class='small'>Valid: {'✅' if (schema.get('google_validation') or {}).get('is_valid') else '❌'} | Rich Results: {'✅' if (schema.get('google_validation') or {}).get('rich_results_eligible') else '❌'} | Schema Count: {(schema.get('google_validation') or {}).get('schema_count',0)}</div>"
            f"</div></div></div>"
          ]) if has_schema_enhanced else ""}
        </div>
      </div>
    </div>
  </div>
        """

        # JS to render charts for each site
        # Prepare data for headings and schema charts
        head_labels = list(heading_counts.keys())
        head_values = [heading_counts[k] or 0 for k in head_labels]
        filtered_schema = {k: v for k, v in (schema_count.items()) if v}

        sites_html += f"""
<script>
(function() {{
  const ctxH = document.getElementById('head-chart-{uid}');
  if (ctxH) {{
    new Chart(ctxH, {{
      type: 'bar',
      data: {{
        labels: {head_labels},
        datasets: [{{ label: 'Címsorok', data: {head_values} }}]
      }},
      options: {{
        responsive: true,
        plugins: {{ legend: {{ display: false }}, title: {{ display: false }} }},
        scales: {{ y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }} }}
      }}
    }});
  }}
  const sch = document.getElementById('schema-chart-{uid}');
  if (sch && {bool(filtered_schema)}) {{
    new Chart(sch, {{
      type: 'doughnut',
      data: {{
        labels: {list(filtered_schema.keys())},
        datasets: [{{ label: 'Schema típusok', data: {list(filtered_schema.values())} }}]
      }},
      options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom' }} }} }}
    }});
  }}
}})();
</script>
        """

    sites_html += "</div>"  # end accordion

    # Glossary modal
    glossary_items = "".join([
        f"<li class='list-group-item'><strong>{html.escape(k)}</strong><br><small class='text-muted'>{html.escape(v)}</small></li>"
        for k, v in EXPLAIN.items()
    ])
    glossary_html = f"""
<div class="modal fade" id="glossaryModal" tabindex="-1" aria-labelledby="glossaryLabel" aria-hidden="true">
  <div class="modal-dialog modal-lg modal-dialog-scrollable">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="glossaryLabel">Mi mit jelent?</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Bezárás"></button>
      </div>
      <div class="modal-body">
        <ul class="list-group">{glossary_items}</ul>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" data-bs-dismiss="modal">Bezárás</button>
      </div>
    </div>
  </div>
</div>
"""

    # Footer and scripts
    html_footer = f"""
{glossary_html}
</div> <!-- /container -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script>
  // Tooltips init
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  [...tooltipTriggerList].forEach(el => new bootstrap.Tooltip(el));
</script>
</body>
</html>
"""

    html_content = html_head + header_html + summary_html + sites_html + html_footer

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ {'Enhanced' if is_enhanced else 'Standard'} HTML jelentés elkészült: {output_file}")
    print(f"📊 Elemzett oldalak száma: {len(data)}")
    print(f"⭐ Átlagos AI-readiness score: {avg_score:.1f}/100")
    if is_enhanced:
        print(f"🤖 AI Enhanced eredmények: {enhancement_stats.get('ai_enhanced_count',0)} ({enhancement_stats.get('ai_enhanced_percentage',0)}%)")
        print(f"🏗️ Schema Enhanced eredmények: {enhancement_stats.get('schema_enhanced_count',0)} ({enhancement_stats.get('schema_enhanced_percentage',0)}%)")
        if enhancement_stats.get('cached_count', 0) > 0:
            print(f"💾 Cache találatok: {enhancement_stats.get('cached_count',0)} ({enhancement_stats.get('cache_hit_rate',0)}%)")

# --------------------------------
# CSV export (ugyanaz a struktúra)
# --------------------------------

def generate_csv_export(json_file: str = "ai_readiness_full_report.json",
                        output_file: str = "ai_readiness_report.csv") -> None:
    """Enhanced CSV export generálása – mezők megegyeznek a korábbi verzióval"""
    import csv
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Hiba: {e}")
        return

    detection = detect_enhanced_analysis(data)
    is_enhanced = detection["is_enhanced"]

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
        for site in data:
            if not isinstance(site, dict):
                continue
            meta = site.get("meta_and_headings", {}) or {}
            schema = site.get("schema", {}) or {}
            psi = site.get("pagespeed_insights", {}) or {}

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
                'H1 Count': meta.get('h1_count', meta.get('headings', {}).get('h1', 0) if isinstance(meta.get('headings'), dict) else 0),
                'Schema Count': sum((schema.get('count', {}) or {}).values()),
                'PSI Mobile': fmt((psi.get('mobile', {}) or {}).get('performance', 0), 1) if psi else '—',
                'PSI Desktop': fmt((psi.get('desktop', {}) or {}).get('performance', 0), 1) if psi else '—'
            }

            if is_enhanced:
                ai_content_eval = site.get('ai_content_evaluation', {}) or {}
                row.update({
                    'AI Enhanced': bool(ai_content_eval),
                    'AI Overall Score': fmt(ai_content_eval.get('overall_ai_score', 0), 1) if ai_content_eval else '—',
                    'Schema Enhanced': schema.get('validation_status') == 'enhanced',
                    'Schema Completeness': fmt(schema.get('schema_completeness_score', 0), 1),
                    'Cached': site.get('cached', False),
                    'Google Validation': (schema.get('google_validation') or {}).get('is_valid', False)
                })

            writer.writerow(row)

    print(f"✅ {'Enhanced' if is_enhanced else 'Standard'} CSV export elkészült: {output_file}")

# Példa futtatás (interface változatlan)
if __name__ == "__main__":
    generate_html_report()
    generate_csv_export()