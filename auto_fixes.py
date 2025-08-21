import re
import json
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from string import Template


class AutoFixGenerator:
    """Automatikus javítási javaslatok generálása"""
    
    def __init__(self):
        self.meta_templates = {
            "title": {
                "template": "<title>{title}</title>",
                "optimal_length": (30, 60),
                "examples": [
                    "Professzionális SEO szolgáltatások - Weboldaloptimalizálás",
                    "Python fejlesztés - Egyedi szoftverek és alkalmazások"
                ]
            },
            "description": {
                "template": '<meta name="description" content="{description}">',
                "optimal_length": (120, 160),
                "examples": [
                    "Professzionális SEO és weboldaloptimalizálás szolgáltatások. Növeld weboldalad látogatottságát és keresőmotoros rangsorolásodat szakértő csapatunkkal.",
                    "Python alapú egyedi szoftverek és webalkalmazások fejlesztése. API integráció, automatizálás és adatelemzés professzionális megoldásokkal."
                ]
            }
        }
        
        self.schema_templates = {
            "organization": Template("""{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "$company_name",
  "url": "$website_url",
  "logo": "$logo_url",
  "description": "$company_description",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "$street_address",
    "addressLocality": "$city",
    "addressCountry": "$country"
  },
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "$phone",
    "contactType": "customer service"
  }
}"""),
            
            "faq": Template("""{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "$question",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "$answer"
      }
    }
  ]
}"""),
            
            "article": Template("""{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "$headline",
  "author": {
    "@type": "Person",
    "name": "$author_name"
  },
  "datePublished": "$publish_date",
  "dateModified": "$modified_date",
  "description": "$article_description",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "$article_url"
  }
}"""),
            
            "howto": Template("""{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "$howto_title",
  "description": "$howto_description",
  "step": [
    {
      "@type": "HowToStep",
      "name": "$step_name",
      "text": "$step_description"
    }
  ]
}""")
        }
    
    def generate_all_fixes(self, analysis_result: Dict, url: str) -> Dict:
        """Összes automatikus javítás generálása - JAVÍTVA"""
        
        # JAVÍTÁS: Ellenőrizzük, hogy van-e érvényes analysis_result
        if not analysis_result or not isinstance(analysis_result, dict):
            return {
                "error": "Nincs elemzési adat",
                "critical_fixes": [],
                "seo_improvements": [],
                "schema_suggestions": [],
                "content_optimizations": [],
                "technical_fixes": [],
                "ai_readiness_fixes": [],
                "implementation_guide": {},
                "prioritized_actions": []
            }
        
        try:
            fixes = {
                "critical_fixes": self._generate_critical_fixes(analysis_result, url),
                "seo_improvements": self._generate_seo_improvements(analysis_result, url),
                "schema_suggestions": self._generate_schema_fixes(analysis_result, url),
                "content_optimizations": self._generate_content_fixes(analysis_result),
                "technical_fixes": self._generate_technical_fixes(analysis_result),
                "ai_readiness_fixes": self._generate_ai_fixes(analysis_result),
                "implementation_guide": self._create_implementation_guide()
            }
            
            # Prioritás szerinti rendezés
            fixes["prioritized_actions"] = self._prioritize_fixes(fixes)
            
            return fixes
            
        except Exception as e:
            # Ha bármilyen hiba van, visszaadjuk az alap struktúrát
            return {
                "error": str(e),
                "critical_fixes": [],
                "seo_improvements": [],
                "schema_suggestions": [],
                "content_optimizations": [],
                "technical_fixes": [],
                "ai_readiness_fixes": [],
                "implementation_guide": self._create_implementation_guide(),
                "prioritized_actions": []
            }
    
    def _generate_critical_fixes(self, analysis: Dict, url: str) -> List[Dict]:
        """Kritikus hibák javítása - JAVÍTVA"""
        critical_fixes = []
        
        meta_data = analysis.get("meta_and_headings", {})
        
        # JAVÍTÁS: Biztonságos title kezelés
        title = meta_data.get("title")
        if not title:  # Ha None vagy üres string
            domain = urlparse(url).netloc
            suggested_title = self._suggest_title_from_domain(domain)
            
            critical_fixes.append({
                "issue": "Hiányzó title tag",
                "severity": "critical",
                "impact": "SEO és AI rangsorolás drasztikus romlása",
                "fix_code": f'<title>{suggested_title}</title>',
                "explanation": "A title tag a legfontosabb SEO elem",
                "estimated_time": "2 perc",
                "implementation": "head szekció első eleme legyen"
            })
        
        # JAVÍTÁS: Biztonságos description kezelés
        description = meta_data.get("description")
        if not description:  # Ha None vagy üres string
            suggested_description = self._suggest_description_from_domain(urlparse(url).netloc)
            
            critical_fixes.append({
                "issue": "Hiányzó meta description",
                "severity": "critical",
                "impact": "Alacsony CTR a keresőkben",
                "fix_code": f'<meta name="description" content="{suggested_description}">',
                "explanation": "Meta description befolyásolja a kattintási arányt",
                "estimated_time": "3 perc",
                "implementation": "head szekcióban a title után"
            })
        
        # Hiányzó H1
        if meta_data.get("h1_count", 0) == 0:
            # JAVÍTÁS: Biztonságos title használat H1 javaslatra
            suggested_h1 = title if title else self._suggest_title_from_domain(urlparse(url).netloc)
            
            critical_fixes.append({
                "issue": "Hiányzó H1 elem",
                "severity": "critical",
                "impact": "Gyenge tartalom struktúra AI-k számára",
                "fix_code": f'<h1>{suggested_h1}</h1>',
                "explanation": "H1 az oldal fő témáját jelöli",
                "estimated_time": "1 perc",
                "implementation": "Főtartalom elején helyezd el"
            })
        
        # Több H1 elem
        if meta_data.get("h1_count", 0) > 1:
            critical_fixes.append({
                "issue": "Túl sok H1 elem",
                "severity": "high",
                "impact": "Zavaró struktúra AI rendszerek számára",
                "fix_code": "<!-- Csak egy H1-et tarts meg, a többit H2-re cseréld -->\n<h2>Alcím</h2>",
                "explanation": "Csak egy H1 legyen oldalanként",
                "estimated_time": "5 perc",
                "implementation": "Többi H1-et H2, H3 stb. elemre cseréld"
            })
        
        return critical_fixes
    
    def _generate_seo_improvements(self, analysis: Dict, url: str) -> List[Dict]:
        """SEO fejlesztések - JAVÍTVA"""
        seo_fixes = []
        
        meta_data = analysis.get("meta_and_headings", {})
        
        # JAVÍTÁS: Biztonságos title kezelés
        title = meta_data.get("title")
        if title:  # Csak ha van title
            title_length = len(title)
            
            if not meta_data.get("title_optimal"):
                if title_length < 30:
                    seo_fixes.append({
                        "issue": "Túl rövid title",
                        "current_length": title_length,
                        "optimal_range": "30-60 karakter",
                        "suggestion": f"Bővítsd ki: '{title}' → '{title} - {self._suggest_title_extension(url)}'",
                        "fix_code": f'<title>{title} - {self._suggest_title_extension(url)}</title>',
                        "impact": "Jobb SEO teljesítmény és AI megjelenés"
                    })
                elif title_length > 60:
                    shortened = title[:57] + "..."
                    seo_fixes.append({
                        "issue": "Túl hosszú title",
                        "current_length": title_length,
                        "optimal_range": "30-60 karakter",
                        "suggestion": f"Rövidítsd le: '{title}' → '{shortened}'",
                        "fix_code": f'<title>{shortened}</title>',
                        "impact": "Teljes megjelenés a keresőkben"
                    })
        
        # JAVÍTÁS: Biztonságos description kezelés
        description = meta_data.get("description")
        if description:  # Csak ha van description
            desc_length = len(description)
            
            if not meta_data.get("description_optimal"):
                if desc_length < 120:
                    extended_desc = description + " " + self._suggest_description_extension(url)
                    seo_fixes.append({
                        "issue": "Túl rövid meta description",
                        "current_length": desc_length,
                        "optimal_range": "120-160 karakter",
                        "suggestion": f"Bővítsd ki részletekkel",
                        "fix_code": f'<meta name="description" content="{extended_desc}">',
                        "impact": "Több információ a keresőkben"
                    })
                elif desc_length > 160:
                    shortened_desc = description[:157] + "..."
                    seo_fixes.append({
                        "issue": "Túl hosszú meta description",
                        "current_length": desc_length,
                        "optimal_range": "120-160 karakter",
                        "suggestion": "Rövidítsd le a legfontosabb információkra",
                        "fix_code": f'<meta name="description" content="{shortened_desc}">',
                        "impact": "Teljes megjelenés, nincs levágás"
                    })
        
        # Open Graph
        if not meta_data.get("has_og_tags"):
            domain = urlparse(url).netloc
            # JAVÍTÁS: Biztonságos default értékek
            og_title = title if title else domain
            og_description = description if description else f"{domain} weboldal"
            
            seo_fixes.append({
                "issue": "Hiányzó Open Graph meta tagek",
                "impact": "Gyenge social media megjelenés",
                "fix_code": f'''<meta property="og:title" content="{og_title}">
    <meta property="og:description" content="{og_description}">
    <meta property="og:url" content="{url}">
    <meta property="og:type" content="website">''',
                "implementation": "head szekcióba illeszd be"
            })
        
        return seo_fixes
    
    def _generate_schema_fixes(self, analysis: Dict, url: str) -> List[Dict]:
        """Schema.org javítások - JAVÍTVA"""
        schema_fixes = []
        
        schema_data = analysis.get("schema", {})
        
        # JAVÍTÁS: Biztonságos schema count kezelés
        schema_count = 0
        if schema_data and "count" in schema_data:
            count_dict = schema_data.get("count", {})
            if isinstance(count_dict, dict):
                schema_count = sum(count_dict.values())
        
        if schema_count == 0:
            # Alapvető Organization schema
            domain = urlparse(url).netloc
            
            schema_fixes.append({
                "type": "Organization Schema",
                "priority": "high",
                "benefit": "Céginformációk struktúrált megjelenítése",
                "code": self.schema_templates["organization"].substitute(
                    company_name=domain.replace('www.', '').replace('.com', '').replace('.hu', '').title(),
                    website_url=url,
                    logo_url=f"{url}/logo.png",
                    company_description="Cég leírása ide kerül",
                    street_address="Cím",
                    city="Város",
                    country="Magyarország",
                    phone="+36-XX-XXX-XXXX"
                ),
                "implementation": "JSON-LD script tag-ként a head szekcióban"
            })
        
        # FAQ schema javaslat ha sok kérdés van a tartalomban
        ai_metrics = analysis.get("ai_metrics", {})
        if ai_metrics and isinstance(ai_metrics, dict):
            qa_format = ai_metrics.get("qa_format", {})
            if isinstance(qa_format, dict) and qa_format.get("question_patterns_count", 0) > 3:
                schema_fixes.append({
                    "type": "FAQ Schema",
                    "priority": "medium",
                    "benefit": "Kérdés-válasz megjelenés a keresőkben",
                    "code": self.schema_templates["faq"].substitute(
                        question="Gyakori kérdés?",
                        answer="Részletes válasz a kérdésre."
                    ),
                    "implementation": "Minden FAQ blokkhoz külön schema",
                    "note": "Automatikusan generálható a meglévő Q&A tartalmakból"
                })
        
        # Article schema blog posztokhoz
        if "blog" in url.lower() or "post" in url.lower() or "cikk" in url.lower():
            # JAVÍTÁS: Biztonságos title kezelés
            meta_data = analysis.get("meta_and_headings", {})
            article_title = meta_data.get("title") if meta_data.get("title") else "Cikk címe"
            
            schema_fixes.append({
                "type": "Article Schema",
                "priority": "medium",
                "benefit": "Cikk részletek megjelenése AI rendszerekben",
                "code": self.schema_templates["article"].substitute(
                    headline=article_title,
                    author_name="Szerző neve",
                    publish_date="2024-01-01",
                    modified_date="2024-01-01",
                    article_description="Cikk rövid leírása",
                    article_url=url
                ),
                "implementation": "Minden cikkoldalon"
            })
        
        return schema_fixes
    
    def _generate_content_fixes(self, analysis: Dict) -> List[Dict]:
        """Tartalom optimalizálás - JAVÍTVA"""
        content_fixes = []
        
        # AI specifikus metrikák alapján
        ai_metrics = analysis.get("ai_metrics", {})
        
        # JAVÍTÁS: Biztonságos dictionary elérés
        if ai_metrics and isinstance(ai_metrics, dict):
            # Step-by-step tartalom hiánya
            content_structure = ai_metrics.get("content_structure", {})
            if isinstance(content_structure, dict):
                lists = content_structure.get("lists", {})
                if isinstance(lists, dict) and lists.get("ordered", 0) < 2:
                    content_fixes.append({
                        "issue": "Hiányzó step-by-step tartalom",
                        "benefit": "AI rendszerek könnyebben feldolgozzák",
                        "suggestion": "Adj hozzá számozott lépéseket",
                        "example_code": '''
    <ol>
    <li>Első lépés: Részletes leírás</li>
    <li>Második lépés: További információk</li>
    <li>Harmadik lépés: Befejezés</li>
    </ol>''',
                        "ai_platforms": ["ChatGPT", "Claude", "Gemini"]
                    })
            
            # FAQ szekció hiánya
            qa_format = ai_metrics.get("qa_format", {})
            if isinstance(qa_format, dict):
                qa_score = qa_format.get("qa_score", 0)
                if qa_score < 30:
                    content_fixes.append({
                        "issue": "Gyenge Q&A struktúra",
                        "benefit": "Jobb megjelenés AI válaszokban",
                        "suggestion": "Adj hozzá FAQ szekciót",
                        "example_code": '''
    <section id="faq">
    <h2>Gyakori kérdések</h2>
    <div class="faq-item">
        <h3>Kérdés: Hogyan működik?</h3>
        <p>Válasz: Részletes magyarázat...</p>
    </div>
    </section>''',
                        "ai_platforms": ["ChatGPT", "Gemini", "Bing Chat"]
                    })
        
        # Tartalom mélység
        content_quality = analysis.get("content_quality", {})
        if content_quality and isinstance(content_quality, dict):
            content_depth = content_quality.get("content_depth", {})
            if isinstance(content_depth, dict) and content_depth.get("depth_score", 0) < 50:
                content_fixes.append({
                    "issue": "Felületes tartalom",
                    "benefit": "Nagyobb tekintély AI rendszerekben",
                    "suggestion": "Bővítsd több példával és részlettel",
                    "improvements": [
                        "Adj hozzá konkrét példákat",
                        "Statisztikák és adatok használata",
                        "Részletes magyarázatok",
                        "Szakmai terminológia"
                    ]
                })
        
        return content_fixes
    
    def _generate_technical_fixes(self, analysis: Dict) -> List[Dict]:
        """Technikai javítások"""
        technical_fixes = []
        
        # Mobile-friendly hiányosságok
        mobile = analysis.get("mobile_friendly", {})
        if not mobile.get("has_viewport"):
            technical_fixes.append({
                "issue": "Hiányzó viewport meta tag",
                "severity": "high",
                "impact": "Rossz mobil megjelenés",
                "fix_code": '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
                "implementation": "head szekció tetején"
            })
        
        # Robots.txt probléma
        robots = analysis.get("robots_txt", {})
        if not robots.get("can_fetch"):
            technical_fixes.append({
                "issue": "Robots.txt blokkolja az indexelést",
                "severity": "critical",
                "impact": "AI rendszerek nem érik el az oldalt",
                "fix_code": """User-agent: *
Allow: /
Sitemap: {}/sitemap.xml""".format(analysis.get("url", "")),
                "implementation": "robots.txt fájl módosítása"
            })
        
        # Sitemap hiánya
        sitemap = analysis.get("sitemap", {})
        if not sitemap.get("exists"):
            technical_fixes.append({
                "issue": "Hiányzó sitemap",
                "impact": "Lassabb indexelés",
                "solution": "XML sitemap generálása",
                "tools": ["WordPress: Yoast SEO", "Online generators", "Google Search Console"],
                "example_url": f"{analysis.get('url', '')}/sitemap.xml"
            })
        
        return technical_fixes
    
    def _generate_ai_fixes(self, analysis: Dict) -> List[Dict]:
        """AI-specifikus optimalizálások"""
        ai_fixes = []
        
        # Platform specifikus javaslatok
        platforms = analysis.get("platform_analysis", {})
        
        for platform_name, platform_data in platforms.items():
            if platform_name == "summary":
                continue
                
            score = platform_data.get("compatibility_score", 0)
            if score < 70:
                ai_fixes.append({
                    "platform": platform_name,
                    "current_score": score,
                    "target_score": 80,
                    "quick_wins": self._get_platform_quick_wins(platform_name, platform_data),
                    "estimated_improvement": f"+{min(20, 80-score)} pont"
                })
        
        # Általános AI optimalizálás
        ai_readiness = analysis.get("ai_readiness_score", 0)
        if ai_readiness < 70:
            ai_fixes.append({
                "type": "general_ai_optimization",
                "current_score": ai_readiness,
                "improvements": [
                    "Strukturált tartalom hozzáadása",
                    "FAQ szekció létrehozása", 
                    "Schema.org markup implementálása",
                    "Heading hierarchia javítása",
                    "Citációk és források hozzáadása"
                ]
            })
        
        return ai_fixes
    
    def _create_implementation_guide(self) -> Dict:
        """Implementálási útmutató"""
        return {
            "priority_order": [
                "1. Kritikus hibák javítása (title, description, H1)",
                "2. Technikai problémák megoldása (robots.txt, sitemap)",
                "3. Schema.org markup hozzáadása",
                "4. Tartalom optimalizálás",
                "5. AI platform specifikus fejlesztések"
            ],
            "estimated_timeline": {
                "critical_fixes": "1-2 óra",
                "technical_fixes": "2-4 óra", 
                "schema_implementation": "4-6 óra",
                "content_optimization": "1-2 nap",
                "platform_optimization": "2-3 nap"
            },
            "testing_checklist": [
                "Google Search Console validálás",
                "Schema.org Testing Tool ellenőrzés",
                "Mobile-Friendly Test",
                "PageSpeed Insights újratesztelés",
                "AI platform tesztelés (ChatGPT, Claude)"
            ],
            "monitoring": [
                "Search Console hibák figyelése",
                "Ranking változások követése",
                "AI platform megjelenések monitorozása",
                "Heti/havi AI-readiness score ellenőrzés"
            ]
        }
    
    def _prioritize_fixes(self, fixes: Dict) -> List[Dict]:
        """Javítások prioritás szerinti rendezése"""
        all_fixes = []
        
        # Kritikus javítások (legmagasabb prioritás)
        for fix in fixes.get("critical_fixes", []):
            all_fixes.append({
                **fix,
                "category": "critical",
                "priority_score": 100
            })
        
        # Technikai javítások
        for fix in fixes.get("technical_fixes", []):
            priority_score = 90 if fix.get("severity") == "critical" else 70
            all_fixes.append({
                **fix,
                "category": "technical",
                "priority_score": priority_score
            })
        
        # SEO fejlesztések
        for fix in fixes.get("seo_improvements", []):
            all_fixes.append({
                **fix,
                "category": "seo",
                "priority_score": 60
            })
        
        # Schema javítások
        for fix in fixes.get("schema_suggestions", []):
            priority_score = 80 if fix.get("priority") == "high" else 50
            all_fixes.append({
                **fix,
                "category": "schema",
                "priority_score": priority_score
            })
        
        # Rendezés prioritás szerint
        return sorted(all_fixes, key=lambda x: x.get("priority_score", 0), reverse=True)
    
    # Helper metódusok
    def _suggest_title_from_domain(self, domain: str) -> str:
        """Title javaslat domain alapján"""
        clean_domain = domain.replace('www.', '').replace('.com', '').replace('.hu', '')
        return f"{clean_domain.title()} - Professzionális Szolgáltatások"
    
    def _suggest_description_from_domain(self, domain: str) -> str:
        """Description javaslat domain alapján"""
        clean_domain = domain.replace('www.', '').replace('.com', '').replace('.hu', '')
        return f"{clean_domain.title()} professzionális szolgáltatásai. Minőségi megoldások, tapasztalt csapat, elégedett ügyfelek. Kérj árajánlatot még ma!"
    
    def _suggest_title_extension(self, url: str) -> str:
        """Title kiterjesztés javaslat"""
        domain = urlparse(url).netloc
        if 'blog' in url:
            return "Blog"
        elif 'szolgaltatas' in url or 'service' in url:
            return "Szolgáltatások"
        elif 'kapcsolat' in url or 'contact' in url:
            return "Kapcsolat"
        else:
            return "Kezdőlap"
    
    def _suggest_description_extension(self, url: str) -> str:
        """Description kiterjesztés javaslat"""
        if 'blog' in url:
            return "Olvass friss cikkeket és szakmai tanácsokat."
        elif 'szolgaltatas' in url:
            return "Fedezd fel szolgáltatásainkat és kérj személyre szabott ajánlatot."
        else:
            return "Tudj meg többet rólunk és vedd fel velünk a kapcsolatot."
    
    def _get_platform_quick_wins(self, platform: str, data: Dict) -> List[str]:
        """Platform specifikus gyors nyereségek"""
        quick_wins = []
        
        if platform == "chatgpt":
            if data.get("structured_lists", {}).get("ordered", 0) == 0:
                quick_wins.append("Adj hozzá számozott listákat")
            if data.get("step_by_step_content", 0) < 3:
                quick_wins.append("Hozz létre step-by-step útmutatót")
        
        elif platform == "claude":
            if data.get("content_length", 0) < 800:
                quick_wins.append("Bővítsd a tartalmat részletekkel")
            if data.get("citations_sources", 0) < 3:
                quick_wins.append("Adj hozzá hivatkozásokat")
        
        elif platform == "gemini":
            if data.get("multimedia_content", {}).get("images", 0) < 3:
                quick_wins.append("Adj hozzá releváns képeket")
            if data.get("structured_data", 0) < 20:
                quick_wins.append("Implementálj Schema.org markup-ot")
        
        elif platform == "bing_chat":
            if data.get("external_references", 0) < 5:
                quick_wins.append("Hivatkozz külső forrásokra")
        
        return quick_wins or ["Általános optimalizálás szükséges"]
    
    def generate_fix_report(self, fixes: Dict, url: str) -> str:
        """Összefoglaló jelentés generálása"""
        report = f"""
# Automatikus Javítási Javaslatok
## Elemzett URL: {url}

### 🚨 Kritikus javítások ({len(fixes.get('critical_fixes', []))})
"""
        
        for fix in fixes.get('critical_fixes', []):
            report += f"""
**{fix['issue']}**
- Súlyosság: {fix['severity']}
- Hatás: {fix['impact']}
- Megoldás: `{fix['fix_code']}`
- Időigény: {fix['estimated_time']}
"""
        
        report += f"""
### ⚙️ Technikai javítások ({len(fixes.get('technical_fixes', []))})
"""
        
        for fix in fixes.get('technical_fixes', []):
            report += f"""
**{fix['issue']}**
- Hatás: {fix['impact']}
- Megoldás: `{fix.get('fix_code', fix.get('solution', 'Lásd részletek'))}`
"""
        
        report += f"""
### 📈 Prioritizált cselekvési terv
"""
        
        for i, action in enumerate(fixes.get('implementation_guide', {}).get('priority_order', []), 1):
            report += f"{i}. {action}\n"
        
        return report