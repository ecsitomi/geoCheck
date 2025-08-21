import requests
from urllib.parse import urlparse, quote
from bs4 import BeautifulSoup
import json
from urllib.robotparser import RobotFileParser
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Tuple, List, Optional
import time
from dotenv import load_dotenv
import os
import re

from ai_metrics import AISpecificMetrics
from content_analyzer import ContentQualityAnalyzer
from platform_optimizer import MultiPlatformGEOAnalyzer
from auto_fixes import AutoFixGenerator
from advanced_reporting import AdvancedReportGenerator
from cache_manager import CacheManager
from ai_evaluator import AIContentEvaluator
from schema_validator import SchemaValidator

# .env fájl betöltése
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

class GEOAnalyzer:
    """Generative Engine Optimization elemző osztály"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GOOGLE_API_KEY
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; GEO-Analyzer/1.0)'
        })

    def _safe_analyze_url(self, url: str, skip_pagespeed: bool = False) -> Dict:
        """Biztonságos URL elemzés wrapper - JAVÍTOTT"""
        try:
            return self.analyze_url(url, skip_pagespeed)
        except Exception as e:
            # Ha bármilyen hiba van, részletes infót adunk vissza
            import traceback
            return {
                "url": url,
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()
            }
    
    def validate_url(self, url: str) -> bool:
        """URL validálás"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def check_robots_txt(self, url: str) -> Tuple[bool, str]:
        """Robots.txt ellenőrzés fejlettebb hibakezeléssel"""
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        
        try:
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            can_fetch = rp.can_fetch("*", url)
            return can_fetch, robots_url
        except Exception as e:
            print(f"    ⚠️ Robots.txt ellenőrzési hiba: {e}")
            return True, robots_url  # Ha nincs robots.txt, engedélyezzük
    
    def check_sitemap(self, url: str) -> Tuple[bool, str, Optional[int]]:
        """Sitemap ellenőrzés több helyen"""
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Próbáljuk meg több helyen is
        sitemap_locations = [
            f"{base_url}/sitemap.xml",
            f"{base_url}/sitemap_index.xml",
            f"{base_url}/sitemap.xml.gz",
            f"{base_url}/wp-sitemap.xml"  # WordPress
        ]
        
        for sitemap_url in sitemap_locations:
            try:
                r = self.session.get(sitemap_url, timeout=10)
                if r.status_code == 200:
                    # Ellenőrizzük, hogy tényleg sitemap-e
                    if 'xml' in r.headers.get('content-type', '').lower() or '<urlset' in r.text[:500]:
                        return True, sitemap_url, len(r.text)
            except requests.RequestException:
                continue
        
        return False, sitemap_locations[0], None
    
    def get_html(self, url: str) -> Optional[str]:
        """HTML lekérése fejlettebb hibakezeléssel"""
        try:
            r = self.session.get(url, timeout=15)
            r.raise_for_status()
            return r.text
        except requests.RequestException as e:
            print(f"    ❌ HTML lekérési hiba: {e}")
            return None
    
    def check_schema(self, html: str) -> Dict[str, any]:
        """Schema.org ellenőrzés részletesebb elemzéssel"""
        soup = BeautifulSoup(html, 'html.parser')
        schemas = soup.find_all("script", type="application/ld+json")
        
        schema_info = {
            "count": {"FAQPage": 0, "HowTo": 0, "Organization": 0, "Product": 0, 
                    "Article": 0, "LocalBusiness": 0, "Other": 0},
            "details": [],
            "has_breadcrumbs": False,
            "has_search_action": False
        }
        
        for script in schemas:
            try:
                # JAVÍTÁS: Tisztítsuk meg a JSON stringet whitespace-ektől
                script_content = script.string
                if not script_content:
                    continue
                    
                # Whitespace tisztítás a JSON parse előtt
                script_content = script_content.strip()
                
                # JSON parse
                data = json.loads(script_content)
                items = data if isinstance(data, list) else [data]
                
                for item in items:
                    # JAVÍTÁS: Biztonságos dictionary hozzáférés
                    if not isinstance(item, dict):
                        continue
                        
                    schema_type = item.get("@type")  # Használjuk a .get() metódust
                    
                    # Többféle típus kezelése
                    if isinstance(schema_type, list):
                        schema_type = schema_type[0] if schema_type else "Unknown"
                    
                    # Kategorizálás
                    if schema_type and schema_type in schema_info["count"]:
                        schema_info["count"][schema_type] += 1
                    elif schema_type:  # Ha van type, de nem ismert
                        schema_info["count"]["Other"] += 1
                    
                    # Speciális sémák detektálása
                    if schema_type == "BreadcrumbList":
                        schema_info["has_breadcrumbs"] = True
                    elif schema_type == "WebSite" and "potentialAction" in item:
                        schema_info["has_search_action"] = True
                    
                    # Schema részletek tárolása
                    if schema_type:  # Csak ha van érvényes type
                        schema_info["details"].append({
                            "type": schema_type,
                            "has_image": "@image" in str(item) or "image" in item,
                            "has_rating": "aggregateRating" in str(item) or "aggregateRating" in item
                        })
                        
            except json.JSONDecodeError as e:
                print(f"    ⚠️ Schema JSON parse hiba: {e}")
                continue
            except (KeyError, TypeError, AttributeError) as e:
                print(f"    ⚠️ Schema feldolgozási hiba: {e}")
                continue
        
        return schema_info
    
    def check_meta_and_headings(self, html: str) -> Dict:
        """Metaadatok és heading struktúra részletes elemzése"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Title elemzés
        title = soup.title.string.strip() if soup.title and soup.title.string else None
        title_length = len(title) if title else 0
        
        # Meta description
        description_tag = soup.find('meta', attrs={'name': 'description'})
        description = description_tag.get('content', '').strip() if description_tag else None
        description_length = len(description) if description else 0
        
        # Open Graph és Twitter Card
        og_title = soup.find('meta', property='og:title')
        og_description = soup.find('meta', property='og:description')
        og_image = soup.find('meta', property='og:image')
        twitter_card = soup.find('meta', attrs={'name': 'twitter:card'})
        
        # Heading struktúra
        headings = {f"h{i}": len(soup.find_all(f"h{i}")) for i in range(1, 7)}
        
        # H1 elemzés
        h1_tags = soup.find_all('h1')
        h1_texts = [h1.get_text().strip() for h1 in h1_tags]
        
        return {
            "title": title,
            "title_length": title_length,
            "title_optimal": 30 <= title_length <= 60,
            "description": description,
            "description_length": description_length,
            "description_optimal": 120 <= description_length <= 160,
            "headings": headings,
            "h1_count": len(h1_tags),
            "h1_texts": h1_texts[:3],  # Max 3 H1 szöveg
            "has_og_tags": bool(og_title or og_description or og_image),
            "has_twitter_card": bool(twitter_card),
            "heading_hierarchy_valid": self._check_heading_hierarchy(headings)
        }
    
    def _check_heading_hierarchy(self, headings: Dict) -> bool:
        """Heading hierarchia ellenőrzése"""
        # H1 kell legyen
        if headings.get('h1', 0) == 0:
            return False
        
        # Ne legyen túl sok H1
        if headings.get('h1', 0) > 1:
            return False
        
        # Hierarchia ellenőrzés: ha van H3, legyen H2 is
        for i in range(3, 7):
            if headings.get(f'h{i}', 0) > 0 and headings.get(f'h{i-1}', 0) == 0:
                return False
        
        return True
    
    def check_mobile_friendly(self, html: str) -> Dict:
        """Mobile-friendly részletes ellenőrzés"""
        soup = BeautifulSoup(html, 'html.parser')
        
        result = {
            "has_viewport": False,
            "viewport_content": None,
            "responsive_images": False,
            "text_size_adjustable": False
        }
        
        # Viewport meta tag
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if viewport:
            content = viewport.get('content', '')
            result["has_viewport"] = True
            result["viewport_content"] = content
            result["responsive_images"] = 'width=device-width' in content
        
        # Responsive képek ellenőrzése
        images = soup.find_all('img')
        responsive_img_count = sum(1 for img in images if img.get('srcset') or 'responsive' in img.get('class', []))
        result["responsive_images"] = responsive_img_count > 0 if images else True
        
        return result
    
    def get_pagespeed_insights_with_retry(self, url: str, strategy: str = 'mobile', max_retries: int = 3) -> Optional[Dict]:
        """PageSpeed Insights API hívás retry logikával és jobb hibakezeléssel"""
        if not self.api_key:
            return None
        
        for attempt in range(max_retries):
            try:
                endpoint = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'
                
                params = {
                    'url': url,
                    'strategy': strategy,
                    'key': self.api_key,
                    'category': ['performance', 'seo']  # Csak a legfontosabbak a gyorsaság érdekében
                }
                
                # Progresszívan növekvő timeout
                timeout = 45 + (attempt * 15)  # 45, 60, 75 másodperc
                
                print(f"    PageSpeed {strategy} próbálkozás {attempt + 1}/{max_retries} (timeout: {timeout}s)")
                
                response = requests.get(endpoint, params=params, timeout=timeout)
                
                if response.status_code == 429:
                    wait_time = 60 + (attempt * 30)  # 60, 90, 120 másodperc
                    print(f"    Rate limit - várakozás {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                elif response.status_code != 200:
                    print(f"    PageSpeed API hiba ({strategy}): {response.status_code}")
                    if attempt < max_retries - 1:
                        time.sleep(10)
                        continue
                    return None
                
                data = response.json()
                categories = data.get('lighthouseResult', {}).get('categories', {})
                
                psi = {}
                for cat in ['performance', 'seo']:
                    score = categories.get(cat, {}).get('score')
                    psi[cat] = round(score * 100) if score is not None else None
                
                # Core Web Vitals (ha van)
                audits = data.get('lighthouseResult', {}).get('audits', {})
                if audits:
                    psi['core_web_vitals'] = {
                        'lcp': audits.get('largest-contentful-paint', {}).get('displayValue'),
                        'fid': audits.get('max-potential-fid', {}).get('displayValue'),
                        'cls': audits.get('cumulative-layout-shift', {}).get('displayValue')
                    }
                
                print(f"    ✓ PageSpeed sikeres ({strategy}): Perf {psi.get('performance', 'N/A')}, SEO {psi.get('seo', 'N/A')}")
                return psi
                
            except requests.exceptions.Timeout:
                print(f"    ⏰ Timeout ({strategy}) - {attempt + 1}. próbálkozás")
                if attempt < max_retries - 1:
                    wait_time = 30 + (attempt * 15)
                    print(f"    Várakozás {wait_time}s...")
                    time.sleep(wait_time)
                continue
            except requests.RequestException as e:
                print(f"    ❌ PageSpeed kapcsolati hiba ({strategy}): {str(e)[:100]}...")
                if attempt < max_retries - 1:
                    time.sleep(20)
                    continue
                return None
            except json.JSONDecodeError as e:
                print(f"    ❌ PageSpeed JSON parse hiba ({strategy}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(10)
                    continue
                return None
        
        print(f"    ❌ PageSpeed sikertelen {max_retries} próbálkozás után ({strategy})")
        return None
    
    def calculate_ai_readiness_score(self, result: Dict) -> int:
        """AI-readiness score számítás részletesebb metrikákkal"""
        score = 0
        
        # Robots.txt (10 pont)
        if result.get('robots_txt', {}).get('can_fetch'):
            score += 10
        
        # Title és meta (20 pont)
        meta = result.get('meta_and_headings', {})
        if meta.get('title_optimal'):
            score += 10
        elif meta.get('title'):
            score += 5
        
        if meta.get('description_optimal'):
            score += 10
        elif meta.get('description'):
            score += 5
        
        # Heading struktúra (15 pont)
        if meta.get('heading_hierarchy_valid'):
            score += 10
        if meta.get('h1_count') == 1:
            score += 5
        
        # Schema.org (20 pont)
        schema = result.get('schema', {})
        schema_count = sum(schema.get('count', {}).values())
        if schema_count > 0:
            score += min(20, schema_count * 5)
        if schema.get('has_breadcrumbs'):
            score += 5
        
        # Sitemap (10 pont)
        if result.get('sitemap', {}).get('exists'):
            score += 10
        
        # Mobile-friendly (10 pont)
        mobile = result.get('mobile_friendly', {})
        if mobile.get('has_viewport'):
            score += 5
        if mobile.get('responsive_images'):
            score += 5
        
        # Social media (5 pont)
        if meta.get('has_og_tags'):
            score += 3
        if meta.get('has_twitter_card'):
            score += 2
        
        # PageSpeed (10 pont)
        psi = result.get('pagespeed_insights', {})
        if psi:
            mobile_psi = psi.get('mobile', {})
            if mobile_psi.get('seo'):
                score += min(10, mobile_psi['seo'] // 10)
        
        return min(100, score)  # Max 100 pont
    
    def analyze_url(self, url: str, skip_pagespeed: bool = False) -> Dict:
        """Egy URL teljes elemzése - JAVÍTOTT paraméterekkel"""
        if not self.validate_url(url):
            return {"url": url, "error": "Érvénytelen URL"}
        
        result = {"url": url, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
        
        print(f"\n📊 Elemzés: {url}")
        
        try:
            # Robots.txt
            print("  🤖 Robots.txt...")
            can_fetch, robots_url = self.check_robots_txt(url)
            result["robots_txt"] = {"url": robots_url, "can_fetch": can_fetch}
            
            # Sitemap
            print("  🗺️ Sitemap...")
            sitemap_exists, sitemap_url, sitemap_size = self.check_sitemap(url)
            result["sitemap"] = {
                "exists": sitemap_exists, 
                "url": sitemap_url,
                "size_bytes": sitemap_size
            }
            
            # HTML lekérés
            print("  📄 HTML letöltés...")
            html = self.get_html(url)
            if not html:
                result["error"] = "HTML nem elérhető"
                return result
            
            # HTML méret
            result["html_size_kb"] = len(html) / 1024
            
            # Meta és headings
            print("  📝 Meta adatok...")
            result["meta_and_headings"] = self.check_meta_and_headings(html)
            
            # Schema - JAVÍTOTT hívás
            print("  🏗️ Schema.org...")
            result["schema"] = self.check_schema(html)
            
            # Mobile-friendly
            print("  📱 Mobile teszt...")
            result["mobile_friendly"] = self.check_mobile_friendly(html)
            
            # AI-specifikus metrikák - JAVÍTOTT hibakezeléssel
            print("  🧠 AI metrikák...")
            try:
                ai_metrics_analyzer = AISpecificMetrics()
                result["ai_metrics"] = ai_metrics_analyzer.analyze_ai_readiness(html, url)
                result["ai_metrics_summary"] = ai_metrics_analyzer.get_ai_readiness_summary(result["ai_metrics"])
            except Exception as e:
                print(f"    ⚠️ AI metrikák hiba: {e}")
                result["ai_metrics"] = {"error": str(e)}
                result["ai_metrics_summary"] = {"error": str(e)}
            
            # Tartalom minőség elemzés - JAVÍTOTT hibakezeléssel
            print("  📊 Tartalom elemzés...")
            try:
                content_analyzer = ContentQualityAnalyzer()
                content_quality = content_analyzer.analyze_content_quality(html, url)
                content_quality["overall_quality_score"] = content_analyzer.calculate_overall_quality_score(content_quality)
                result["content_quality"] = content_quality
            except Exception as e:
                print(f"    ⚠️ Tartalom elemzés hiba: {e}")
                result["content_quality"] = {"error": str(e)}
            
            # Multi-platform GEO elemzés - JAVÍTOTT hibakezeléssel
            print("  🔗 Platform kompatibilitás...")
            try:
                platform_analyzer = MultiPlatformGEOAnalyzer()
                result["platform_analysis"] = platform_analyzer.analyze_all_platforms(html, url)
                result["platform_suggestions"] = platform_analyzer.get_all_suggestions(result["platform_analysis"])
                result["platform_priorities"] = platform_analyzer.get_platform_priorities(result["platform_analysis"])
            except Exception as e:
                print(f"    ⚠️ Platform elemzés hiba: {e}")
                result["platform_analysis"] = {"error": str(e)}
                result["platform_suggestions"] = {"error": str(e)}
                result["platform_priorities"] = []
            
            # Index hint
            parsed = urlparse(url)
            result["index_hint"] = {
                "google_search_url": f"https://www.google.com/search?q=site:{parsed.netloc}",
                "bing_search_url": f"https://www.bing.com/search?q=site:{parsed.netloc}"
            }
            
            # PageSpeed Insights - JAVÍTVA skip_pagespeed kezeléssel
            pagespeed_results = {}
            if self.api_key and not skip_pagespeed:
                print("  ⚡ PageSpeed Insights...")
                
                # Először mobile (fontosabb)
                mobile_psi = self.get_pagespeed_insights_with_retry(url, 'mobile')
                if mobile_psi:
                    pagespeed_results["mobile"] = mobile_psi
                    
                    # Desktop csak akkor, ha mobile sikeres volt
                    print("  💻 PageSpeed Desktop...")
                    desktop_psi = self.get_pagespeed_insights_with_retry(url, 'desktop', max_retries=2)
                    if desktop_psi:
                        pagespeed_results["desktop"] = desktop_psi
            elif skip_pagespeed:
                print("  ⏭️ PageSpeed átugrása (beállítás szerint)")
            else:
                print("  ⚠️ PageSpeed átugrása (nincs API kulcs)")
            
            if pagespeed_results:
                result["pagespeed_insights"] = pagespeed_results
            
            # AI-readiness score
            result["ai_readiness_score"] = self.calculate_ai_readiness_score(result)
            
            # Automatikus javítási javaslatok - JAVÍTOTT hibakezeléssel
            print("  🔧 Javítási javaslatok...")
            try:
                auto_fix_generator = AutoFixGenerator()
                result["auto_fixes"] = auto_fix_generator.generate_all_fixes(result, url)
            except Exception as e:
                print(f"    ⚠️ Javítási javaslatok hiba: {e}")
                result["auto_fixes"] = {"error": str(e)}
            
            print(f"  ✅ Kész! AI Score: {result['ai_readiness_score']}/100")
            
        except Exception as e:
            # Általános hibakezelés
            import traceback
            print(f"  ❌ Kritikus hiba: {e}")
            traceback.print_exc()
            result["error"] = str(e)
            result["error_type"] = type(e).__name__
            result["ai_readiness_score"] = 0
        
        return result
    
    def analyze_urls_parallel(self, url_list: List[str], max_workers: int = 2, skip_pagespeed: bool = False) -> List[Dict]:
        """Több URL párhuzamos elemzése - JAVÍTOTT"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # JAVÍTÁS: skip_pagespeed átadása minden worker-nek
            future_to_url = {
                executor.submit(self._safe_analyze_url, url, skip_pagespeed): url 
                for url in url_list
            }
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"✓ Befejezve: {url}")
                except Exception as e:
                    # JAVÍTÁS: Részletesebb hibaüzenet
                    print(f"✗ Hiba {url} elemzésekor: {type(e).__name__}: {str(e)}")
                    import traceback
                    traceback.print_exc()  # Teljes stack trace kiírása
                    results.append({
                        "url": url, 
                        "error": str(e),
                        "error_type": type(e).__name__
                    })
        
        return results

def analyze_urls(url_list: List[str], api_key: Optional[str] = None, 
                output_file: str = "ai_readiness_full_report.json",
                parallel: bool = True, skip_pagespeed: bool = False,
                max_workers: int = 2) -> None:
    """Fő elemző függvény - JAVÍTOTT paraméterekkel"""
    
    analyzer = GEOAnalyzer(api_key)
    
    # Ha nincs API kulcs, automatikusan skip PageSpeed
    if not analyzer.api_key:
        skip_pagespeed = True
    
    print(f"{'='*50}")
    print(f"🚀 GEO Analyzer - {len(url_list)} URL elemzése")
    print(f"API kulcs: {'✅ Van' if analyzer.api_key else '❌ Nincs'}")
    print(f"PageSpeed: {'❌ Átugrás' if skip_pagespeed else '✅ Engedélyezve'}")
    print(f"Párhuzamos: {'✅ Igen' if parallel and len(url_list) > 1 else '❌ Nem'}")
    if parallel and len(url_list) > 1:
        print(f"Worker szálak: {max_workers}")
    print(f"{'='*50}")
    
    start_time = time.time()
    
    if parallel and len(url_list) > 1:
        # JAVÍTÁS: Paraméterek átadása
        results = analyzer.analyze_urls_parallel(url_list, max_workers, skip_pagespeed)
    else:
        results = []
        for url in url_list:
            # JAVÍTÁS: skip_pagespeed átadása
            result = analyzer.analyze_url(url, skip_pagespeed)
            results.append(result)
    
    # Eredmények mentése
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"💾 Jelentés mentve: {output_file}")
    except Exception as e:
        print(f"❌ Hiba a fájl mentésekor: {e}")
    
    elapsed_time = time.time() - start_time
    
    print(f"\n{'='*50}")
    print(f"✅ Elemzés befejezve!")
    print(f"⏱️ Időtartam: {elapsed_time:.1f} másodperc")
    print(f"💾 Jelentés: {output_file}")
    print(f"{'='*50}")
    
    # Összefoglaló statisztikák
    valid_results = [r for r in results if 'ai_readiness_score' in r and 'error' not in r]
    error_results = [r for r in results if 'error' in r]
    
    if valid_results:
        avg_score = sum(r['ai_readiness_score'] for r in valid_results) / len(valid_results)
        print(f"\n📊 Összefoglaló:")
        print(f"  • Sikeres elemzések: {len(valid_results)}/{len(results)}")
        print(f"  • Átlagos AI-readiness score: {avg_score:.1f}/100")
        
        # Top 3 és Bottom 3
        sorted_results = sorted(valid_results, key=lambda x: x['ai_readiness_score'], reverse=True)
        
        if sorted_results:
            print("\n🏆 Legjobb oldalak:")
            for r in sorted_results[:3]:
                print(f"  • {r['url']}: {r['ai_readiness_score']}/100")
        
        if len(sorted_results) > 3:
            print("\n🔧 Fejlesztendő oldalak:")
            for r in sorted_results[-3:]:
                if r['ai_readiness_score'] < 50:
                    print(f"  • {r['url']}: {r['ai_readiness_score']}/100")
    
    if error_results:
        print(f"\n⚠️ Hibás elemzések ({len(error_results)}):")
        for r in error_results:
            error_msg = r.get('error', 'Ismeretlen hiba')
            print(f"  • {r['url']}: {error_msg[:100]}...")  # Max 100 karakter


# Példa futtatás
if __name__ == "__main__":
    urls_to_test = [
        "https://www.example.com",
        "https://www.wikipedia.org",
        "https://www.github.com"
    ]
    
    # API kulcs a környezeti változóból
    api_key = GOOGLE_API_KEY
    
    if not api_key:
        print("⚠️ Figyelem: Google API kulcs nincs beállítva!")
        print("Állítsd be a .env fájlban: GOOGLE_API_KEY=your_api_key")
        print("PageSpeed Insights nélkül fut az elemzés.\n")
    
    # Gyorsabb futtatás: skip_pagespeed=True ha nincs szükség PageSpeed-re
    analyze_urls(urls_to_test, api_key, parallel=True, skip_pagespeed=False)
    
    # HTML report generálás
    try:
        from report import generate_html_report
        generate_html_report()
    except ImportError:
        print("⚠️ report.py nem található - HTML jelentés kihagyva")