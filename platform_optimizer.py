import re
import json
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod


class AIPlattformOptimizer(ABC):
    """Absztrakt osztály AI platform optimalizáláshoz"""
    
    @abstractmethod
    def analyze_compatibility(self, soup: BeautifulSoup, text: str) -> Dict:
        pass
    
    @abstractmethod
    def get_optimization_suggestions(self, analysis: Dict) -> List[Dict]:
        pass


class ChatGPTOptimizer(AIPlattformOptimizer):
    """ChatGPT/OpenAI specifikus optimalizálás"""
    
    def __init__(self):
        self.preferred_formats = [
            'FAQ', 'HowTo', 'listicle', 'step-by-step', 'comparison'
        ]
        
        # ChatGPT kedveli ezeket
        self.positive_signals = [
            'steps', 'lépések', 'process', 'folyamat', 'guide', 'útmutató',
            'tips', 'tippek', 'best practices', 'legjobb gyakorlatok',
            'example', 'példa', 'tutorial', 'oktatóanyag'
        ]
    
    def analyze_compatibility(self, soup: BeautifulSoup, text: str) -> Dict:
        """ChatGPT kompatibilitás elemzése"""
        
        # Step-by-step tartalom detektálása
        step_patterns = [
            r'\b(?:lépés|step)\s*\d+',
            r'\b\d+\.\s*[A-ZÁÉÍÓÖŐÚÜŰ]',
            r'\bFirst|Second|Third|Finally\b',
            r'\bElőször|Másodszor|Harmadszor|Végül\b'
        ]
        
        step_indicators = sum(len(re.findall(pattern, text, re.I)) for pattern in step_patterns)
        
        # Ordered lists (számozott listák)
        ordered_lists = len(soup.find_all('ol'))
        list_items = len(soup.find_all('li'))
        
        # Q&A formátum
        questions = text.count('?')
        
        # Gyakorlati tartalom
        practical_keywords = sum(text.lower().count(keyword) for keyword in self.positive_signals)
        
        # Kód példák (ha tech tartalom)
        code_blocks = len(soup.find_all(['pre', 'code']))
        
        # Táblázatok (strukturált adatok)
        tables = len(soup.find_all('table'))
        
        compatibility_score = self._calculate_chatgpt_score(
            step_indicators, ordered_lists, list_items, questions, 
            practical_keywords, code_blocks, tables
        )
        
        return {
            "platform": "ChatGPT",
            "step_by_step_content": step_indicators,
            "structured_lists": {"ordered": ordered_lists, "items": list_items},
            "qa_elements": questions,
            "practical_content": practical_keywords,
            "code_examples": code_blocks,
            "structured_data": tables,
            "compatibility_score": compatibility_score,
            "optimization_level": self._get_optimization_level(compatibility_score)
        }
    
    def get_optimization_suggestions(self, analysis: Dict) -> List[Dict]:
        """ChatGPT optimalizálási javaslatok"""
        suggestions = []
        
        if analysis.get("step_by_step_content", 0) < 3:
            suggestions.append({
                "type": "structure",
                "priority": "high",
                "suggestion": "Adj hozzá step-by-step útmutatókat",
                "description": "ChatGPT szereti a számozott lépéseket és folyamatokat",
                "implementation": "Használj <ol> listákat és világos lépés számozást"
            })
        
        if analysis.get("structured_lists", {}).get("ordered", 0) == 0:
            suggestions.append({
                "type": "formatting",
                "priority": "medium",
                "suggestion": "Használj számozott listákat",
                "description": "Strukturált listák javítják a ChatGPT megértését",
                "implementation": "<ol><li>Első pont</li><li>Második pont</li></ol>"
            })
        
        if analysis.get("qa_elements", 0) < 5:
            suggestions.append({
                "type": "content",
                "priority": "medium",
                "suggestion": "Adj hozzá Q&A szekciót",
                "description": "Kérdés-válasz formátum ideális ChatGPT-hez",
                "implementation": "FAQ szekció vagy gyakori kérdések blokk"
            })
        
        if analysis.get("code_examples", 0) == 0 and "tech" in analysis.get("content_type", ""):
            suggestions.append({
                "type": "enhancement",
                "priority": "low",
                "suggestion": "Adj hozzá kód példákat",
                "description": "Technikai tartalomhoz hasznos a kód illusztrálás",
                "implementation": "<pre><code> blokkok használata"
            })
        
        return suggestions
    
    def _calculate_chatgpt_score(self, steps: int, ordered: int, items: int, 
                               questions: int, practical: int, code: int, tables: int) -> int:
        """ChatGPT kompatibilitás pontszám"""
        score = 0
        
        # Step-by-step tartalom (legfontosabb)
        score += min(30, steps * 8)
        
        # Strukturált listák
        score += min(25, ordered * 15 + items * 2)
        
        # Q&A elemek
        score += min(20, questions * 3)
        
        # Gyakorlati tartalom
        score += min(15, practical * 2)
        
        # Strukturált adatok
        score += min(10, code * 5 + tables * 8)
        
        return min(100, score)
    
    def _get_optimization_level(self, score: int) -> str:
        """Optimalizálási szint"""
        if score >= 80:
            return "Kiváló"
        elif score >= 60:
            return "Jó"
        elif score >= 40:
            return "Közepes"
        else:
            return "Fejlesztendő"


class ClaudeOptimizer(AIPlattformOptimizer):
    """Claude (Anthropic) specifikus optimalizálás"""
    
    def __init__(self):
        # Claude kedveli a részletes, kontextusba helyezett információkat
        self.context_indicators = [
            'background', 'háttér', 'context', 'kontextus', 'overview', 'áttekintés',
            'analysis', 'elemzés', 'detailed', 'részletes', 'comprehensive', 'átfogó'
        ]
        
        self.nuanced_language = [
            'however', 'azonban', 'although', 'bár', 'nevertheless', 'mindazonáltal',
            'on the other hand', 'másrészt', 'furthermore', 'továbbá'
        ]
    
    def analyze_compatibility(self, soup: BeautifulSoup, text: str) -> Dict:
        """Claude kompatibilitás elemzése"""
        
        # Hosszú forma tartalom (Claude kedveli)
        word_count = len(text.split())
        
        # Kontextuális információk
        context_keywords = sum(text.lower().count(keyword) for keyword in self.context_indicators)
        
        # Árnyalt nyelv használata
        nuanced_expressions = sum(text.lower().count(expr) for expr in self.nuanced_language)
        
        # Részletes magyarázatok (hosszú bekezdések)
        paragraphs = [p for p in text.split('\n') if p.strip()]
        long_paragraphs = sum(1 for p in paragraphs if len(p.split()) > 100)
        
        # Hivatkozások és források (Claude értékeli a megalapozott információt)
        citations = len(soup.find_all(['cite', 'blockquote']))
        external_links = len(soup.find_all('a', href=re.compile(r'^https?://')))
        
        # Szakmai mélység
        technical_terms = len(re.findall(r'\b[A-ZÁÉÍÓÖŐÚÜŰ][a-záéíóöőúüű]*(?:ás|és|ség|ság|izmus|ció)\b', text))
        
        compatibility_score = self._calculate_claude_score(
            word_count, context_keywords, nuanced_expressions, 
            long_paragraphs, citations, external_links, technical_terms
        )
        
        return {
            "platform": "Claude",
            "content_length": word_count,
            "contextual_information": context_keywords,
            "nuanced_language": nuanced_expressions,
            "detailed_explanations": long_paragraphs,
            "citations_sources": citations + external_links,
            "technical_depth": technical_terms,
            "compatibility_score": compatibility_score,
            "optimization_level": self._get_optimization_level(compatibility_score)
        }
    
    def get_optimization_suggestions(self, analysis: Dict) -> List[Dict]:
        """Claude optimalizálási javaslatok"""
        suggestions = []
        
        if analysis.get("content_length", 0) < 800:
            suggestions.append({
                "type": "content",
                "priority": "high",
                "suggestion": "Bővítsd a tartalmat részletesebb információkkal",
                "description": "Claude jobban teljesít hosszabb, átfogó tartalmakkal",
                "implementation": "Adj hozzá kontextust, háttér információkat és példákat"
            })
        
        if analysis.get("contextual_information", 0) < 3:
            suggestions.append({
                "type": "content",
                "priority": "high",
                "suggestion": "Adj hozzá kontextuális információkat",
                "description": "Claude értékeli a háttér és overview szekciók",
                "implementation": "Kezdd kontextussal, adj áttekintést a témáról"
            })
        
        if analysis.get("citations_sources", 0) < 3:
            suggestions.append({
                "type": "credibility",
                "priority": "medium",
                "suggestion": "Adj hozzá hivatkozásokat és forrásokat",
                "description": "Claude preferálja a megalapozott, forrásokkal támogatott tartalmat",
                "implementation": "Használj <cite> tageket és külső linkeket"
            })
        
        if analysis.get("nuanced_language", 0) < 2:
            suggestions.append({
                "type": "style",
                "priority": "low",
                "suggestion": "Használj árnyaltabb nyelvezetet",
                "description": "Claude jobban megérti a komplex, árnyalt megfogalmazásokat",
                "implementation": "Használj azonban, másrészt, továbbá típusú kötőszavakat"
            })
        
        return suggestions
    
    def _calculate_claude_score(self, words: int, context: int, nuanced: int,
                              long_paras: int, citations: int, external: int, technical: int) -> int:
        """Claude kompatibilitás pontszám"""
        score = 0
        
        # Tartalom hossz
        if words >= 1500:
            score += 25
        elif words >= 800:
            score += 15
        elif words >= 500:
            score += 10
        
        # Kontextuális információk
        score += min(20, context * 5)
        
        # Árnyalt nyelv
        score += min(15, nuanced * 8)
        
        # Részletes magyarázatok
        score += min(15, long_paras * 5)
        
        # Források és hivatkozások
        score += min(15, citations * 8 + external * 2)
        
        # Szakmai mélység
        score += min(10, technical * 1)
        
        return min(100, score)
    
    def _get_optimization_level(self, score: int) -> str:
        """Optimalizálási szint"""
        if score >= 80:
            return "Kiváló"
        elif score >= 60:
            return "Jó"
        elif score >= 40:
            return "Közepes"
        else:
            return "Fejlesztendő"


class GeminiOptimizer(AIPlattformOptimizer):
    """Google Gemini specifikus optimalizálás"""
    
    def __init__(self):
        # Gemini kedveli a multimodális tartalmat és a friss adatokat
        self.fresh_content_indicators = [
            '2024', '2025', 'latest', 'recent', 'current', 'new', 'updated',
            'legfrissebb', 'aktuális', 'új', 'frissített', 'mostani'
        ]
        
        self.structured_data_types = [
            'FAQPage', 'HowTo', 'Article', 'NewsArticle', 'Product', 'Review'
        ]
    
    def analyze_compatibility(self, soup: BeautifulSoup, text: str) -> Dict:
        """Gemini kompatibilitás elemzése"""
        
        # Multimédia tartalom
        images = len(soup.find_all('img'))
        videos = len(soup.find_all(['video', 'iframe']))
        
        # Friss tartalom indikátorok
        freshness_indicators = sum(text.lower().count(indicator) for indicator in self.fresh_content_indicators)
        
        # Strukturált adatok (Schema.org)
        structured_data_score = 0
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                # JAVÍTÁS: Tisztítsuk meg a JSON stringet
                script_content = script.string
                if not script_content:
                    continue
                    
                # Whitespace tisztítás
                script_content = script_content.strip()
                
                # JSON parse
                data = json.loads(script_content)
                
                # JAVÍTÁS: Biztonságos dictionary kezelés
                if isinstance(data, dict):
                    schema_type = data.get("@type")  # .get() használata
                    if schema_type and schema_type in self.structured_data_types:
                        structured_data_score += 10
                elif isinstance(data, list):
                    # Ha lista, akkor végigmegyünk az elemeken
                    for item in data:
                        if isinstance(item, dict):
                            schema_type = item.get("@type")
                            if schema_type and schema_type in self.structured_data_types:
                                structured_data_score += 10
                                
            except (json.JSONDecodeError, KeyError, TypeError, AttributeError) as e:
                # Minden lehetséges hibát elkapunk
                continue
        
        # Google szolgáltatásokra vonatkozó optimalizálás
        google_features = len(soup.find_all(attrs={'itemscope': True})) + \
                        len(soup.find_all(attrs={'itemtype': True})) + \
                        len(soup.find_all('meta', property=re.compile(r'^og:')))
        
        # Lokalizáció (Gemini jobban támogatja a helyi tartalmat)
        local_indicators = len(re.findall(r'\b(?:Budapest|Magyarország|Hungary|magyar)\b', text, re.I))
        
        # Adatok és tények (Gemini kedveli a faktikus tartalmat)
        data_points = len(re.findall(r'\b\d+(?:[.,]\d+)?%?\s*(?:százalék|percent|adat|data|statisztika)\b', text.lower()))
        
        compatibility_score = self._calculate_gemini_score(
            images, videos, freshness_indicators, structured_data_score,
            google_features, local_indicators, data_points
        )
        
        return {
            "platform": "Gemini",
            "multimedia_content": {"images": images, "videos": videos},
            "content_freshness": freshness_indicators,
            "structured_data": structured_data_score,
            "google_optimization": google_features,
            "localization": local_indicators,
            "factual_content": data_points,
            "compatibility_score": compatibility_score,
            "optimization_level": self._get_optimization_level(compatibility_score)
        }
    
    def get_optimization_suggestions(self, analysis: Dict) -> List[Dict]:
        """Gemini optimalizálási javaslatok"""
        suggestions = []
        
        multimedia = analysis.get("multimedia_content", {})
        if multimedia.get("images", 0) < 3:
            suggestions.append({
                "type": "multimedia",
                "priority": "high",
                "suggestion": "Adj hozzá több képet és vizuális elemet",
                "description": "Gemini kiválóan támogatja a multimodális tartalmat",
                "implementation": "Releváns képek alt texttel és leírásokkal"
            })
        
        if analysis.get("structured_data", 0) < 20:
            suggestions.append({
                "type": "schema",
                "priority": "high",
                "suggestion": "Bővítsd a Schema.org markup-ot",
                "description": "Gemini erősen támaszkodik a strukturált adatokra",
                "implementation": "FAQ, HowTo, Article schema hozzáadása"
            })
        
        if analysis.get("content_freshness", 0) < 5:
            suggestions.append({
                "type": "freshness",
                "priority": "medium",
                "suggestion": "Hangsúlyozd a tartalom frissességét",
                "description": "Gemini preferálja az aktuális, friss információkat",
                "implementation": "Dátumok, 'frissített', 'aktuális' kifejezések használata"
            })
        
        if analysis.get("factual_content", 0) < 3:
            suggestions.append({
                "type": "content",
                "priority": "medium",
                "suggestion": "Adj hozzá több adatot és statisztikát",
                "description": "Gemini kedveli a faktikus, számszerű információkat",
                "implementation": "Konkrét számok, százalékok, kutatási eredmények"
            })
        
        return suggestions
    
    def _calculate_gemini_score(self, images: int, videos: int, freshness: int,
                              schema: int, google_feat: int, local: int, data: int) -> int:
        """Gemini kompatibilitás pontszám"""
        score = 0
        
        # Multimédia (legfontosabb Gemini-hez)
        score += min(30, images * 5 + videos * 10)
        
        # Strukturált adatok
        score += min(25, schema)
        
        # Frissesség
        score += min(15, freshness * 3)
        
        # Google optimalizálás
        score += min(15, google_feat * 2)
        
        # Faktikus tartalom
        score += min(10, data * 3)
        
        # Lokalizáció
        score += min(5, local * 2)
        
        return min(100, score)
    
    def _get_optimization_level(self, score: int) -> str:
        """Optimalizálási szint"""
        if score >= 80:
            return "Kiváló"
        elif score >= 60:
            return "Jó"
        elif score >= 40:
            return "Közepes"
        else:
            return "Fejlesztendő"


class BingChatOptimizer(AIPlattformOptimizer):
    """Microsoft Bing Chat specifikus optimalizálás"""
    
    def __init__(self):
        # Bing Chat kedveli a hivatkozásokat és a webes integrációt
        self.web_integration_signals = [
            'source', 'forrás', 'reference', 'hivatkozás', 'link', 'website',
            'according to', 'szerint', 'based on', 'alapján'
        ]
    
    def analyze_compatibility(self, soup: BeautifulSoup, text: str) -> Dict:
        """Bing Chat kompatibilitás elemzése"""
        
        # Külső hivatkozások (Bing Chat kedveli)
        external_links = len(soup.find_all('a', href=re.compile(r'^https?://')))
        
        # Hivatkozási szignálok a szövegben
        citation_signals = sum(text.lower().count(signal) for signal in self.web_integration_signals)
        
        # Microsoft ökoszisztéma integráció
        ms_integration = len(soup.find_all(['meta[name*="msapplication"]', '[data-ms]']))
        
        # Keresés-orientált tartalom
        search_oriented = text.lower().count('search') + text.lower().count('keres')
        
        # Időszerű információk (Bing erős a real-time adatokban)
        time_sensitive = len(re.findall(r'\b(?:today|yesterday|tomorrow|ma|tegnap|holnap|this week|ezen a héten)\b', text.lower()))
        
        compatibility_score = self._calculate_bing_score(
            external_links, citation_signals, ms_integration,
            search_oriented, time_sensitive
        )
        
        return {
            "platform": "Bing Chat",
            "external_references": external_links,
            "citation_signals": citation_signals,
            "microsoft_integration": ms_integration,
            "search_optimization": search_oriented,
            "time_sensitive_content": time_sensitive,
            "compatibility_score": compatibility_score,
            "optimization_level": self._get_optimization_level(compatibility_score)
        }
    
    def get_optimization_suggestions(self, analysis: Dict) -> List[Dict]:
        """Bing Chat optimalizálási javaslatok"""
        suggestions = []
        
        if analysis.get("external_references", 0) < 5:
            suggestions.append({
                "type": "references",
                "priority": "high",
                "suggestion": "Adj hozzá több külső hivatkozást",
                "description": "Bing Chat erősen támaszkodik a webes forrásokra",
                "implementation": "Releváns, megbízható külső oldalakra linkek"
            })
        
        if analysis.get("citation_signals", 0) < 3:
            suggestions.append({
                "type": "style",
                "priority": "medium",
                "suggestion": "Használj hivatkozási kifejezéseket",
                "description": "Bing Chat kedveli a 'according to', 'based on' típusú kifejezéseket",
                "implementation": "'Forrás szerint', 'alapján' kifejezések használata"
            })
        
        return suggestions
    
    def _calculate_bing_score(self, links: int, citations: int, ms_int: int,
                            search: int, time_sens: int) -> int:
        """Bing Chat kompatibilitás pontszám"""
        score = 0
        
        # Külső hivatkozások (legfontosabb)
        score += min(40, links * 6)
        
        # Hivatkozási szignálok
        score += min(25, citations * 8)
        
        # Keresés orientáltság
        score += min(15, search * 5)
        
        # Időszerűség
        score += min(15, time_sens * 4)
        
        # Microsoft integráció
        score += min(5, ms_int * 5)
        
        return min(100, score)
    
    def _get_optimization_level(self, score: int) -> str:
        """Optimalizálási szint"""
        if score >= 80:
            return "Kiváló"
        elif score >= 60:
            return "Jó"
        elif score >= 40:
            return "Közepes"
        else:
            return "Fejlesztendő"


class MultiPlatformGEOAnalyzer:
    """Multi-platform GEO elemző főosztály - AI-enhanced verzió"""
    
    def __init__(self, ai_evaluator=None, cache_manager=None):
        self.platforms = {
            'chatgpt': ChatGPTOptimizer(),
            'claude': ClaudeOptimizer(),
            'gemini': GeminiOptimizer(),
            'bing_chat': BingChatOptimizer()
        }
        self.ai_evaluator = ai_evaluator
        self.cache_manager = cache_manager
        self.ml_scorer = MLPlatformScorer() if self._ml_available() else None
    
    def analyze_all_platforms(self, html: str, url: str) -> Dict:
        """Összes platform elemzése AI-enhanced módon"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Tiszta szöveg kinyerése
        text_content = self._extract_clean_text(soup)
        
        results = {}
        
        # Hagyományos platform elemzés
        for platform_name, optimizer in self.platforms.items():
            try:
                traditional_result = optimizer.analyze_compatibility(soup, text_content)
                
                # AI-enhanced scoring ha elérhető
                if self.ai_evaluator:
                    ai_platform_score = self.ai_evaluator.platform_specific_evaluation(text_content, platform_name)
                    # Hibrid scoring: hagyományos + AI
                    enhanced_score = self._combine_scores(traditional_result, ai_platform_score)
                    traditional_result.update(enhanced_score)
                
                # ML scoring ha elérhető
                if self.ml_scorer:
                    ml_score = self.ml_scorer.predict_platform_score(
                        platform_name, text_content, self._extract_metadata(soup)
                    )
                    traditional_result["ml_score"] = ml_score
                    traditional_result["hybrid_score"] = (traditional_result["compatibility_score"] + ml_score) / 2
                
                results[platform_name] = traditional_result
                
            except Exception as e:
                results[platform_name] = {
                    "platform": platform_name,
                    "error": str(e),
                    "compatibility_score": 0
                }
        
        # AI-alapú összesített elemzés
        if self.ai_evaluator:
            ai_summary = self.ai_evaluator.evaluate_content_quality(
                text_content, list(self.platforms.keys())
            )
            results['ai_analysis'] = ai_summary
        
        # Összesített elemzés
        results['summary'] = self._create_enhanced_platform_summary(results)
        
        return results
    
    def get_all_suggestions(self, platform_analyses: Dict) -> Dict:
        """Összes platform optimalizálási javaslatok"""
        all_suggestions = {}
        
        for platform_name, optimizer in self.platforms.items():
            if platform_name in platform_analyses and 'error' not in platform_analyses[platform_name]:
                try:
                    all_suggestions[platform_name] = optimizer.get_optimization_suggestions(
                        platform_analyses[platform_name]
                    )
                except Exception as e:
                    all_suggestions[platform_name] = [{"error": str(e)}]
        
        # Közös javaslatok azonosítása
        all_suggestions['common_optimizations'] = self._find_common_suggestions(all_suggestions)
        
        return all_suggestions
    
    def _extract_clean_text(self, soup: BeautifulSoup) -> str:
        """Tiszta szöveg kinyerése"""
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
        
        text = soup.get_text()
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _create_platform_summary(self, results: Dict) -> Dict:
        """Platform összefoglaló létrehozása"""
        scores = {}
        levels = {}
        
        for platform, data in results.items():
            if platform != 'summary' and 'error' not in data:
                scores[platform] = data.get('compatibility_score', 0)
                levels[platform] = data.get('optimization_level', 'Ismeretlen')
        
        if not scores:
            return {"error": "Nincs érvényes platform adat"}
        
        avg_score = sum(scores.values()) / len(scores)
        best_platform = max(scores, key=scores.get)
        worst_platform = min(scores, key=scores.get)
        
        return {
            "average_compatibility": round(avg_score, 1),
            "best_platform": {"name": best_platform, "score": scores[best_platform]},
            "worst_platform": {"name": worst_platform, "score": scores[worst_platform]},
            "platform_scores": scores,
            "optimization_levels": levels,
            "overall_level": self._get_overall_level(avg_score)
        }
    
    def _find_common_suggestions(self, all_suggestions: Dict) -> List[Dict]:
        """Közös optimalizálási javaslatok keresése"""
        common = []
        
        # Típus alapú csoportosítás
        type_suggestions = {}
        
        for platform, suggestions in all_suggestions.items():
            if platform == 'common_optimizations':
                continue
                
            for suggestion in suggestions:
                if isinstance(suggestion, dict) and 'type' in suggestion:
                    suggestion_type = suggestion['type']
                    if suggestion_type not in type_suggestions:
                        type_suggestions[suggestion_type] = []
                    type_suggestions[suggestion_type].append(suggestion)
        
        # Legalább 2 platformon megjelenő javaslatok
        for suggestion_type, suggestions in type_suggestions.items():
            if len(suggestions) >= 2:
                # Első javaslat mint reprezentáció
                common_suggestion = suggestions[0].copy()
                common_suggestion['platforms'] = len(suggestions)
                common_suggestion['priority'] = 'high' if len(suggestions) >= 3 else 'medium'
                common.append(common_suggestion)
        
        return common
    
    def _get_overall_level(self, avg_score: float) -> str:
        """Összesített optimalizálási szint"""
        if avg_score >= 80:
            return "Kiváló"
        elif avg_score >= 60:
            return "Jó"
        elif avg_score >= 40:
            return "Közepes"
        else:
            return "Fejlesztendő"
    
    def get_platform_priorities(self, platform_analyses: Dict) -> List[Dict]:
        """Platform prioritások meghatározása a pontszámok alapján"""
        if 'summary' not in platform_analyses:
            return []
        
        scores = platform_analyses['summary'].get('platform_scores', {})
        
        # Prioritás lista létrehozása
        priorities = []
        for platform, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            if score >= 70:
                priority = "Már optimalizált"
            elif score >= 50:
                priority = "Közepes prioritás"
            else:
                priority = "Magas prioritás"
            
            priorities.append({
                "platform": platform,
                "score": score,
                "priority": priority,
                "action": self._get_action_recommendation(score)
            })
        
        return priorities
    
    def _get_action_recommendation(self, score: int) -> str:
        """Cselekvési javaslat a pontszám alapján"""
        if score >= 80:
            return "Fenntartás és finomhangolás"
        elif score >= 60:
            return "Kisebb optimalizálások"
        elif score >= 40:
            return "Jelentős fejlesztések szükségesek"
        else:
            return "Teljes újragondolás javasolt"
    
    def _ml_available(self) -> bool:
        """ML modellek elérhetőségének ellenőrzése"""
        try:
            import pandas as pd
            return True
        except ImportError:
            return False
    
    def _combine_scores(self, traditional: Dict, ai_result: Dict) -> Dict:
        """Hagyományos és AI pontszámok kombinálása"""
        if not ai_result or ai_result.get('error'):
            return {"ai_enhanced": False}
        
        ai_score = ai_result.get('platform_score', 0)
        traditional_score = traditional.get('compatibility_score', 0)
        
        # Súlyozott átlag: 60% hagyományos, 40% AI
        hybrid_score = (traditional_score * 0.6) + (ai_score * 0.4)
        
        return {
            "ai_enhanced": True,
            "ai_score": ai_score,
            "hybrid_compatibility_score": round(hybrid_score, 1),
            "ai_suggestions": ai_result.get('optimization_suggestions', [])
        }
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """Metadata kinyerése ML modell számára"""
        return {
            "external_links": len(soup.find_all('a', href=re.compile(r'^https?://'))),
            "schema_count": len(soup.find_all("script", type="application/ld+json")),
            "image_count": len(soup.find_all('img')),
            "list_count": len(soup.find_all(['ul', 'ol'])),
            "heading_count": len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
            "table_count": len(soup.find_all('table'))
        }
    
    def _create_enhanced_platform_summary(self, results: Dict) -> Dict:
        """Enhanced platform összefoglaló létrehozása"""
        scores = {}
        hybrid_scores = {}
        ai_scores = {}
        levels = {}
        
        for platform, data in results.items():
            if platform in ['summary', 'ai_analysis'] or 'error' in data:
                continue
                
            scores[platform] = data.get('compatibility_score', 0)
            hybrid_scores[platform] = data.get('hybrid_compatibility_score', scores[platform])
            ai_scores[platform] = data.get('ai_score', 0)
            levels[platform] = data.get('optimization_level', 'Ismeretlen')
        
        if not scores:
            return {"error": "Nincs érvényes platform adat"}
        
        # Alapstatisztikák
        avg_score = sum(scores.values()) / len(scores)
        avg_hybrid = sum(hybrid_scores.values()) / len(hybrid_scores)
        avg_ai = sum(ai_scores.values()) / len(ai_scores) if any(ai_scores.values()) else 0
        
        best_platform = max(hybrid_scores, key=hybrid_scores.get)
        worst_platform = min(hybrid_scores, key=hybrid_scores.get)
        
        # AI elemzés összefoglalója
        ai_summary = results.get('ai_analysis', {})
        
        return {
            "average_compatibility": round(avg_score, 1),
            "average_hybrid_score": round(avg_hybrid, 1),
            "average_ai_score": round(avg_ai, 1),
            "best_platform": {"name": best_platform, "score": hybrid_scores[best_platform]},
            "worst_platform": {"name": worst_platform, "score": hybrid_scores[worst_platform]},
            "platform_scores": scores,
            "hybrid_scores": hybrid_scores,
            "ai_scores": ai_scores,
            "optimization_levels": levels,
            "overall_level": self._get_overall_level(avg_hybrid),
            "ai_enhanced": bool(ai_summary),
            "ai_overall_score": ai_summary.get('overall_ai_score', 0),
            "improvement_potential": round(max(hybrid_scores.values()) - min(hybrid_scores.values()), 1)
        }


class MLPlatformScorer:
    """Machine Learning alapú platform scoring"""
    
    def __init__(self):
        self.feature_weights = {
            'chatgpt': {
                'list_count': 0.25, 'question_count': 0.20, 'step_indicators': 0.30,
                'word_count': 0.10, 'code_blocks': 0.15
            },
            'claude': {
                'word_count': 0.30, 'external_links': 0.20, 'technical_depth': 0.25,
                'context_indicators': 0.15, 'citations': 0.10
            },
            'gemini': {
                'image_count': 0.25, 'freshness_indicators': 0.20, 'schema_count': 0.20,
                'external_links': 0.15, 'structured_data': 0.20
            },
            'bing_chat': {
                'external_links': 0.35, 'citations': 0.25, 'time_sensitivity': 0.20,
                'source_indicators': 0.20
            }
        }
    
    def predict_platform_score(self, platform: str, content: str, metadata: Dict) -> float:
        """Platform score predikció feature-alapú modellel"""
        if platform not in self.feature_weights:
            return 50.0  # Alapértelmezett
        
        features = self._extract_features(content, metadata)
        weights = self.feature_weights[platform]
        
        score = 0
        for feature, weight in weights.items():
            feature_value = features.get(feature, 0)
            normalized_value = min(100, feature_value * 10)  # Normalizálás
            score += normalized_value * weight
        
        return round(min(100, max(0, score)), 1)
    
    def _extract_features(self, content: str, metadata: Dict) -> Dict:
        """Feature extraction tartalomból és metadatából"""
        content_lower = content.lower()
        
        features = {
            # Alapvető metrikák
            'word_count': len(content.split()) / 100,  # Normalizálva
            'question_count': content.count('?'),
            'list_count': metadata.get('list_count', 0),
            'external_links': metadata.get('external_links', 0),
            'schema_count': metadata.get('schema_count', 0),
            'image_count': metadata.get('image_count', 0),
            
            # ChatGPT specifikus
            'step_indicators': len(re.findall(r'\b(?:lépés|step)\s*\d+|\d+\.\s+[A-ZÁÉÍÓÖŐÚÜŰ]', content, re.I)),
            'code_blocks': content.count('```') + content.count('<code>'),
            
            # Claude specifikus
            'technical_depth': len(re.findall(r'\b[A-ZÁÉÍÓÖŐÚÜŰ][a-záéíóöőúüű]*(?:ás|és|ség|ság|izmus|ció)\b', content)),
            'context_indicators': len(re.findall(r'\b(?:kontextus|background|áttekintés|however|nevertheless)\b', content_lower)),
            'citations': len(re.findall(r'(?:forrás|source|according to|based on)', content_lower)),
            
            # Gemini specifikus
            'freshness_indicators': len(re.findall(r'\b(?:202[4-5]|friss|new|latest|aktuális)\b', content_lower)),
            'structured_data': metadata.get('table_count', 0) + metadata.get('heading_count', 0),
            
            # Bing specifikus
            'source_indicators': len(re.findall(r'\b(?:forrás szerint|according to|based on)\b', content_lower)),
            'time_sensitivity': len(re.findall(r'\b(?:ma|today|mostani|current)\b', content_lower))
        }
        
        return features