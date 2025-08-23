import json
from openai import OpenAI
from typing import Dict, Any, Optional, Tuple, List
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
    OpenAI API-val történő összefoglaló és javaslat generálás - TURBÓZOTT VERZIÓ
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
    
    def generate_summary_and_recommendations(self, json_data: Dict[str, Any]) -> Tuple[str, str]:
        """
        Generál egy összefoglalót és javaslatokat a JSON adatok alapján
        
        Args:
            json_data: Az elemzés eredményét tartalmazó JSON adatok
            
        Returns:
            Tuple[str, str]: (összefoglaló, javaslatok)
        """
        try:
            # Kompakt adatok kinyerése a token limit miatt
            compact_data = self._create_compact_analysis(json_data)
            
            # Rövid prompt a token limit betartásához
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Te egy GEO (Generative Engine Optimization) szakértő vagy. KRITIKUS: Válaszolj CSAK valid JSON formátumban: {\"summary\": \"...\", \"recommendations\": \"...\"}"
                    },
                    {
                        "role": "user", 
                        "content": f"""GEO audit eredmények elemzése:

1. ÖSSZEFOGLALÓ (max 600 szó): AI readiness score, meta adatok, schema, tartalom, platform kompatibilitás
2. JAVASLATOK (max 600 szó): Prioritizált javítási terv

Adatok:
{json.dumps(compact_data, ensure_ascii=False)}

FONTOS: Válaszolj CSAK ezzel a JSON struktúrával, semmi mással:
{{"summary": "...", "recommendations": "..."}}"""
                    }
                ],
                temperature=0.7,
                max_tokens=2000  # Biztonságos token limit
            )
            
            # Válasz feldolgozása
            ai_response = response.choices[0].message.content.strip()
            logger.info(f"OpenAI válasz első 200 karakter: {ai_response[:200]}...")
            
            # Tisztítás
            cleaned_response = ai_response
            
            # Markdown code block eltávolítása
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[-1].split("```")[0].strip()
            elif "```" in cleaned_response:
                parts = cleaned_response.split("```")
                if len(parts) >= 2:
                    cleaned_response = parts[1].strip()
            
            cleaned_response = cleaned_response.strip()
            if cleaned_response.startswith("json"):
                cleaned_response = cleaned_response[4:].strip()
            
            logger.info(f"Tisztított válasz első 200 karakter: {cleaned_response[:200]}...")
            
            try:
                # JSON parsing
                parsed_response = json.loads(cleaned_response)
                summary = parsed_response.get("summary", "Nem sikerült generálni az összefoglalót.")
                recommendations = parsed_response.get("recommendations", "Nem sikerült generálni a javaslatokat.")

                return summary, recommendations
                
            except json.JSONDecodeError as e:
                # Ha nem valid JSON, próbáljuk szétválasztani manuálisan
                logger.warning(f"AI válasz nem valid JSON ({e}), manuális feldolgozás...")
                logger.warning(f"Problémás JSON: {cleaned_response[:500]}...")
                return self._parse_ai_response_manually(ai_response)
                
        except Exception as e:
            logger.error(f"Hiba az AI összefoglaló generálása során: {str(e)}")
            error_summary = "Hiba történt az AI összefoglaló generálása során. Kérlek, ellenőrizd az OpenAI API kulcsot és próbáld újra."
            error_recommendations = "Az AI javaslatok nem elérhetők. Manuálisan ellenőrizd az eredményeket és készíts optimalizálási tervet."
            return error_summary, error_recommendations
    
    def _create_compact_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kompakt adatok kinyerése a token limit betartásához
        """
        try:
            # Alapvető URL és score adatok
            if isinstance(data, dict) and 'results' in data:
                results = data.get('results', [])
            elif isinstance(data, list):
                results = data
            else:
                results = [data] if isinstance(data, dict) else []
            
            # Biztonságos szűrés
            valid_results = []
            for r in results:
                if isinstance(r, dict) and 'url' in r:
                    valid_results.append(r)
            
            if not valid_results:
                return {"error": "Nincs elemzendő adat"}
            
            compact = {
                "summary": {
                    "urls_count": len(valid_results),
                    "urls": [r.get("url", "N/A")[:50] for r in valid_results[:3]]  # Max 3 URL, rövidítve
                },
                "scores": [],
                "key_issues": [],
                "platforms": {}
            }
            
            # Minden URL-hez kompakt adatok
            for result in valid_results[:2]:  # Max 2 URL a token limit miatt
                url = result.get("url", "Unknown")[:30]  # Rövidített URL
                
                url_data = {
                    "url": url,
                    "ai_score": result.get("ai_readiness_score", 0),
                    "meta_title_ok": bool(result.get("meta_and_headings", {}).get("title_optimal")),
                    "meta_desc_ok": bool(result.get("meta_and_headings", {}).get("description_optimal")),
                    "schema_count": sum(result.get("schema", {}).get("count", {}).values()) if isinstance(result.get("schema", {}).get("count"), dict) else result.get("schema", {}).get("count", 0),
                    "word_count": result.get("content_quality", {}).get("readability", {}).get("word_count", 0),
                    "mobile_ok": bool(result.get("mobile_friendly", {}).get("has_viewport")),
                }
                
                # Platform pontszámok
                platforms = result.get("platform_analysis", {})
                if platforms and not platforms.get("error"):
                    for platform in ["chatgpt", "claude", "gemini", "bing_chat"]:
                        if platform in platforms:
                            score = platforms[platform].get("compatibility_score", 0)
                            if platform not in compact["platforms"]:
                                compact["platforms"][platform] = []
                            compact["platforms"][platform].append(score)
                
                compact["scores"].append(url_data)
                
                # Kritikus problémák
                if url_data["ai_score"] < 50:
                    issues = []
                    if not url_data["meta_title_ok"]:
                        issues.append("title")
                    if not url_data["meta_desc_ok"]:
                        issues.append("description")
                    if url_data["schema_count"] == 0:
                        issues.append("schema")
                    if url_data["word_count"] < 300:
                        issues.append("content")
                    
                    compact["key_issues"].append({
                        "url": url,
                        "score": url_data["ai_score"],
                        "issues": issues[:3]  # Max 3 probléma
                    })
            
            # Platform átlagok
            for platform, scores in compact["platforms"].items():
                if scores:
                    compact["platforms"][platform] = round(sum(scores) / len(scores), 1)
            
            return compact
            
        except Exception as e:
            logger.error(f"Hiba a kompakt adatok kinyerése során: {str(e)}")
            return {"error": "Adatfeldolgozási hiba"}

    def _extract_structured_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Intelligens adatkinyerés és strukturálás - TELJES adathalmaz feldolgozása
        Prioritizálja és strukturálja az adatokat az AI számára
        """
        try:
            # Ha van results mező, azt használjuk, egyébként az egész data-t
            if isinstance(data, dict) and 'results' in data:
                results = data.get('results', [])
            elif isinstance(data, list):
                results = data
            else:
                results = [data] if isinstance(data, dict) else []
            
            # Szűrjük ki a hibás eredményeket - biztonságos ellenőrzés
            valid_results = []
            for r in results:
                if isinstance(r, dict) and 'error' not in r and 'url' in r:
                    valid_results.append(r)
            
            if not valid_results:
                # Ha nincs valid results, próbáljuk az eredeti data-t
                if isinstance(data, dict) and 'url' in data:
                    valid_results = [data]
                else:
                    return {"error": "Nincs érvényes elemzési eredmény"}
            
            # Strukturált adatok összeállítása
            structured_data = {
                "overview": {
                    "total_urls": len(valid_results),
                    "analysis_date": data.get("analysis_date", "N/A"),
                    "urls_analyzed": [r.get("url", "N/A") for r in valid_results]
                },
                "scores": {},
                "technical_seo": {},
                "content_quality": {},
                "ai_metrics": {},
                "platform_compatibility": {},
                "schema_analysis": {},
                "performance": {},
                "critical_issues": [],
                "quick_wins": [],
                "detailed_results": []
            }
            
            # Minden URL részletes feldolgozása
            for result in valid_results:
                url = result.get("url", "Unknown")
                
                # AI Readiness Score
                ai_score = result.get("ai_readiness_score", 0)
                
                # Részletes eredmény struktúra
                detailed = {
                    "url": url,
                    "ai_readiness_score": ai_score,
                    "ai_level": self._get_ai_level(ai_score)
                }
                
                # Meta adatok
                meta = result.get("meta_and_headings", {})
                detailed["meta"] = {
                    "title": {
                        "exists": bool(meta.get("title")),
                        "length": meta.get("title_length", 0),
                        "optimal": meta.get("title_optimal", False)
                    },
                    "description": {
                        "exists": bool(meta.get("description")),
                        "length": meta.get("description_length", 0),
                        "optimal": meta.get("description_optimal", False)
                    },
                    "headings": meta.get("headings", {}),
                    "h1_count": meta.get("h1_count", 0),
                    "heading_hierarchy_valid": meta.get("heading_hierarchy_valid", False),
                    "og_tags": meta.get("has_og_tags", False),
                    "twitter_card": meta.get("has_twitter_card", False)
                }
                
                # Schema elemzés
                schema = result.get("schema", {})
                detailed["schema"] = {
                    "count": sum(schema.get("count", {}).values()) if isinstance(schema.get("count"), dict) else schema.get("count", 0),
                    "types": list(schema.get("count", {}).keys()) if isinstance(schema.get("count"), dict) else [],
                    "has_breadcrumbs": schema.get("has_breadcrumbs", False),
                    "has_search_action": schema.get("has_search_action", False),
                    "validation_status": schema.get("validation_status", "standard"),
                    "google_validation": schema.get("google_validation", {}),
                    "completeness_score": schema.get("schema_completeness_score", 0),
                    "effectiveness": schema.get("effectiveness_analysis", {})
                }
                
                # AI metrikák
                ai_metrics = result.get("ai_metrics", {})
                ai_summary = result.get("ai_metrics_summary", {})
                detailed["ai_metrics"] = {
                    "weighted_average": ai_summary.get("weighted_average", 0),
                    "individual_scores": ai_summary.get("individual_scores", {}),
                    "level": ai_summary.get("level", "Unknown")
                }
                
                # Tartalom minőség
                content = result.get("content_quality", {})
                if content and not content.get("error"):
                    detailed["content"] = {
                        "overall_score": content.get("overall_quality_score", 0),
                        "word_count": content.get("readability", {}).get("word_count", 0),
                        "readability_score": content.get("readability", {}).get("readability_score", 0),
                        "vocabulary_richness": content.get("keyword_analysis", {}).get("vocabulary_richness", 0),
                        "depth_score": content.get("content_depth", {}).get("depth_score", 0),
                        "authority_score": content.get("authority_signals", {}).get("authority_score", 0),
                        "semantic_score": content.get("semantic_richness", {}).get("semantic_score", 0)
                    }
                
                # Platform kompatibilitás
                platforms = result.get("platform_analysis", {})
                if platforms and not platforms.get("error"):
                    platform_scores = {}
                    for platform_name, platform_data in platforms.items():
                        if platform_name != "summary" and isinstance(platform_data, dict):
                            platform_scores[platform_name] = {
                                "compatibility_score": platform_data.get("compatibility_score", 0),
                                "hybrid_score": platform_data.get("hybrid_score", 0),
                                "ai_score": platform_data.get("ai_score", 0),
                                "optimization_level": platform_data.get("optimization_level", "N/A"),
                                "ai_enhanced": platform_data.get("ai_enhanced", False)
                            }
                    detailed["platforms"] = platform_scores
                
                # AI Content Evaluation (Enhanced)
                ai_eval = result.get("ai_content_evaluation", {})
                if ai_eval and not ai_eval.get("error"):
                    detailed["ai_evaluation"] = {
                        "overall_score": ai_eval.get("overall_ai_score", 0),
                        "platform_scores": ai_eval.get("ai_quality_scores", {}),
                        "has_evaluation": True
                    }
                
                # PageSpeed
                psi = result.get("pagespeed_insights", {})
                if psi:
                    detailed["performance"] = {
                        "mobile": psi.get("mobile", {}),
                        "desktop": psi.get("desktop", {})
                    }
                
                # Technikai SEO
                detailed["technical"] = {
                    "robots_allowed": result.get("robots_txt", {}).get("can_fetch", False),
                    "sitemap_exists": result.get("sitemap", {}).get("exists", False),
                    "mobile_viewport": result.get("mobile_friendly", {}).get("has_viewport", False),
                    "responsive_images": result.get("mobile_friendly", {}).get("responsive_images", False),
                    "html_size_kb": result.get("html_size_kb", 0)
                }
                
                # Kritikus problémák azonosítása
                if ai_score < 40:
                    structured_data["critical_issues"].append({
                        "url": url,
                        "score": ai_score,
                        "main_issues": self._identify_main_issues(detailed)
                    })
                
                # Quick wins azonosítása
                quick_wins = self._identify_quick_wins(detailed)
                if quick_wins:
                    structured_data["quick_wins"].extend(quick_wins)
                
                # Részletes eredmény hozzáadása
                structured_data["detailed_results"].append(detailed)
            
            # Összesített statisztikák számítása
            if valid_results:
                all_scores = [r.get("ai_readiness_score", 0) for r in valid_results]
                structured_data["scores"] = {
                    "average_ai_readiness": sum(all_scores) / len(all_scores),
                    "min_score": min(all_scores),
                    "max_score": max(all_scores),
                    "excellent_count": len([s for s in all_scores if s >= 85]),
                    "good_count": len([s for s in all_scores if 60 <= s < 85]),
                    "average_count": len([s for s in all_scores if 40 <= s < 60]),
                    "poor_count": len([s for s in all_scores if s < 40])
                }
                
                # Platform átlagok
                platform_averages = {}
                platform_names = ["chatgpt", "claude", "gemini", "bing_chat"]
                for platform in platform_names:
                    scores = []
                    for r in structured_data["detailed_results"]:
                        if "platforms" in r and platform in r["platforms"]:
                            scores.append(r["platforms"][platform]["compatibility_score"])
                    if scores:
                        platform_averages[platform] = sum(scores) / len(scores)
                
                structured_data["platform_compatibility"] = platform_averages
            
            return structured_data
            
        except Exception as e:
            logger.error(f"Hiba a strukturált adatok kinyerése során: {str(e)}")
            # Fallback: eredeti adat visszaadása
            return data
    
    def _get_ai_level(self, score: float) -> str:
        """AI readiness szint meghatározása"""
        if score >= 85:
            return "Kiváló"
        elif score >= 60:
            return "Jó"
        elif score >= 40:
            return "Közepes"
        else:
            return "Fejlesztendő"
    
    def _identify_main_issues(self, detailed: Dict) -> List[str]:
        """Fő problémák azonosítása"""
        issues = []
        
        # Meta problémák
        if not detailed.get("meta", {}).get("title", {}).get("optimal"):
            issues.append("Title tag nem optimális")
        if not detailed.get("meta", {}).get("description", {}).get("optimal"):
            issues.append("Meta description hiányzik vagy nem optimális")
        
        # Schema problémák
        if detailed.get("schema", {}).get("count", 0) == 0:
            issues.append("Nincs Schema.org markup")
        
        # Tartalom problémák
        if detailed.get("content", {}).get("word_count", 0) < 300:
            issues.append("Kevés tartalom")
        
        # Technikai problémák
        if not detailed.get("technical", {}).get("mobile_viewport"):
            issues.append("Nincs mobile viewport")
        
        return issues[:5]  # Max 5 fő probléma
    
    def _identify_quick_wins(self, detailed: Dict) -> List[Dict]:
        """Gyors nyerések azonosítása"""
        quick_wins = []
        url = detailed.get("url", "")
        
        # Title optimalizálás
        title_data = detailed.get("meta", {}).get("title", {})
        if title_data.get("exists") and not title_data.get("optimal"):
            if title_data.get("length", 0) < 30 or title_data.get("length", 0) > 60:
                quick_wins.append({
                    "url": url,
                    "type": "Title optimalizálás",
                    "current": f"{title_data.get('length', 0)} karakter",
                    "target": "30-60 karakter",
                    "impact": "Magas",
                    "effort": "Alacsony"
                })
        
        # Meta description
        desc_data = detailed.get("meta", {}).get("description", {})
        if not desc_data.get("exists") or desc_data.get("length", 0) < 120:
            quick_wins.append({
                "url": url,
                "type": "Meta description hozzáadása",
                "current": f"{desc_data.get('length', 0)} karakter",
                "target": "120-160 karakter",
                "impact": "Közepes",
                "effort": "Alacsony"
            })
        
        # Schema.org
        if detailed.get("schema", {}).get("count", 0) == 0:
            quick_wins.append({
                "url": url,
                "type": "Schema.org markup hozzáadása",
                "current": "0 schema elem",
                "target": "Minimum FAQ vagy Article schema",
                "impact": "Magas",
                "effort": "Közepes"
            })
        
        return quick_wins
    
    def _parse_ai_response_manually(self, response: str) -> Tuple[str, str]:
        """
        Manuális feldolgozás, ha az AI válasz nem valid JSON
        """
        try:
            import re
            
            logger.info(f"Manuális parsing indítása, válasz hossza: {len(response)} karakter")
            logger.info(f"Válasz első 300 karakter: {response[:300]}...")
            
            # Tisztítás - JSON és markdown elemek eltávolítása
            cleaned = response
            cleaned = re.sub(r'```json|```', '', cleaned)
            cleaned = re.sub(r'^json\s*', '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'[{}"]', '', cleaned)  # JSON karakterek eltávolítása
            
            # Különböző pattern-ek próbálása
            patterns = [
                # JSON-szerű szerkezet
                (r'summary[:\s]+(.*?)(?:recommendations|javaslat)', r'recommendations[:\s]+(.*)'),
                # Számozott lista
                (r'1\.\s*(?:összefoglaló|summary)[:\s]*(.*?)(?:2\.|recommendations|javaslat)', 
                 r'2\.\s*(?:javaslatok|recommendations)[:\s]*(.*)'),
                # Nagybetűs címek
                (r'ÖSSZEFOGLALÓ[:\s]*(.*?)(?:JAVASLATOK|RECOMMENDATIONS)', 
                 r'(?:JAVASLATOK|RECOMMENDATIONS)[:\s]*(.*)'),
                # Természetes szöveg
                (r'(?:összefoglaló|summary)[:\s]*(.*?)(?:javaslatok|recommendations|ajánlások)', 
                 r'(?:javaslatok|recommendations|ajánlások)[:\s]*(.*)'),
            ]
            
            summary = None
            recommendations = None
            
            # Próbáljuk meg az összes pattern-t
            for sum_pattern, rec_pattern in patterns:
                if not summary:
                    sum_match = re.search(sum_pattern, cleaned, re.IGNORECASE | re.DOTALL)
                    if sum_match:
                        summary = sum_match.group(1).strip()
                        logger.info(f"Summary pattern találat, hossz: {len(summary)}")
                
                if not recommendations:
                    rec_match = re.search(rec_pattern, cleaned, re.IGNORECASE | re.DOTALL)
                    if rec_match:
                        recommendations = rec_match.group(1).strip()
                        logger.info(f"Recommendations pattern találat, hossz: {len(recommendations)}")
                
                if summary and recommendations:
                    break
            
            # Ha még mindig nincs eredmény, válasz felezése
            if not summary or not recommendations:
                logger.info("Pattern matching sikertelen, válasz felezése...")
                
                # Keresünk természetes töréspontokat
                break_words = ['javaslatok', 'recommendations', 'ajánlások', '2.', 'következtetések']
                break_point = len(cleaned) // 2
                
                for word in break_words:
                    pos = cleaned.lower().find(word.lower())
                    if pos > 100:  # Minimum 100 karakter legyen az első részben
                        break_point = pos
                        break
                
                if not summary:
                    summary = cleaned[:break_point].strip()
                if not recommendations:
                    recommendations = cleaned[break_point:].strip()
            
            # További tisztítás
            if summary:
                summary = re.sub(r'\s+', ' ', summary)  # Többszörös szóközök
                summary = re.sub(r'^[:\-\s]*', '', summary)  # Kezdő karakterek
                
            if recommendations:
                recommendations = re.sub(r'\s+', ' ', recommendations)  # Többszörös szóközök
                recommendations = re.sub(r'^[:\-\s]*', '', recommendations)  # Kezdő karakterek
                # Javaslatok szó eltávolítása az elejéről
                recommendations = re.sub(r'^(?:javaslatok|recommendations|ajánlások)[:\s]*', '', recommendations, flags=re.IGNORECASE)
            
            # Végső ellenőrzés
            if not summary or len(summary) < 50:
                logger.warning("Summary túl rövid vagy üres, eredeti válasz használata")
                summary = response[:800] if len(response) > 800 else response
                
            if not recommendations or len(recommendations) < 50:
                logger.warning("Recommendations túl rövid vagy üres, alapértelmezett üzenet")
                recommendations = "A javaslatok automatikus generálása sikertelen. Kérlek tekintsd át manuálisan az elemzési eredményeket."
            
            logger.info(f"Manuális parsing befejezve - Summary: {len(summary)} kar, Recommendations: {len(recommendations)} kar")
            
            return (
                summary.strip() or "Az összefoglaló generálása részben sikertelen.",
                recommendations.strip() or "A javaslatok generálása részben sikertelen."
            )
            
        except Exception as e:
            logger.error(f"Hiba a manuális feldolgozás során: {str(e)}")
            # Végső fallback
            return (
                response[:800] if len(response) > 800 else response,
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
    test_data = {
        "results": [
            {
                "url": "https://example.com",
                "ai_readiness_score": 75.5,
                "meta_and_headings": {
                    "title": "Test Title",
                    "title_length": 11,
                    "title_optimal": False,
                    "description": "Test Description",
                    "description_length": 16,
                    "description_optimal": False,
                    "h1_count": 1,
                    "heading_hierarchy_valid": True,
                    "has_og_tags": True,
                    "has_twitter_card": False
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
                }
            }
        ]
    }
    
    try:
        generator = AISummaryGenerator()
        summary, recommendations = generator.generate_summary_and_recommendations(test_data)
        print("Összefoglaló:", summary)
        print("\nJavaslatok:", recommendations)
    except Exception as e:
        print(f"Teszt hiba: {str(e)}")