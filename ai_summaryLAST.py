import json
from openai import OpenAI
from typing import Dict, Any, Optional, Tuple, List, Union
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

def get_openai_api_key():
    """Biztonságos API kulcs lekérés Streamlit függőségek nélkül"""
    load_dotenv()
    return os.getenv("OPENAI_API_KEY")

class AISummaryGenerator:
    """
    OpenAI API-val történő összefoglaló és javaslat generálás - OPTIMALIZÁLT VERZIÓ
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializálja az AI Summary Generator-t
        
        Args:
            api_key: OpenAI API kulcs (ha nincs megadva, környezetből veszi)
        """
        self.api_key = api_key or get_openai_api_key()
        if not self.api_key:
            raise ValueError("OpenAI API kulcs szükséges. Állítsd be a OPENAI_API_KEY environment változót.")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_summary_and_recommendations(self, json_data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Tuple[str, str]:
        """
        Generál egy összefoglalót és javaslatokat a JSON adatok alapján
        
        Args:
            json_data: Az elemzés eredményét tartalmazó JSON adatok (dict vagy list)
            
        Returns:
            Tuple[str, str]: (összefoglaló, javaslatok)
        """
        try:
            # Kompakt, de teljes körű adatkinyerés
            analysis_summary = self._create_compact_summary(json_data)
            
            # Token méret ellenőrzés és optimalizálás
            json_str = json.dumps(analysis_summary, indent=2, ensure_ascii=False)
            estimated_tokens = len(json_str) // 4  # Durva becslés
            
            # Ha túl nagy, további tömörítés
            if estimated_tokens > 4000:
                analysis_summary = self._ultra_compact_summary(analysis_summary)
                json_str = json.dumps(analysis_summary, indent=2, ensure_ascii=False)
            
            # OpenAI API hívás - ERŐS JSON KÉNYSZERÍTÉS
            try:
                # Először próbáljuk response_format paraméterrel (GPT-4-turbo támogatja)
                response = self.client.chat.completions.create(
                    model="gpt-4-turbo-preview",  # vagy "gpt-4-1106-preview"
                    response_format={"type": "json_object"},  # JSON mód
                    messages=[
                        {
                            "role": "system",
                            "content": """Te egy GEO (Generative Engine Optimization) szakértő vagy.
Válaszolj CSAK valid JSON formátumban a megadott struktúrában."""
                        },
                        {
                            "role": "user", 
                            "content": f"""Elemezd ezt a GEO audit eredményt és készíts részletes összefoglalót és javaslatokat.

AUDIT EREDMÉNYEK:
{json_str}

Készíts:
1. Részletes ÖSSZEFOGLALÓ (600-800 szó), amely tartalmazza:
   - AI Readiness Score értékelése (átlag: {analysis_summary.get('overview', {}).get('avg_ai_score', 0)}/100)
   - URL-enkénti teljesítmény
   - Főbb problémák gyakorisága
   - Platform kompatibilitás
   - Technikai hiányosságok

2. Konkrét JAVASLATOK (600-800 szó), prioritizálva:
   - Kritikus javítások
   - Quick wins (gyors eredmények)
   - Platform-specifikus optimalizációk
   - Várható score javulás

Válaszolj PONTOSAN ebben a JSON struktúrában:
{{
    "summary": "Ide írd a részletes összefoglalót. Használj konkrét számokat, százalékokat. Említsd meg az átlagos AI score-t, a legjobb és legrosszabb teljesítményű URL-eket, a leggyakoribb problémákat.",
    "recommendations": "Ide írd a prioritizált javaslatokat. Kezdd a kritikus problémákkal, majd a quick wins lehetőségekkel. Adj konkrét megoldásokat és becsüld meg a várható javulást."
}}"""
                        }
                    ],
                    temperature=0.7,
                    max_tokens=2500
                )
            except Exception as e:
                # Ha nem támogatja a response_format-ot, használjuk a standard módot
                logger.info(f"JSON response format nem támogatott, standard mód: {e}")
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": """Te egy GEO szakértő vagy. 
KRITIKUS: Válaszod CSAK valid JSON lehet {"summary": "...", "recommendations": "..."} formátumban!
Ne használj markdown-t, csak tiszta JSON-t!"""
                        },
                        {
                            "role": "user", 
                            "content": f"""GEO audit elemzése:

{json_str}

Átlag AI Score: {analysis_summary.get('overview', {}).get('avg_ai_score', 0)}/100
URL-ek száma: {analysis_summary.get('overview', {}).get('urls_analyzed', 0)}

Top problémák: {', '.join([f"{issue[0]} ({issue[1]}x)" for issue in analysis_summary.get('common_issues', [])[:3]])}

FONTOS: Válaszolj CSAK ezzel a JSON struktúrával:
{{"summary": "részletes összefoglaló szöveg", "recommendations": "konkrét javaslatok szövege"}}"""
                        }
                    ],
                    temperature=0.7,
                    max_tokens=2500
                )
            
            # Válasz feldolgozása - ROBUSZTUSABB JSON PARSING
            ai_response = response.choices[0].message.content.strip()
            logger.info(f"OpenAI válasz első 200 karakter: {ai_response[:200]}...")
            
            # Tisztítsuk meg a választ minden felesleges karaktertől
            cleaned_response = ai_response
            
            # Markdown code block eltávolítása
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[-1].split("```")[0].strip()
            elif "```" in cleaned_response:
                parts = cleaned_response.split("```")
                if len(parts) >= 2:
                    cleaned_response = parts[1].strip()
            
            # További tisztítás
            cleaned_response = cleaned_response.strip()
            if cleaned_response.startswith("json"):
                cleaned_response = cleaned_response[4:].strip()
            
            logger.info(f"Tisztított válasz első 200 karakter: {cleaned_response[:200]}...")
            
            # Első próbálkozás: tiszta JSON parse
            try:
                parsed_response = json.loads(cleaned_response)
                summary = parsed_response.get("summary", "")
                recommendations = parsed_response.get("recommendations", "")
                
                # Ellenőrizzük, hogy valódi tartalom-e
                if summary and recommendations and len(summary) > 100 and len(recommendations) > 100:
                    logger.info("JSON parsing sikeres")
                    return summary, recommendations
                else:
                    logger.warning("JSON parse sikeres de túl rövid vagy üres a tartalom")
                    raise ValueError("Incomplete response")
                    
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"JSON parse hiba: {e}")
                logger.warning(f"Problémás JSON: {cleaned_response[:500]}...")
                
                # Második próbálkozás: regex alapú kinyerés
                import re
                
                # Többféle pattern próbálkozás
                patterns = [
                    # Standard JSON
                    (r'"summary"\s*:\s*"([^"]*(?:\\.[^"]*)*)"', r'"recommendations"\s*:\s*"([^"]*(?:\\.[^"]*)*)"'),
                    # Aposztróf
                    (r"'summary'\s*:\s*'([^']*(?:\\.[^']*)*)'", r"'recommendations'\s*:\s*'([^']*(?:\\.[^']*)*)'"),
                    # Többsoros JSON
                    (r'"summary"\s*:\s*"([\s\S]*?)"(?:,\s*"recommendations")', r'"recommendations"\s*:\s*"([\s\S]*?)"(?:\s*\})'),
                ]
                
                summary = None
                recommendations = None
                
                for sum_pattern, rec_pattern in patterns:
                    if not summary:
                        sum_match = re.search(sum_pattern, cleaned_response, re.DOTALL)
                        if sum_match:
                            summary = sum_match.group(1)
                            # Escape karakterek kezelése
                            summary = summary.replace('\\n', '\n').replace('\\"', '"').replace('\\t', '    ')
                    
                    if not recommendations:
                        rec_match = re.search(rec_pattern, cleaned_response, re.DOTALL)
                        if rec_match:
                            recommendations = rec_match.group(1)
                            recommendations = recommendations.replace('\\n', '\n').replace('\\"', '"').replace('\\t', '    ')
                
                if summary and recommendations:
                    logger.info("Regex alapú JSON kinyerés sikeres")
                    return summary, recommendations
                
                # Harmadik próbálkozás: manuális feldolgozás
                logger.warning("Regex parsing sikertelen, manuális feldolgozás...")
                return self._parse_ai_response_manually(ai_response)
                
        except Exception as e:
            logger.error(f"Hiba az AI összefoglaló generálása során: {str(e)}")
            # Negyedik próbálkozás: fallback summary generálás
            logger.info("Fallback summary generálás...")
            return self._fallback_summary_generation(analysis_summary)
                
        except Exception as e:
            logger.error(f"Kritikus hiba az AI összefoglaló generálása során: {str(e)}")
            
            # Végső fallback: legalább alapinformációkat adjunk
            try:
                # Ha van analysis_summary, használjuk a fallback generátort
                if 'analysis_summary' in locals():
                    return self._fallback_summary_generation(analysis_summary)
            except:
                pass
            
            # Ha semmi sem működik, általános hibaüzenet
            return (
                "Az AI összefoglaló generálása sikertelen volt. Kérlek ellenőrizd az OpenAI API kulcsot és a kapcsolatot.",
                "A javaslatok automatikus generálása nem sikerült. Tekintsd át manuálisan az elemzési eredményeket."
            )
    
    def _create_compact_summary(self, data: Union[Dict, List]) -> Dict[str, Any]:
        """
        Kompakt összefoglaló készítése - maximum 4000 token méretű
        """
        try:
            # Normalizáljuk az adatot - lehet dict vagy list
            if isinstance(data, dict):
                if 'results' in data:
                    results = data['results']
                else:
                    results = [data]
            elif isinstance(data, list):
                results = data
            else:
                results = []
            
            # Szűrjük ki a hibás eredményeket
            valid_results = [
                r for r in results 
                if isinstance(r, dict) and 'error' not in r and 'ai_readiness_score' in r
            ]
            
            if not valid_results:
                return {"error": "Nincs érvényes elemzési eredmény"}
            
            # Kompakt összefoglaló struktúra
            summary = {
                "overview": {
                    "urls_analyzed": len(valid_results),
                    "avg_ai_score": round(sum(r.get('ai_readiness_score', 0) for r in valid_results) / len(valid_results), 1)
                },
                "urls": []
            }
            
            # Minden URL kompakt összefoglalója (max 3 URL részletesen)
            for result in valid_results[:3]:  # Limitáljuk 3 URL-re a méret miatt
                url_summary = self._extract_url_essentials(result)
                summary["urls"].append(url_summary)
            
            # Ha több mint 3 URL van, csak az alapokat adjuk hozzá
            if len(valid_results) > 3:
                summary["additional_urls"] = []
                for result in valid_results[3:]:
                    summary["additional_urls"].append({
                        "url": result.get("url", "N/A"),
                        "score": result.get("ai_readiness_score", 0),
                        "main_issues": self._get_top_issues(result)[:2]  # Csak 2 fő probléma
                    })
            
            # Globális statisztikák
            all_scores = [r.get('ai_readiness_score', 0) for r in valid_results]
            summary["statistics"] = {
                "min_score": min(all_scores),
                "max_score": max(all_scores),
                "excellent": len([s for s in all_scores if s >= 85]),
                "good": len([s for s in all_scores if 60 <= s < 85]),
                "poor": len([s for s in all_scores if s < 40])
            }
            
            # Top problémák összesítése
            all_issues = []
            for r in valid_results:
                all_issues.extend(self._get_top_issues(r))
            
            # Probléma gyakoriság
            issue_freq = {}
            for issue in all_issues:
                issue_freq[issue] = issue_freq.get(issue, 0) + 1
            
            # Top 5 leggyakoribb probléma
            summary["common_issues"] = sorted(
                issue_freq.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            
            return summary
            
        except Exception as e:
            logger.error(f"Kompakt összefoglaló készítése sikertelen: {str(e)}")
            return {"error": str(e)}
    
    def _extract_url_essentials(self, result: Dict) -> Dict[str, Any]:
        """
        Egy URL lényegi adatainak kinyerése - kompakt formában
        """
        url = result.get("url", "N/A")
        score = result.get("ai_readiness_score", 0)
        
        # Meta adatok
        meta = result.get("meta_and_headings", {})
        meta_summary = {
            "title_ok": meta.get("title_optimal", False),
            "desc_ok": meta.get("description_optimal", False),
            "h1_count": meta.get("h1_count", 0),
            "social": meta.get("has_og_tags", False) or meta.get("has_twitter_card", False)
        }
        
        # Schema
        schema = result.get("schema", {})
        schema_count = 0
        if isinstance(schema.get("count"), dict):
            schema_count = sum(schema["count"].values())
        elif isinstance(schema.get("count"), (int, float)):
            schema_count = schema["count"]
        
        # Content
        content = result.get("content_quality", {})
        content_score = content.get("overall_quality_score", 0) if not content.get("error") else 0
        word_count = content.get("readability", {}).get("word_count", 0) if not content.get("error") else 0
        
        # Platforms
        platforms = result.get("platform_analysis", {})
        platform_scores = {}
        if platforms and not platforms.get("error"):
            for p_name in ["chatgpt", "claude", "gemini", "bing_chat"]:
                if p_name in platforms and isinstance(platforms[p_name], dict):
                    platform_scores[p_name] = round(platforms[p_name].get("compatibility_score", 0), 0)
        
        # PageSpeed
        psi = result.get("pagespeed_insights", {})
        perf_mobile = psi.get("mobile", {}).get("performance", 0) if psi else 0
        
        # Technical
        tech_ok = (
            result.get("robots_txt", {}).get("can_fetch", False) and
            result.get("sitemap", {}).get("exists", False) and
            result.get("mobile_friendly", {}).get("has_viewport", False)
        )
        
        return {
            "url": url,
            "ai_score": score,
            "level": self._get_level(score),
            "meta": meta_summary,
            "schema_count": schema_count,
            "content_score": round(content_score, 0),
            "word_count": word_count,
            "platforms": platform_scores,
            "mobile_perf": perf_mobile,
            "tech_ok": tech_ok,
            "top_issues": self._get_top_issues(result)[:3],  # Max 3 issue
            "quick_wins": self._get_quick_wins(result)[:2]   # Max 2 quick win
        }
    
    def _ultra_compact_summary(self, summary: Dict) -> Dict[str, Any]:
        """
        Ultra kompakt összefoglaló ha még mindig túl nagy
        """
        # Csak az első URL részletes adatai + statisztikák
        ultra_compact = {
            "overview": summary.get("overview", {}),
            "first_url": summary.get("urls", [{}])[0] if summary.get("urls") else {},
            "other_urls_count": len(summary.get("urls", [])) - 1 + len(summary.get("additional_urls", [])),
            "statistics": summary.get("statistics", {}),
            "top_issues": summary.get("common_issues", [])[:3]
        }
        
        # További URL-ek csak score-ral
        if len(summary.get("urls", [])) > 1:
            ultra_compact["other_scores"] = [
                {"url": u.get("url", "")[:50], "score": u.get("ai_score", 0)} 
                for u in summary.get("urls", [])[1:3]
            ]
        
        return ultra_compact
    
    def _get_level(self, score: float) -> str:
        """Szint meghatározás"""
        if score >= 85: return "Kiváló"
        if score >= 60: return "Jó"
        if score >= 40: return "Közepes"
        return "Gyenge"
    
    def _get_top_issues(self, result: Dict) -> List[str]:
        """Top problémák azonosítása"""
        issues = []
        
        # Meta
        meta = result.get("meta_and_headings", {})
        if not meta.get("title_optimal"):
            issues.append("Title nem optimális")
        if not meta.get("description_optimal"):
            issues.append("Description hiányzik/rossz")
        if meta.get("h1_count", 0) != 1:
            issues.append(f"H1 probléma ({meta.get('h1_count', 0)} db)")
        
        # Schema
        schema = result.get("schema", {})
        schema_count = 0
        if isinstance(schema.get("count"), dict):
            schema_count = sum(schema["count"].values())
        elif isinstance(schema.get("count"), (int, float)):
            schema_count = schema["count"]
        
        if schema_count == 0:
            issues.append("Nincs Schema markup")
        
        # Content
        content = result.get("content_quality", {})
        if not content.get("error"):
            word_count = content.get("readability", {}).get("word_count", 0)
            if word_count < 300:
                issues.append(f"Kevés tartalom ({word_count} szó)")
        
        # Technical
        if not result.get("robots_txt", {}).get("can_fetch"):
            issues.append("Robots.txt tiltás")
        if not result.get("sitemap", {}).get("exists"):
            issues.append("Nincs sitemap")
        if not result.get("mobile_friendly", {}).get("has_viewport"):
            issues.append("Nincs mobile viewport")
        
        # Performance
        psi = result.get("pagespeed_insights", {})
        if psi:
            mobile_perf = psi.get("mobile", {}).get("performance", 100)
            if mobile_perf < 50:
                issues.append(f"Gyenge mobil sebesség ({mobile_perf})")
        
        return issues
    
    def _get_quick_wins(self, result: Dict) -> List[str]:
        """Gyors javítások"""
        wins = []
        
        meta = result.get("meta_and_headings", {})
        if not meta.get("title_optimal"):
            wins.append("Title tag optimalizálás (30-60 karakter)")
        
        if not meta.get("description"):
            wins.append("Meta description hozzáadása")
        
        schema = result.get("schema", {})
        schema_count = 0
        if isinstance(schema.get("count"), dict):
            schema_count = sum(schema["count"].values())
        
        if schema_count == 0:
            wins.append("FAQ vagy Article Schema hozzáadása")
        
        if not meta.get("has_og_tags"):
            wins.append("Open Graph tagek hozzáadása")
        
        if not result.get("sitemap", {}).get("exists"):
            wins.append("XML sitemap létrehozása")
        
        return wins[:3]  # Max 3
    
    def _fallback_summary_generation(self, analysis_summary: Dict) -> Tuple[str, str]:
        """
        Fallback összefoglaló generálás ha az AI nem ad valid JSON-t
        """
        try:
            overview = analysis_summary.get("overview", {})
            urls = analysis_summary.get("urls", [])
            stats = analysis_summary.get("statistics", {})
            issues = analysis_summary.get("common_issues", [])
            
            # Összefoglaló generálása
            summary_parts = []
            
            # Áttekintés
            avg_score = overview.get("avg_ai_score", 0)
            url_count = overview.get("urls_analyzed", 0)
            
            summary_parts.append(f"Az elemzés {url_count} URL vizsgálatát tartalmazza, átlagos AI Readiness Score: {avg_score}/100.")
            
            # Szint értékelés
            if avg_score >= 85:
                level_text = "kiváló, az oldalak készen állnak az AI platformokra"
            elif avg_score >= 60:
                level_text = "jó, de van még fejlesztési potenciál"
            elif avg_score >= 40:
                level_text = "közepes, jelentős optimalizációra van szükség"
            else:
                level_text = "gyenge, sürgős beavatkozás szükséges"
            
            summary_parts.append(f"Az átlagos teljesítmény {level_text}.")
            
            # Statisztikák
            if stats:
                summary_parts.append(f"\nStatisztikák: {stats.get('excellent', 0)} kiváló, {stats.get('good', 0)} jó, {stats.get('poor', 0)} gyenge teljesítményű oldal.")
                summary_parts.append(f"Legjobb eredmény: {stats.get('max_score', 0)}/100, leggyengébb: {stats.get('min_score', 0)}/100.")
            
            # URL részletek
            if urls:
                summary_parts.append("\nRészletes eredmények:")
                for i, url_data in enumerate(urls[:3], 1):
                    url = url_data.get("url", "N/A")
                    score = url_data.get("ai_score", 0)
                    level = url_data.get("level", "N/A")
                    top_issues = url_data.get("top_issues", [])
                    
                    summary_parts.append(f"\n{i}. {url}: {score}/100 ({level})")
                    if top_issues:
                        summary_parts.append(f"   Főbb problémák: {', '.join(top_issues[:3])}")
            
            # Leggyakoribb problémák
            if issues:
                summary_parts.append("\n\nLeggyakoribb problémák az összes oldalon:")
                for issue, count in issues[:5]:
                    summary_parts.append(f"- {issue}: {count} alkalommal")
            
            summary = " ".join(summary_parts)
            
            # Javaslatok generálása
            rec_parts = []
            
            rec_parts.append("Prioritizált fejlesztési javaslatok:\n")
            
            # Kritikus javítások
            if avg_score < 40:
                rec_parts.append("KRITIKUS PRIORITÁS:")
                rec_parts.append("1. Schema.org markup azonnali implementálása minden oldalon")
                rec_parts.append("2. Meta title és description optimalizálás (30-60 és 120-160 karakter)")
                rec_parts.append("3. Mobile viewport meta tag hozzáadása")
            
            # Általános javaslatok az issues alapján
            rec_parts.append("\nFőbb teendők a problémák alapján:")
            
            issue_solutions = {
                "Title nem optimális": "Optimalizáld a title tageket 30-60 karakterre, használj kulcsszavakat",
                "Description hiányzik/rossz": "Adj hozzá meta description-t 120-160 karakterrel",
                "Nincs Schema markup": "Implementálj FAQ vagy Article schema-t JSON-LD formátumban",
                "Kevés tartalom": "Bővítsd a tartalmat minimum 300-500 szóra",
                "Nincs sitemap": "Hozz létre XML sitemap-et és add hozzá a robots.txt-hez",
                "Nincs mobile viewport": "Add hozzá: <meta name='viewport' content='width=device-width, initial-scale=1'>",
                "H1 probléma": "Használj pontosan 1 db H1 címsort oldalanként"
            }
            
            rec_num = 1
            for issue, count in issues[:5]:
                if issue in issue_solutions:
                    rec_parts.append(f"{rec_num}. {issue_solutions[issue]} (Érint: {count} oldalt)")
                    rec_num += 1
            
            # Quick wins
            if urls and urls[0].get("quick_wins"):
                rec_parts.append("\n\nGyors eredmények (Quick Wins):")
                for win in urls[0]["quick_wins"][:3]:
                    rec_parts.append(f"- {win}")
            
            # Platform-specifikus
            rec_parts.append("\n\nPlatform-specifikus optimalizáció:")
            rec_parts.append("- ChatGPT: Strukturált tartalom, Q&A formátum, lépésenkénti útmutatók")
            rec_parts.append("- Claude: Részletes kontextus, hivatkozások, hosszú formátumú tartalom")
            rec_parts.append("- Gemini: Friss információk, multimédia, schema markup")
            rec_parts.append("- Bing Chat: Külső források, időszerű tartalom, fact-checking")
            
            # Várható javulás
            improvement = min(100 - avg_score, 30)
            rec_parts.append(f"\n\nVárható AI Score javulás a javaslatok implementálása után: +{improvement} pont")
            
            recommendations = "\n".join(rec_parts)
            
            return summary, recommendations
            
        except Exception as e:
            logger.error(f"Fallback generation hiba: {str(e)}")
            return (
                "Az automatikus összefoglaló generálás sikertelen volt.",
                "Kérlek ellenőrizd manuálisan az elemzési eredményeket."
            )
    
    def _parse_ai_response_manually(self, response: str) -> Tuple[str, str]:
        """
        Robusztus manuális feldolgozás különböző AI válasz formátumokhoz
        """
        try:
            import re
            
            logger.info(f"Manuális parsing indítása, válasz hossza: {len(response)} karakter")
            
            # Különböző elválasztók keresése
            patterns = [
                # JSON-szerű struktúra idézőjelek nélkül
                (r'summary\s*:\s*(.*?)(?:recommendations|javaslat|$)', r'recommendations\s*:\s*(.*)'),
                # Számozott lista
                (r'1\.\s*(?:ÖSSZEFOGLALÓ|Summary|Összefoglaló)[:\s]*(.*?)(?:2\.|recommendations|javaslat|$)', 
                 r'2\.\s*(?:JAVASLATOK|Recommendations|Javaslatok)[:\s]*(.*)'),
                # Markdown fejlécek
                (r'#+\s*(?:Összefoglaló|Summary|ÖSSZEFOGLALÓ)(.*?)(?:#+\s*(?:Javaslatok|Recommendations)|$)', 
                 r'#+\s*(?:Javaslatok|Recommendations|JAVASLATOK)(.*)'),
                # Nagybetűs elválasztók
                (r'ÖSSZEFOGLALÓ[:\s]*(.*?)(?:JAVASLATOK|RECOMMENDATIONS|$)', 
                 r'(?:JAVASLATOK|RECOMMENDATIONS)[:\s]*(.*)'),
                # Bármilyen szöveg "summary" és "recommendations" között
                (r'(?:summary|összefoglaló)[:\s]*(.*?)(?:recommendations|javaslatok|ajánlások)', 
                 r'(?:recommendations|javaslatok|ajánlások)[:\s]*(.*)'),
            ]
            
            summary = None
            recommendations = None
            
            # Próbáljuk meg az összes pattern-t
            for sum_pattern, rec_pattern in patterns:
                if not summary:
                    sum_match = re.search(sum_pattern, response, re.IGNORECASE | re.DOTALL)
                    if sum_match:
                        summary = sum_match.group(1).strip()
                        logger.info(f"Summary pattern match találat, hossz: {len(summary)}")
                
                if not recommendations:
                    rec_match = re.search(rec_pattern, response, re.IGNORECASE | re.DOTALL)
                    if rec_match:
                        recommendations = rec_match.group(1).strip()
                        logger.info(f"Recommendations pattern match találat, hossz: {len(recommendations)}")
                
                if summary and recommendations:
                    break
            
            # Ha még mindig nincs, próbáljuk meg a válasz felezésével
            if not summary or not recommendations:
                logger.info("Pattern matching sikertelen, válasz felezése...")
                # Keressünk természetes töréspontot
                break_points = [
                    response.find("Javaslatok"),
                    response.find("JAVASLATOK"),
                    response.find("Recommendations"),
                    response.find("recommendations"),
                    response.find("2."),
                    len(response) // 2  # Végső esetben felezzük
                ]
                
                # Első valid töréspont
                break_point = next((p for p in break_points if p > 100), len(response) // 2)
                logger.info(f"Töréspont: {break_point}")
                
                if not summary:
                    summary = response[:break_point].strip()
                if not recommendations:
                    recommendations = response[break_point:].strip()
            
            # Tisztítás
            # Eltávolítjuk a felesleges karaktereket és formázásokat
            if summary:
                # JSON maradványok
                summary = summary.replace('"', '').replace('{', '').replace('}', '').replace("'", "")
                summary = summary.replace('\\n', '\n').replace('\\t', ' ')
                # Markdown
                summary = re.sub(r'[#*`]', '', summary)
                # Többszörös szóközök
                summary = re.sub(r'\s+', ' ', summary)
                # Címek és kulcsszavak eltávolítása
                summary = re.sub(r'^(summary|összefoglaló)[:\s]*', '', summary, flags=re.IGNORECASE)
                summary = summary.strip()
            
            if recommendations:
                # JSON maradványok
                recommendations = recommendations.replace('"', '').replace('{', '').replace('}', '').replace("'", "")
                recommendations = recommendations.replace('\\n', '\n').replace('\\t', ' ')
                # Markdown
                recommendations = re.sub(r'[#*`]', '', recommendations)
                # Többszörös szóközök
                recommendations = re.sub(r'\s+', ' ', recommendations)
                # Címek és kulcsszavak eltávolítása
                recommendations = re.sub(r'^(recommendations|javaslatok|ajánlások)[:\s]*', '', recommendations, flags=re.IGNORECASE)
                recommendations = recommendations.strip()
            
            # Ellenőrzés
            if summary and len(summary) > 50:
                logger.info("Manuális parsing sikeres")
                return (summary, recommendations or "A javaslatok automatikus generálása részben sikertelen. Kérlek tekintsd át manuálisan az elemzési eredményeket.")
            else:
                # Ha túl rövid, használjuk a teljes választ
                logger.warning("Manuális parsing nem adott megfelelő eredményt, teljes válasz használata")
                return (
                    response[:1500] if len(response) > 1500 else response,
                    "A javaslatok automatikus generálása sikertelen. Kérlek tekintsd át manuálisan az elemzési eredményeket és készíts optimalizálási tervet."
                )
            
        except Exception as e:
            logger.error(f"Manuális parsing kritikus hiba: {str(e)}")
            # Végső fallback - legalább valami információt adjunk
            return (
                response[:1000] if len(response) > 1000 else response,
                "Automatikus javaslat generálás sikertelen. Manuális elemzés szükséges."
            )

def generate_ai_summary_from_file(json_file_path: str) -> Tuple[str, str]:
    """
    Segédfüggvény: AI összefoglaló generálása JSON fájlból
    
    Args:
        json_file_path: A JSON fájl elérési útja
        
    Returns:
        Tuple[str, str]: (összefoglaló, javaslatok)
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        generator = AISummaryGenerator()
        return generator.generate_summary_and_recommendations(data)
        
    except FileNotFoundError:
        logger.error(f"JSON fájl nem található: {json_file_path}")
        return "A JSON fájl nem található.", "Kérlek, futtasd le előbb az elemzést."
    except Exception as e:
        logger.error(f"Hiba a fájl feldolgozása során: {str(e)}")
        return "Hiba történt a fájl feldolgozása során.", "Ellenőrizd a fájl formátumát és próbáld újra."

if __name__ == "__main__":
    # Teszt futtatás
    # Példa: lista formátumú input (ahogy a való életben is érkezik)
    test_data = [
        {
            "url": "https://example.com",
            "ai_readiness_score": 75.5,
            "meta_and_headings": {
                "title": "Test Title - Example Site",
                "title_length": 25,
                "title_optimal": False,
                "description": "This is a test description for the example website",
                "description_length": 50,
                "description_optimal": False,
                "h1_count": 1,
                "heading_hierarchy_valid": True,
                "has_og_tags": True,
                "has_twitter_card": False,
                "headings": {"h1": 1, "h2": 3, "h3": 5}
            },
            "schema": {
                "count": {"Article": 1, "BreadcrumbList": 1},
                "has_breadcrumbs": True,
                "validation_status": "enhanced",
                "schema_completeness_score": 85
            },
            "content_quality": {
                "overall_quality_score": 72,
                "readability": {
                    "word_count": 500,
                    "readability_score": 80
                },
                "keyword_analysis": {
                    "vocabulary_richness": 0.65
                }
            },
            "platform_analysis": {
                "chatgpt": {
                    "compatibility_score": 75,
                    "hybrid_score": 78,
                    "ai_score": 80
                },
                "claude": {
                    "compatibility_score": 70,
                    "hybrid_score": 72,
                    "ai_score": 74
                }
            },
            "robots_txt": {"can_fetch": True},
            "sitemap": {"exists": True},
            "mobile_friendly": {"has_viewport": True},
            "pagespeed_insights": {
                "mobile": {"performance": 65, "seo": 88}
            }
        },
        {
            "url": "https://example2.com",
            "ai_readiness_score": 45.2,
            "meta_and_headings": {
                "title": "Short",
                "title_length": 5,
                "title_optimal": False,
                "description": None,
                "description_length": 0,
                "description_optimal": False,
                "h1_count": 0,
                "heading_hierarchy_valid": False,
                "has_og_tags": False,
                "has_twitter_card": False
            },
            "schema": {
                "count": {},
                "has_breadcrumbs": False,
                "validation_status": "standard"
            },
            "content_quality": {
                "overall_quality_score": 35,
                "readability": {
                    "word_count": 150,
                    "readability_score": 45
                }
            },
            "robots_txt": {"can_fetch": True},
            "sitemap": {"exists": False},
            "mobile_friendly": {"has_viewport": False}
        }
    ]
    
    try:
        generator = AISummaryGenerator()
        print("🚀 AI Summary Generator teszt indítása...")
        print(f"📊 {len(test_data)} URL elemzése")
        
        summary, recommendations = generator.generate_summary_and_recommendations(test_data)
        
        print("\n" + "="*60)
        print("📝 ÖSSZEFOGLALÓ:")
        print("="*60)
        print(summary)
        
        print("\n" + "="*60)
        print("💡 JAVASLATOK:")
        print("="*60)
        print(recommendations)
        
        print("\n✅ Teszt sikeresen lefutott!")
        
    except Exception as e:
        print(f"❌ Teszt hiba: {str(e)}")
        import traceback
        traceback.print_exc()