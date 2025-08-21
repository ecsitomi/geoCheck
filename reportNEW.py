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
    Modern HTML jelentés generálása professzionális UI/UX dizájnnal
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
    detection_result = detect_enhanced_analysis(data)
    is_enhanced = detection_result["is_enhanced"]
    enhancement_stats = detection_result["enhancement_stats"]
    
    # Valid results
    valid_results = [r for r in data if isinstance(r, dict) and 'ai_readiness_score' in r and 'error' not in r]
    avg_score = sum(r['ai_readiness_score'] for r in valid_results) / len(valid_results) if valid_results else 0
    
    # Report címek és stílus
    report_title = "Enhanced GEO AI Readiness Report" if is_enhanced else "GEO AI Readiness Report"
    
    # HTML template modern dizájnnal
    html_content = f"""
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_title} - {datetime.now().strftime('%Y-%m-%d')}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {{
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --primary-light: #818cf8;
            --secondary: #ec4899;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --info: #3b82f6;
            --dark: #1e293b;
            --light: #f8fafc;
            --gray: #64748b;
            --gray-light: #e2e8f0;
            --gray-dark: #475569;
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
            --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.15);
            --radius: 12px;
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: var(--dark);
            line-height: 1.6;
            position: relative;
        }}
        
        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
            pointer-events: none;
            z-index: 0;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
            position: relative;
            z-index: 1;
        }}
        
        /* Modern Header */
        .header {{
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 2.5rem;
            margin-bottom: 2rem;
            box-shadow: var(--shadow-xl), 0 0 100px rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary), var(--secondary), var(--primary));
            background-size: 200% 100%;
            animation: gradient 3s ease infinite;
        }}
        
        @keyframes gradient {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        
        .header-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 2rem;
            flex-wrap: wrap;
        }}
        
        .header-title {{
            flex: 1;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .enhanced-badge {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 0.5rem 1.2rem;
            border-radius: 50px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            box-shadow: var(--shadow-md);
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}
        
        .header-meta {{
            color: var(--gray);
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .header-meta i {{
            color: var(--primary);
        }}
        
        /* Summary Cards */
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .summary-card {{
            background: white;
            border-radius: var(--radius);
            padding: 1.8rem;
            box-shadow: var(--shadow-md);
            transition: var(--transition);
            position: relative;
            overflow: hidden;
            cursor: help;
        }}
        
        .summary-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--primary);
            transform: scaleX(0);
            transition: transform 0.3s;
        }}
        
        .summary-card:hover {{
            transform: translateY(-5px);
            box-shadow: var(--shadow-xl);
        }}
        
        .summary-card:hover::before {{
            transform: scaleX(1);
        }}
        
        .summary-card.enhanced {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
        }}
        
        .summary-card-icon {{
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            margin-bottom: 1rem;
            background: rgba(99, 102, 241, 0.1);
            color: var(--primary);
        }}
        
        .summary-card.enhanced .summary-card-icon {{
            background: rgba(255, 255, 255, 0.2);
            color: white;
        }}
        
        .summary-card-value {{
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            color: var(--dark);
        }}
        
        .summary-card.enhanced .summary-card-value {{
            color: white;
        }}
        
        .summary-card-label {{
            font-size: 0.9rem;
            color: var(--gray);
            font-weight: 500;
        }}
        
        .summary-card.enhanced .summary-card-label {{
            color: rgba(255, 255, 255, 0.9);
        }}
        
        /* Tooltip */
        .tooltip {{
            position: relative;
            display: inline-block;
            cursor: help;
        }}
        
        .tooltip-icon {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: var(--gray-light);
            color: var(--gray);
            font-size: 0.7rem;
            margin-left: 0.5rem;
            cursor: pointer;
            transition: var(--transition);
        }}
        
        .tooltip-icon:hover {{
            background: var(--primary);
            color: white;
        }}
        
        .tooltip-content {{
            visibility: hidden;
            opacity: 0;
            position: absolute;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            background: var(--dark);
            color: white;
            padding: 0.8rem 1rem;
            border-radius: 8px;
            font-size: 0.85rem;
            white-space: nowrap;
            max-width: 300px;
            z-index: 1000;
            box-shadow: var(--shadow-lg);
            transition: var(--transition);
            pointer-events: none;
        }}
        
        .tooltip:hover .tooltip-content {{
            visibility: visible;
            opacity: 1;
        }}
        
        .tooltip-content::after {{
            content: '';
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            border: 6px solid transparent;
            border-top-color: var(--dark);
        }}
        
        /* Site Cards */
        .site-card {{
            background: white;
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: var(--shadow-lg);
            overflow: hidden;
            transition: var(--transition);
        }}
        
        .site-card:hover {{
            box-shadow: var(--shadow-xl), 0 0 50px rgba(99, 102, 241, 0.1);
        }}
        
        .site-header {{
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            padding: 2rem;
            color: white;
            position: relative;
        }}
        
        .site-header-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 2rem;
            flex-wrap: wrap;
        }}
        
        .site-url {{
            font-size: 1.6rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .site-url i {{
            font-size: 1.2rem;
            opacity: 0.8;
        }}
        
        .score-display {{
            position: relative;
            width: 100px;
            height: 100px;
        }}
        
        .score-circle {{
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: white;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            box-shadow: var(--shadow-lg);
        }}
        
        .score-value {{
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .score-label {{
            position: absolute;
            bottom: -25px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 0.75rem;
            font-weight: 600;
            background: rgba(255, 255, 255, 0.9);
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            color: var(--primary);
        }}
        
        /* Tabs */
        .tabs {{
            display: flex;
            gap: 0;
            background: var(--light);
            padding: 0.5rem;
            border-radius: 12px;
            margin: 1.5rem;
            overflow-x: auto;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.06);
        }}
        
        .tab {{
            padding: 0.8rem 1.5rem;
            background: transparent;
            border: none;
            cursor: pointer;
            font-weight: 600;
            color: var(--gray);
            transition: var(--transition);
            border-radius: 8px;
            white-space: nowrap;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .tab i {{
            font-size: 0.9rem;
        }}
        
        .tab:hover {{
            color: var(--primary);
            background: rgba(99, 102, 241, 0.05);
        }}
        
        .tab.active {{
            background: white;
            color: var(--primary);
            box-shadow: var(--shadow-md);
        }}
        
        .tab-content {{
            display: none;
            padding: 2rem;
            animation: fadeIn 0.3s ease-in;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        /* Metrics Grid */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }}
        
        .metric-card {{
            background: var(--light);
            padding: 1.5rem;
            border-radius: var(--radius);
            border: 1px solid var(--gray-light);
            transition: var(--transition);
            position: relative;
        }}
        
        .metric-card:hover {{
            transform: translateY(-3px);
            box-shadow: var(--shadow-md);
            border-color: var(--primary);
        }}
        
        .metric-card.ai-enhanced {{
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(236, 72, 153, 0.05));
            border-color: var(--primary);
        }}
        
        .metric-header {{
            display: flex;
            align-items: center;
            gap: 0.8rem;
            margin-bottom: 1rem;
            font-weight: 600;
            color: var(--dark);
        }}
        
        .metric-icon {{
            width: 36px;
            height: 36px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--primary);
            color: white;
            font-size: 1rem;
        }}
        
        .metric-content {{
            color: var(--gray-dark);
            font-size: 0.9rem;
            line-height: 1.8;
        }}
        
        .metric-item {{
            display: flex;
            justify-content: space-between;
            padding: 0.3rem 0;
            border-bottom: 1px solid var(--gray-light);
        }}
        
        .metric-item:last-child {{
            border-bottom: none;
        }}
        
        .metric-label {{
            color: var(--gray);
        }}
        
        .metric-value {{
            font-weight: 600;
            color: var(--dark);
        }}
        
        .metric-value.success {{ color: var(--success); }}
        .metric-value.warning {{ color: var(--warning); }}
        .metric-value.danger {{ color: var(--danger); }}
        
        /* Platform Cards */
        .platform-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }}
        
        .platform-card {{
            background: white;
            padding: 1.5rem;
            border-radius: var(--radius);
            text-align: center;
            border: 2px solid var(--gray-light);
            transition: var(--transition);
            position: relative;
            overflow: hidden;
        }}
        
        .platform-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--gray-light);
            transition: var(--transition);
        }}
        
        .platform-card:hover {{
            transform: translateY(-5px);
            box-shadow: var(--shadow-lg);
            border-color: var(--primary);
        }}
        
        .platform-card:hover::before {{
            background: linear-gradient(90deg, var(--primary), var(--secondary));
        }}
        
        .platform-logo {{
            width: 48px;
            height: 48px;
            margin: 0 auto 1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            color: var(--primary);
        }}
        
        .platform-name {{
            font-weight: 700;
            color: var(--dark);
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
        }}
        
        .platform-score {{
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0.5rem 0;
        }}
        
        .platform-level {{
            font-size: 0.85rem;
            color: var(--gray);
            font-weight: 500;
            margin-top: 0.5rem;
        }}
        
        /* Fix Cards */
        .fix-card {{
            background: white;
            border-radius: var(--radius);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border-left: 4px solid var(--primary);
            box-shadow: var(--shadow-md);
            transition: var(--transition);
        }}
        
        .fix-card:hover {{
            transform: translateX(5px);
            box-shadow: var(--shadow-lg);
        }}
        
        .fix-card.critical {{
            border-left-color: var(--danger);
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.05), rgba(239, 68, 68, 0.02));
        }}
        
        .fix-card.warning {{
            border-left-color: var(--warning);
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.05), rgba(245, 158, 11, 0.02));
        }}
        
        .fix-card.info {{
            border-left-color: var(--info);
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(59, 130, 246, 0.02));
        }}
        
        .fix-card.schema {{
            border-left-color: var(--warning);
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.05), rgba(245, 158, 11, 0.02));
        }}
        
        .fix-card.content {{
            border-left-color: var(--info);
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(59, 130, 246, 0.02));
        }}
        
        .fix-card.seo {{
            border-left-color: var(--success);
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.05), rgba(16, 185, 129, 0.02));
        }}
        
        .fix-header {{
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
        }}
        
        .fix-icon {{
            width: 40px;
            height: 40px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--primary);
            color: white;
        }}
        
        .fix-card.critical .fix-icon {{ background: var(--danger); }}
        .fix-card.warning .fix-icon {{ background: var(--warning); }}
        .fix-card.info .fix-icon {{ background: var(--info); }}
        
        .fix-title {{
            font-weight: 700;
            color: var(--dark);
            font-size: 1.1rem;
        }}
        
        .fix-content {{
            color: var(--gray-dark);
            line-height: 1.6;
            margin-bottom: 1rem;
        }}
        
        .fix-code {{
            background: var(--dark);
            color: #e2e8f0;
            padding: 1rem;
            border-radius: 8px;
            font-family: 'Fira Code', 'SF Mono', monospace;
            font-size: 0.85rem;
            overflow-x: auto;
            margin: 1rem 0;
            position: relative;
        }}
        
        .fix-code::before {{
            content: 'CODE';
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            background: var(--primary);
            color: white;
            font-size: 0.7rem;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-family: 'Inter', sans-serif;
        }}
        
        /* Charts */
        .chart-container {{
            background: white;
            padding: 1.5rem;
            border-radius: var(--radius);
            box-shadow: var(--shadow-md);
            margin: 1rem 0;
        }}
        
        .charts-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
            margin: 2rem 0;
        }}
        
        /* Progress Bar */
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: var(--gray-light);
            border-radius: 10px;
            overflow: hidden;
            margin: 0.5rem 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            transition: width 0.5s ease;
            border-radius: 10px;
        }}
        
        /* Buttons */
        .btn {{
            padding: 0.8rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white;
            box-shadow: var(--shadow-md);
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }}
        
        /* Footer */
        .footer {{
            text-align: center;
            padding: 3rem 0;
            color: white;
            margin-top: 4rem;
        }}
        
        .footer-logo {{
            font-size: 3rem;
            margin-bottom: 1rem;
            opacity: 0.8;
        }}
        
        .footer-text {{
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}
        
        .footer-meta {{
            font-size: 0.9rem;
            opacity: 0.8;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}
            
            .header h1 {{
                font-size: 1.8rem;
            }}
            
            .summary-grid {{
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 1rem;
            }}
            
            .metrics-grid {{
                grid-template-columns: 1fr;
            }}
            
            .platform-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            .charts-row {{
                grid-template-columns: 1fr;
            }}
            
            .tabs {{
                overflow-x: auto;
            }}
            
            .site-header-content {{
                flex-direction: column;
                text-align: center;
            }}
        }}
        
        /* Animations */
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateX(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}
        
        .animate-slide {{
            animation: slideIn 0.5s ease;
        }}
        
        /* Utilities */
        .text-success {{ color: var(--success); }}
        .text-warning {{ color: var(--warning); }}
        .text-danger {{ color: var(--danger); }}
        .text-primary {{ color: var(--primary); }}
        .text-muted {{ color: var(--gray); }}
        
        .bg-success {{ background: var(--success); }}
        .bg-warning {{ background: var(--warning); }}
        .bg-danger {{ background: var(--danger); }}
        .bg-primary {{ background: var(--primary); }}
        
        .badge {{
            display: inline-flex;
            align-items: center;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            gap: 0.3rem;
        }}
        
        .badge-success {{
            background: rgba(16, 185, 129, 0.1);
            color: var(--success);
        }}
        
        .badge-warning {{
            background: rgba(245, 158, 11, 0.1);
            color: var(--warning);
        }}
        
        .badge-danger {{
            background: rgba(239, 68, 68, 0.1);
            color: var(--danger);
        }}
        
        .badge-primary {{
            background: rgba(99, 102, 241, 0.1);
            color: var(--primary);
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header animate-slide">
            <div class="header-content">
                <div class="header-title">
                    <h1>
                        <i class="fas fa-chart-line"></i>
                        {report_title}
                        {f'<span class="enhanced-badge"><i class="fas fa-rocket"></i> AI ENHANCED</span>' if is_enhanced else ''}
                    </h1>
                    <div class="header-meta">
                        <i class="fas fa-calendar"></i>
                        {datetime.now().strftime('%Y. %m. %d. %H:%M')}
                        <span>•</span>
                        <i class="fas fa-globe"></i>
                        Generative Engine Optimization Elemzés
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Summary Cards -->
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-card-icon">
                    <i class="fas fa-globe"></i>
                </div>
                <div class="summary-card-value">{len(data)}</div>
                <div class="summary-card-label">
                    Elemzett oldalak
                    <span class="tooltip">
                        <i class="fas fa-question-circle tooltip-icon"></i>
                        <span class="tooltip-content">Az elemzésbe bevont weboldalak száma</span>
                    </span>
                </div>
            </div>
            
            <div class="summary-card">
                <div class="summary-card-icon">
                    <i class="fas fa-tachometer-alt"></i>
                </div>
                <div class="summary-card-value">{fmt(avg_score, 1)}</div>
                <div class="summary-card-label">
                    Átlagos AI Score
                    <span class="tooltip">
                        <i class="fas fa-question-circle tooltip-icon"></i>
                        <span class="tooltip-content">Az oldalak AI-barátságának átlagos értéke (0-100)</span>
                    </span>
                </div>
            </div>
            
            <div class="summary-card">
                <div class="summary-card-icon">
                    <i class="fas fa-trophy"></i>
                </div>
                <div class="summary-card-value">{sum(1 for s in valid_results if s.get('ai_readiness_score', 0) >= 70)}</div>
                <div class="summary-card-label">
                    Kiváló oldalak
                    <span class="tooltip">
                        <i class="fas fa-question-circle tooltip-icon"></i>
                        <span class="tooltip-content">70+ pontot elért, AI-optimalizált oldalak</span>
                    </span>
                </div>
            </div>
            
            <div class="summary-card">
                <div class="summary-card-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <div class="summary-card-value">{sum(1 for s in valid_results if s.get('ai_readiness_score', 0) < 50)}</div>
                <div class="summary-card-label">
                    Fejlesztendő
                    <span class="tooltip">
                        <i class="fas fa-question-circle tooltip-icon"></i>
                        <span class="tooltip-content">50 pont alatti, optimalizálást igénylő oldalak</span>
                    </span>
                </div>
            </div>"""
    
    if is_enhanced:
        html_content += f"""
            <div class="summary-card enhanced">
                <div class="summary-card-icon">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="summary-card-value">{enhancement_stats['ai_enhanced_percentage']}%</div>
                <div class="summary-card-label">
                    AI Enhanced
                    <span class="tooltip">
                        <i class="fas fa-question-circle tooltip-icon"></i>
                        <span class="tooltip-content">Mély AI elemzéssel vizsgált oldalak aránya</span>
                    </span>
                </div>
            </div>
            
            <div class="summary-card enhanced">
                <div class="summary-card-icon">
                    <i class="fas fa-code"></i>
                </div>
                <div class="summary-card-value">{enhancement_stats['schema_enhanced_percentage']}%</div>
                <div class="summary-card-label">
                    Schema Enhanced
                    <span class="tooltip">
                        <i class="fas fa-question-circle tooltip-icon"></i>
                        <span class="tooltip-content">Részletes schema validációval ellenőrzött oldalak</span>
                    </span>
                </div>
            </div>"""
    
    html_content += """
        </div>
"""

    # Site Cards
    for idx, site in enumerate(data):
        if not isinstance(site, dict):
            continue
            
        url = site.get("url", "N/A")
        score = site.get("ai_readiness_score", 0)
        uid = f"site_{idx}_{re.sub(r'[^a-zA-Z0-9]', '_', url)}"
        
        # Enhanced jelzők
        has_ai_eval = bool(site.get('ai_content_evaluation'))
        has_schema_enhanced = site.get('schema', {}).get('validation_status') == 'enhanced'
        was_cached = site.get('cached', False)
        
        # Score level
        score_level = level_from_score(score)
        
        # Adatok
        meta_data = site.get("meta_and_headings", {})
        schema_data = site.get("schema", {})
        mobile = site.get("mobile_friendly", {})
        ai_metrics = site.get("ai_metrics", {})
        ai_metrics_summary = site.get("ai_metrics_summary", {})
        content_quality = site.get("content_quality", {})
        platform_analysis = site.get("platform_analysis", {})
        auto_fixes = site.get("auto_fixes", {})
        ai_content_evaluation = site.get("ai_content_evaluation", {})
        ai_readability = site.get("ai_readability", {})
        ai_factual_check = site.get("ai_factual_check", {})
        
        html_content += f"""
        <div class="site-card">
            <div class="site-header">
                <div class="site-header-content">
                    <div>
                        <div class="site-url">
                            <i class="fas fa-link"></i>
                            {html.escape(url)}
                        </div>
                        <div style="margin-top: 1rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">"""
        
        if has_ai_eval:
            html_content += '<span class="badge badge-primary"><i class="fas fa-robot"></i> AI Enhanced</span>'
        if has_schema_enhanced:
            html_content += '<span class="badge badge-success"><i class="fas fa-code"></i> Schema Enhanced</span>'
        if was_cached:
            html_content += '<span class="badge badge-warning"><i class="fas fa-database"></i> Cached</span>'
            
        html_content += f"""
                        </div>
                    </div>
                    <div class="score-display">
                        <div class="score-circle">
                            <div class="score-value">{fmt(score, 0)}</div>
                        </div>
                        <div class="score-label">{score_level}</div>
                    </div>
                </div>
            </div>
            
            <!-- Tabs -->
            <div class="tabs">
                <button class="tab active" onclick="showTab(event, '{uid}', 'overview')">
                    <i class="fas fa-chart-pie"></i> Áttekintés
                </button>
                <button class="tab" onclick="showTab(event, '{uid}', 'ai-metrics')">
                    <i class="fas fa-robot"></i> AI Metrikák
                </button>
                <button class="tab" onclick="showTab(event, '{uid}', 'content')">
                    <i class="fas fa-file-alt"></i> Tartalom
                </button>
                <button class="tab" onclick="showTab(event, '{uid}', 'platforms')">
                    <i class="fas fa-layer-group"></i> Platformok
                </button>
                <button class="tab" onclick="showTab(event, '{uid}', 'fixes')">
                    <i class="fas fa-wrench"></i> Javítások
                </button>
            </div>
            
            <!-- Overview Tab -->
            <div id="{uid}-overview" class="tab-content active">
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-header">
                            <div class="metric-icon">
                                <i class="fas fa-tags"></i>
                            </div>
                            <span>Meta Adatok
                                <span class="tooltip">
                                    <i class="fas fa-question-circle tooltip-icon"></i>
                                    <span class="tooltip-content">Az oldal meta információi, amelyek segítik a keresőmotorokat és AI rendszereket</span>
                                </span>
                            </span>
                        </div>
                        <div class="metric-content">"""
        
        # Meta adatok
        title = meta_data.get("title")
        description = meta_data.get("description")
        title_len = len(title) if title else 0
        desc_len = len(description) if description else 0
        
        html_content += f"""
                            <div class="metric-item">
                                <span class="metric-label">Title hossz:</span>
                                <span class="metric-value {('success' if 30 <= title_len <= 60 else 'warning' if title_len > 0 else 'danger')}">{title_len} kar</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Description hossz:</span>
                                <span class="metric-value {('success' if 120 <= desc_len <= 160 else 'warning' if desc_len > 0 else 'danger')}">{desc_len} kar</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">OG Tags:</span>
                                <span class="metric-value {('success' if meta_data.get('has_og_tags') else 'danger')}">
                                    {"✓ Van" if meta_data.get('has_og_tags') else "✗ Nincs"}
                                </span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Twitter Card:</span>
                                <span class="metric-value {('success' if meta_data.get('has_twitter_card') else 'danger')}">
                                    {"✓ Van" if meta_data.get('has_twitter_card') else "✗ Nincs"}
                                </span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-header">
                            <div class="metric-icon">
                                <i class="fas fa-sitemap"></i>
                            </div>
                            <span>Crawlability
                                <span class="tooltip">
                                    <i class="fas fa-question-circle tooltip-icon"></i>
                                    <span class="tooltip-content">Keresőmotorok és AI rendszerek számára való hozzáférhetőség</span>
                                </span>
                            </span>
                        </div>
                        <div class="metric-content">
                            <div class="metric-item">
                                <span class="metric-label">Robots.txt:</span>
                                <span class="metric-value {('success' if site.get('robots_txt', {}).get('can_fetch') else 'danger')}">
                                    {"✓ Engedélyezett" if site.get('robots_txt', {}).get('can_fetch') else "✗ Tiltott"}
                                </span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Sitemap:</span>
                                <span class="metric-value {('success' if site.get('sitemap', {}).get('exists') else 'warning')}">
                                    {"✓ Van" if site.get('sitemap', {}).get('exists') else "⚠ Nincs"}
                                </span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">HTML méret:</span>
                                <span class="metric-value">{fmt(site.get('html_size_kb', 0), 1)} KB</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-header">
                            <div class="metric-icon">
                                <i class="fas fa-mobile-alt"></i>
                            </div>
                            <span>Mobilbarát
                                <span class="tooltip">
                                    <i class="fas fa-question-circle tooltip-icon"></i>
                                    <span class="tooltip-content">Mobil eszközökön való megjelenés optimalizáltsága</span>
                                </span>
                            </span>
                        </div>
                        <div class="metric-content">
                            <div class="metric-item">
                                <span class="metric-label">Viewport:</span>
                                <span class="metric-value {('success' if mobile.get('has_viewport') else 'danger')}">
                                    {"✓ Van" if mobile.get('has_viewport') else "✗ Nincs"}
                                </span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Responsive képek:</span>
                                <span class="metric-value {('success' if mobile.get('responsive_images') else 'warning')}">
                                    {"✓ Igen" if mobile.get('responsive_images') else "⚠ Nem"}
                                </span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="metric-card {'ai-enhanced' if has_schema_enhanced else ''}">
                        <div class="metric-header">
                            <div class="metric-icon">
                                <i class="fas fa-code"></i>
                            </div>
                            <span>Struktúra {'(Enhanced)' if has_schema_enhanced else ''}
                                <span class="tooltip">
                                    <i class="fas fa-question-circle tooltip-icon"></i>
                                    <span class="tooltip-content">Strukturált adatok és schema markup használata</span>
                                </span>
                            </span>
                        </div>
                        <div class="metric-content">
                            <div class="metric-item">
                                <span class="metric-label">H1 elemek:</span>
                                <span class="metric-value">{meta_data.get('h1_count', 0)}</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Schema típusok:</span>
                                <span class="metric-value">{sum(schema_data.get('count', {}).values())}</span>
                            </div>"""
        
        if has_schema_enhanced:
            schema_score = schema_data.get('schema_completeness_score', 0)
            google_validation = schema_data.get('google_validation', {})
            html_content += f"""
                            <div class="metric-item">
                                <span class="metric-label">Schema teljesség:</span>
                                <span class="metric-value">{fmt(schema_score, 1)}/100</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Google validáció:</span>
                                <span class="metric-value {('success' if google_validation.get('is_valid') else 'danger')}">
                                    {"✓ Valid" if google_validation.get('is_valid') else "✗ Invalid"}
                                </span>
                            </div>"""
        
        html_content += """
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
            
            <!-- AI Metrics Tab -->
            <div id="{uid}-ai-metrics" class="tab-content">
                <h3 style="margin-bottom: 1.5rem; color: var(--dark);">
                    <i class="fas fa-robot"></i> AI Readiness Metrikák
                </h3>"""
        
        # AI metrikák megjelenítése
        ai_summary = ai_metrics_summary if ai_metrics_summary else site.get("ai_metrics_summary", {})
        if ai_summary and not ai_summary.get('error'):
            scores = ai_summary.get('individual_scores', {})
            
            html_content += f"""
                <div class="metrics-grid">"""
            
            score_descriptions = {
                'structure': ('Tartalom struktúra', 'Listák, táblázatok, bekezdések és fejlécek szervezettsége', 'fas fa-sitemap'),
                'qa_format': ('Q&A formátum', 'Kérdés-válasz struktúrák és FAQ elemek jelenléte', 'fas fa-question-circle'),
                'entities': ('Entitások', 'Személyek, helyek, események strukturált jelölése', 'fas fa-tags'),
                'freshness': ('Frissesség', 'Dátumok, időbélyegek és aktualitás jelzések', 'fas fa-clock'),
                'citations': ('Hivatkozások', 'Külső források, lábjegyzetek és referenciák', 'fas fa-quote-right'),
                'formatting': ('Formázás', 'AI-barát formázási elemek használata', 'fas fa-paint-brush'),
                'depth': ('Mélység', 'Tartalom részletessége és szakmai mélysége', 'fas fa-layer-group'),
                'conversational': ('Konverzációs', 'Közvetlen megszólítások és párbeszéd elemek', 'fas fa-comments')
            }
            
            for key, value in scores.items():
                if key in score_descriptions:
                    name, desc, icon = score_descriptions[key]
                    score_class = 'success' if value >= 75 else 'warning' if value >= 50 else 'danger'
                    
                    html_content += f"""
                    <div class="metric-card">
                        <div class="metric-header">
                            <div class="metric-icon">
                                <i class="{icon}"></i>
                            </div>
                            <span>{name}
                                <span class="tooltip">
                                    <i class="fas fa-question-circle tooltip-icon"></i>
                                    <span class="tooltip-content">{desc}</span>
                                </span>
                            </span>
                        </div>
                        <div class="metric-content">
                            <div style="font-size: 2rem; font-weight: 700; text-align: center; padding: 1rem 0;">
                                <span class="text-{score_class}">{value}</span>
                                <span style="font-size: 1rem; color: var(--gray);">/100</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {value}%"></div>
                            </div>
                        </div>
                    </div>"""
            
            html_content += """
                </div>"""
        else:
            html_content += '<p style="text-align: center; color: var(--gray); padding: 2rem;">AI metrikák nem elérhetők</p>'
        
        html_content += """
            </div>
            
            <!-- Content Tab -->
            <div id="{uid}-content" class="tab-content">
                <h3 style="margin-bottom: 1.5rem; color: var(--dark);">
                    <i class="fas fa-file-alt"></i> Tartalom Minőség
                </h3>"""
        
        # Enhanced AI tartalom értékelés megjelenítése
        if ai_content_evaluation:
            ai_quality_scores = ai_content_evaluation.get('ai_quality_scores', {})
            overall_ai_score = ai_content_evaluation.get('overall_ai_score', 0)
            ai_recommendations = ai_content_evaluation.get('ai_recommendations', [])
            
            html_content += f"""
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-header">
                            <div class="metric-icon">
                                <i class="fas fa-robot"></i>
                            </div>
                            <span>AI Tartalom Értékelés
                                <span class="tooltip">
                                    <i class="fas fa-question-circle tooltip-icon"></i>
                                    <span class="tooltip-content">AI platformok által adott tartalmi pontszámok</span>
                                </span>
                            </span>
                        </div>
                        <div class="metric-content">
                            <div style="text-align: center; margin-bottom: 1rem;">
                                <div style="font-size: 2rem; font-weight: 700; color: var(--primary);">
                                    {fmt(overall_ai_score, 1)}<span style="font-size: 1rem; color: var(--gray);">/100</span>
                                </div>
                                <div style="color: var(--gray);">Összes AI Score</div>
                            </div>"""
            
            for platform, score in ai_quality_scores.items():
                html_content += f"""
                            <div class="metric-item">
                                <span class="metric-label">{platform.upper()}:</span>
                                <span class="metric-value">{fmt(score, 1)}/100</span>
                            </div>"""
            
            html_content += """
                        </div>
                    </div>"""
            
            if ai_recommendations:
                html_content += f"""
                    <div class="metric-card">
                        <div class="metric-header">
                            <div class="metric-icon">
                                <i class="fas fa-lightbulb"></i>
                            </div>
                            <span>AI Javaslatok</span>
                        </div>
                        <div class="metric-content">"""
                
                for recommendation in ai_recommendations[:5]:
                    html_content += f"""
                            <div class="metric-item">
                                <i class="fas fa-check-circle" style="color: var(--success); margin-right: 0.5rem;"></i>
                                {html.escape(str(recommendation))}
                            </div>"""
                
                html_content += """
                        </div>
                    </div>"""
            
            html_content += """
                </div>"""
        
        # AI Readability és Factual Check megjelenítése
        if ai_readability or ai_factual_check:
            html_content += """
                <div class="metrics-grid" style="margin-top: 1.5rem;">"""
            
            if ai_readability:
                clarity_score = ai_readability.get('clarity_score', 0)
                engagement_score = ai_readability.get('engagement_score', 0)
                structure_score = ai_readability.get('structure_score', 0)
                ai_friendliness = ai_readability.get('ai_friendliness', 0)
                overall_score = ai_readability.get('overall_score', 0)
                improvements = ai_readability.get('improvements', [])
                
                html_content += f"""
                    <div class="metric-card">
                        <div class="metric-header">
                            <div class="metric-icon">
                                <i class="fas fa-eye"></i>
                            </div>
                            <span>AI Olvashatóság</span>
                        </div>
                        <div class="metric-content">
                            <div style="text-align: center; margin-bottom: 1rem;">
                                <div style="font-size: 1.5rem; font-weight: 700; color: var(--primary);">
                                    {fmt(overall_score, 1)}<span style="font-size: 0.8rem; color: var(--gray);">/100</span>
                                </div>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Tisztaság:</span>
                                <span class="metric-value">{fmt(clarity_score, 0)}/100</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Vonzó tartalom:</span>
                                <span class="metric-value">{fmt(engagement_score, 0)}/100</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Struktúra:</span>
                                <span class="metric-value">{fmt(structure_score, 0)}/100</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">AI barátság:</span>
                                <span class="metric-value">{fmt(ai_friendliness, 0)}/100</span>
                            </div>"""
                
                if improvements:
                    html_content += """
                            <div style="margin-top: 1rem; font-size: 0.9rem; color: var(--gray);">
                                <strong>Javítási javaslatok:</strong>"""
                    for improvement in improvements[:3]:
                        html_content += f"""
                                <div>• {html.escape(str(improvement))}</div>"""
                    html_content += """
                            </div>"""
                
                html_content += """
                        </div>
                    </div>"""
            
            if ai_factual_check:
                factual_score = ai_factual_check.get('factual_score', 0)
                accuracy_indicators = ai_factual_check.get('accuracy_indicators', {})
                
                html_content += f"""
                    <div class="metric-card">
                        <div class="metric-header">
                            <div class="metric-icon">
                                <i class="fas fa-shield-alt"></i>
                            </div>
                            <span>Faktualitás Ellenőrzés</span>
                        </div>
                        <div class="metric-content">
                            <div style="text-align: center; margin-bottom: 1rem;">
                                <div style="font-size: 1.5rem; font-weight: 700; color: var(--success);">
                                    {fmt(factual_score, 1)}<span style="font-size: 0.8rem; color: var(--gray);">/100</span>
                                </div>
                                <div style="color: var(--gray);">Faktualitási Score</div>
                            </div>"""
                
                for indicator, value in accuracy_indicators.items():
                    if isinstance(value, (int, float)):
                        html_content += f"""
                            <div class="metric-item">
                                <span class="metric-label">{indicator.replace('_', ' ').title()}:</span>
                                <span class="metric-value">{fmt(value, 1)}</span>
                            </div>"""
                
                html_content += """
                        </div>
                    </div>"""
            
            html_content += """
                </div>"""
        
        # Tartalom minőség (standard)
        if content_quality:
            readability = content_quality.get('readability', {})
            keyword_analysis = content_quality.get('keyword_analysis', {})
            
            html_content += f"""
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-header">
                            <div class="metric-icon">
                                <i class="fas fa-book-open"></i>
                            </div>
                            <span>Olvashatóság
                                <span class="tooltip">
                                    <i class="fas fa-question-circle tooltip-icon"></i>
                                    <span class="tooltip-content">A szöveg olvashatósága és érthetősége</span>
                                </span>
                            </span>
                        </div>
                        <div class="metric-content">
                            <div class="metric-item">
                                <span class="metric-label">Szavak száma:</span>
                                <span class="metric-value">{readability.get('word_count', 0)}</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Mondatok:</span>
                                <span class="metric-value">{readability.get('sentence_count', 0)}</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Flesch pontszám:</span>
                                <span class="metric-value">{readability.get('flesch_score', 0)}</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Nehézségi szint:</span>
                                <span class="metric-value">{readability.get('readability_level', 'N/A')}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-header">
                            <div class="metric-icon">
                                <i class="fas fa-key"></i>
                            </div>
                            <span>Kulcsszavak
                                <span class="tooltip">
                                    <i class="fas fa-question-circle tooltip-icon"></i>
                                    <span class="tooltip-content">Leggyakrabban használt kifejezések</span>
                                </span>
                            </span>
                        </div>
                        <div class="metric-content">
                            <div class="metric-item">
                                <span class="metric-label">Összes szó:</span>
                                <span class="metric-value">{keyword_analysis.get('total_words', 0)}</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Egyedi szavak:</span>
                                <span class="metric-value">{keyword_analysis.get('unique_words', 0)}</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Szókincs gazdagság:</span>
                                <span class="metric-value">{fmt(keyword_analysis.get('vocabulary_richness', 0) * 100, 1)}%</span>
                            </div>
                        </div>
                    </div>
                </div>"""
        
        html_content += """
            </div>
            
            <!-- Platforms Tab -->
            <div id="{uid}-platforms" class="tab-content">
                <h3 style="margin-bottom: 1.5rem; color: var(--dark);">
                    <i class="fas fa-layer-group"></i> Platform Kompatibilitás
                </h3>"""
        
        # Platform elemzés
        if platform_analysis:
            html_content += '<div class="platform-grid">'
            
            platform_icons = {
                'chatgpt': 'fas fa-comments',
                'claude': 'fas fa-brain',
                'gemini': 'fas fa-gem',
                'bing_chat': 'fab fa-microsoft'
            }
            
            for platform_name, platform_data in platform_analysis.items():
                if platform_name == 'summary' or not isinstance(platform_data, dict):
                    continue
                
                platform_score = platform_data.get('compatibility_score', 0)
                optimization_level = platform_data.get('optimization_level', 'N/A')
                ai_score = platform_data.get('ai_score', 0)
                
                icon = platform_icons.get(platform_name, 'fas fa-robot')
                
                html_content += f"""
                    <div class="platform-card">
                        <div class="platform-logo">
                            <i class="{icon}"></i>
                        </div>
                        <div class="platform-name">{platform_name.upper()}</div>
                        <div class="platform-score">{fmt(platform_score, 0)}</div>
                        <div class="platform-level">{optimization_level}</div>
                        <div style="margin-top: 1rem;">
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {platform_score}%"></div>
                            </div>
                        </div>
                        <div style="margin-top: 0.5rem; font-size: 0.8rem; color: var(--gray);">
                            AI Score: {fmt(ai_score, 0)}/100
                        </div>
                    </div>"""
            
            html_content += '</div>'
        
        # Ha nincs platform_analysis, de van ai_content_evaluation, akkor azt jelenítjük meg
        elif ai_content_evaluation and ai_content_evaluation.get('ai_quality_scores'):
            html_content += '<div class="platform-grid">'
            
            ai_quality_scores = ai_content_evaluation.get('ai_quality_scores', {})
            platform_icons = {
                'chatgpt': 'fas fa-comments',
                'claude': 'fas fa-brain', 
                'gemini': 'fas fa-gem',
                'bing_chat': 'fab fa-microsoft'
            }
            
            for platform_name, score in ai_quality_scores.items():
                icon = platform_icons.get(platform_name, 'fas fa-robot')
                score_class = 'success' if score >= 75 else 'warning' if score >= 50 else 'danger'
                
                html_content += f"""
                    <div class="platform-card">
                        <div class="platform-logo">
                            <i class="{icon}"></i>
                        </div>
                        <div class="platform-name">{platform_name.upper()}</div>
                        <div class="platform-score">{fmt(score, 1)}</div>
                        <div class="platform-level">{level_from_score(score)}</div>
                        <div style="margin-top: 1rem;">
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {score}%"></div>
                            </div>
                        </div>
                        <div style="margin-top: 0.5rem; font-size: 0.8rem; color: var(--gray);">
                            AI Enhanced
                        </div>
                    </div>"""
            
            html_content += '</div>'
        else:
            html_content += '<p style="text-align: center; color: var(--gray); padding: 2rem;">Platform kompatibilitási adatok nem elérhetők</p>'
        
        html_content += """
            </div>
            
            <!-- Fixes Tab -->
            <div id="{uid}-fixes" class="tab-content">
                <h3 style="margin-bottom: 1.5rem; color: var(--dark);">
                    <i class="fas fa-wrench"></i> Javítási Javaslatok
                </h3>"""
        
        # Javítások
        if auto_fixes:
            critical_fixes = auto_fixes.get('critical_fixes', [])
            seo_improvements = auto_fixes.get('seo_improvements', [])
            schema_suggestions = auto_fixes.get('schema_suggestions', [])
            content_optimizations = auto_fixes.get('content_optimizations', [])
            
            # Kritikus javítások
            if critical_fixes:
                html_content += '<div style="margin-bottom: 2rem;"><h4 style="color: var(--danger); margin-bottom: 1rem;"><i class="fas fa-exclamation-triangle"></i> Kritikus javítások</h4>'
                
                for fix in critical_fixes[:3]:  # Max 3 kritikus
                    if isinstance(fix, dict):
                        html_content += f"""
                        <div class="fix-card critical">
                            <div class="fix-header">
                                <div class="fix-icon">
                                    <i class="fas fa-exclamation"></i>
                                </div>
                                <div class="fix-title">{html.escape(fix.get('issue', 'N/A'))}</div>
                            </div>
                            <div class="fix-content">
                                <p><strong>Hatás:</strong> {html.escape(fix.get('impact', ''))}</p>
                                <p><strong>Magyarázat:</strong> {html.escape(fix.get('explanation', ''))}</p>
                                <p><strong>Becsült idő:</strong> {html.escape(fix.get('estimated_time', ''))}</p>
                                <p><strong>Súlyosság:</strong> {html.escape(fix.get('severity', ''))}</p>
                            </div>"""
                        
                        if fix.get('fix_code'):
                            html_content += f'<div class="fix-code">{html.escape(fix.get("fix_code", ""))}</div>'
                        
                        html_content += '</div>'
                
                html_content += '</div>'
            
            # Schema javaslatok
            if schema_suggestions:
                html_content += '<div style="margin-bottom: 2rem;"><h4 style="color: var(--warning); margin-bottom: 1rem;"><i class="fas fa-code"></i> Schema.org javaslatok</h4>'
                
                for suggestion in schema_suggestions[:3]:
                    if isinstance(suggestion, dict):
                        priority_color = 'var(--danger)' if suggestion.get('priority') == 'high' else 'var(--warning)' if suggestion.get('priority') == 'medium' else 'var(--info)'
                        
                        html_content += f"""
                        <div class="fix-card schema">
                            <div class="fix-header">
                                <div class="fix-icon" style="background: {priority_color};">
                                    <i class="fas fa-sitemap"></i>
                                </div>
                                <div class="fix-title">{html.escape(suggestion.get('type', 'N/A'))}</div>
                            </div>
                            <div class="fix-content">
                                <p><strong>Előny:</strong> {html.escape(suggestion.get('benefit', ''))}</p>
                                <p><strong>Prioritás:</strong> {html.escape(suggestion.get('priority', ''))}</p>
                                <p><strong>Implementáció:</strong> {html.escape(suggestion.get('implementation', ''))}</p>"""
                        
                        if suggestion.get('note'):
                            html_content += f'<p><strong>Megjegyzés:</strong> {html.escape(suggestion.get("note", ""))}</p>'
                        
                        if suggestion.get('code'):
                            html_content += f'<div class="fix-code" style="max-height: 200px; overflow-y: auto;">{html.escape(suggestion.get("code", ""))}</div>'
                        
                        html_content += '</div></div>'
                
                html_content += '</div>'
            
            # Tartalom optimalizációk
            if content_optimizations:
                html_content += '<div style="margin-bottom: 2rem;"><h4 style="color: var(--info); margin-bottom: 1rem;"><i class="fas fa-edit"></i> Tartalom optimalizációk</h4>'
                
                for optimization in content_optimizations[:3]:
                    if isinstance(optimization, dict):
                        html_content += f"""
                        <div class="fix-card content">
                            <div class="fix-header">
                                <div class="fix-icon" style="background: var(--info);">
                                    <i class="fas fa-file-alt"></i>
                                </div>
                                <div class="fix-title">{html.escape(optimization.get('issue', 'N/A'))}</div>
                            </div>
                            <div class="fix-content">"""
                        
                        if optimization.get('priority'):
                            html_content += f'<p><strong>Prioritás:</strong> {html.escape(optimization.get("priority", ""))}</p>'
                        if optimization.get('action'):
                            html_content += f'<p><strong>Teendő:</strong> {html.escape(optimization.get("action", ""))}</p>'
                        if optimization.get('benefit'):
                            html_content += f'<p><strong>Előny:</strong> {html.escape(optimization.get("benefit", ""))}</p>'
                        
                        html_content += '</div></div>'
                
                html_content += '</div>'
            
            # SEO fejlesztések
            if seo_improvements:
                html_content += '<div style="margin-bottom: 2rem;"><h4 style="color: var(--success); margin-bottom: 1rem;"><i class="fas fa-search"></i> SEO fejlesztések</h4>'
                
                for improvement in seo_improvements[:3]:
                    if isinstance(improvement, dict):
                        html_content += f"""
                        <div class="fix-card seo">
                            <div class="fix-header">
                                <div class="fix-icon" style="background: var(--success);">
                                    <i class="fas fa-chart-line"></i>
                                </div>
                                <div class="fix-title">{html.escape(improvement.get('issue', improvement.get('title', 'N/A')))}</div>
                            </div>
                            <div class="fix-content">"""
                        
                        for key, value in improvement.items():
                            if key not in ['issue', 'title'] and value:
                                html_content += f'<p><strong>{key.replace("_", " ").title()}:</strong> {html.escape(str(value))}</p>'
                        
                        html_content += '</div></div>'
                
                html_content += '</div>'
        else:
            html_content += '<p style="text-align: center; color: var(--gray); padding: 2rem;">Javítási javaslatok nem elérhetők</p>'
        
        html_content += """
            </div>
        </div>"""

    # Footer
    html_content += f"""
        <div class="footer">
            <div class="footer-logo">
                <i class="fas fa-chart-line"></i>
            </div>
            <div class="footer-text">
                GEO AI Readiness Analyzer
            </div>
            <div class="footer-meta">
                © {datetime.now().year} • {'Enhanced Analysis' if is_enhanced else 'Standard Analysis'} • Minden jog fenntartva
            </div>
        </div>
    </div>
    
    <script>
        // Tab kezelés
        function showTab(event, siteId, tabName) {{
            const allTabs = document.querySelectorAll('[id^="' + siteId + '-"]');
            allTabs.forEach(tab => tab.classList.remove('active'));
            
            const targetTab = document.getElementById(siteId + '-' + tabName);
            if (targetTab) {{
                targetTab.classList.add('active');
            }}
            
            const tabButtons = event.target.parentElement.querySelectorAll('.tab');
            tabButtons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            event.preventDefault();
            return false;
        }}
        
        // Charts"""

    # Chart generálás
    for idx, site in enumerate(data):
        if not isinstance(site, dict):
            continue
            
        url = site.get("url", "N/A")
        uid = f"site_{idx}_{re.sub(r'[^a-zA-Z0-9]', '_', url)}"
        
        meta_data = site.get("meta_and_headings", {})
        headings = meta_data.get("headings", {})
        
        schema_data = site.get("schema", {})
        schema_count = schema_data.get("count", {})
        
        # Heading chart
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
                    label: 'Heading elemek',
                    data: {heading_values},
                    backgroundColor: 'rgba(99, 102, 241, 0.8)',
                    borderColor: 'rgba(99, 102, 241, 1)',
                    borderWidth: 1,
                    borderRadius: 8
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Heading Struktúra',
                        font: {{
                            size: 14,
                            weight: 'bold'
                        }}
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
        }});"""
        
        # Schema chart
        if schema_count and any(v > 0 for v in schema_count.values()):
            filtered_schema = {k: v for k, v in schema_count.items() if v > 0}
            
            html_content += f"""
        
        // Schema Chart - {uid}
        new Chart(document.getElementById('schemaChart_{uid}'), {{
            type: 'doughnut',
            data: {{
                labels: {list(filtered_schema.keys())},
                datasets: [{{
                    label: 'Schema típusok',
                    data: {list(filtered_schema.values())},
                    backgroundColor: [
                        'rgba(99, 102, 241, 0.8)',
                        'rgba(236, 72, 153, 0.8)',
                        'rgba(251, 146, 60, 0.8)',
                        'rgba(34, 197, 94, 0.8)',
                        'rgba(168, 85, 247, 0.8)',
                        'rgba(250, 204, 21, 0.8)'
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
                        text: 'Schema Típusok',
                        font: {{
                            size: 14,
                            weight: 'bold'
                        }}
                    }},
                    legend: {{
                        position: 'bottom',
                        labels: {{
                            padding: 15,
                            font: {{
                                size: 11
                            }}
                        }}
                    }}
                }}
            }}
        }});"""

    html_content += """
    </script>
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

def generate_csv_export(json_file: str = "ai_readiness_full_report.json",
                        output_file: str = "ai_readiness_report.csv") -> None:
    """Enhanced CSV export generálása"""
    import csv
    
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Hiba: {e}")
        return
    
    # Enhanced felismerés
    detection_result = detect_enhanced_analysis(data)
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
        
        for site in data:
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
            
            # Enhanced mezők hozzáadása
            if is_enhanced:
                ai_content_eval = site.get('ai_content_evaluation', {})
                row.update({
                    'AI Enhanced': bool(ai_content_eval),
                    'AI Overall Score': fmt(ai_content_eval.get('overall_ai_score', 0), 1) if ai_content_eval else '—',
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