import json
import re
import time
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup


class AIContentEvaluator:
    """AI-alapú tartalom értékelő - Claude API használatával"""
    
    def __init__(self):
        self.anthropic_api_url = "https://api.anthropic.com/v1/messages"
        self.max_content_length = 6000  # Token limit miatt
        self.evaluation_cache = {}  # Egyszerű memória cache
        
    def evaluate_content_quality(self, content: str, target_platforms: List[str] = None) -> Dict:
        """AI-alapú tartalom minőség értékelés"""
        if not target_platforms:
            target_platforms = ['chatgpt', 'claude', 'gemini']
        
        # Tartalom rövidítése ha túl hosszú
        truncated_content = self._truncate_content(content)
        
        # Cache ellenőrzés
        cache_key = f"quality_{hash(truncated_content)}"
        if cache_key in self.evaluation_cache:
            return self.evaluation_cache[cache_key]
        
        try:
            # AI értékelés kérés
            evaluation = self._request_ai_evaluation(truncated_content, target_platforms)
            
            # Cache-eljük az eredményt
            self.evaluation_cache[cache_key] = evaluation
            
            return evaluation
            
        except Exception as e:
            print(f"    ⚠️ AI értékelés hiba: {e}")
            # Fallback heurisztikus értékelésre
            return self._fallback_heuristic_evaluation(content, target_platforms)
    
    def semantic_relevance_score(self, content: str, keywords: List[str]) -> float:
        """Szemantikai releváncia pontszám"""
        if not keywords:
            return 0.0
        
        # Egyszerű megközelítés - kulcsszavak kontextuális előfordulása
        content_lower = content.lower()
        total_score = 0
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Direkt match
            direct_matches = content_lower.count(keyword_lower)
            
            # Kontextuális előfordulás (50 karakter környezetben)
            contextual_score = 0
            for match in re.finditer(re.escape(keyword_lower), content_lower):
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                context = content_lower[start:end]
                
                # Pozitív kontextus indikátorok
                positive_indicators = ['fontos', 'kulcs', 'essential', 'important', 'key']
                contextual_score += sum(1 for indicator in positive_indicators if indicator in context)
            
            keyword_score = (direct_matches * 1.0) + (contextual_score * 0.5)
            total_score += keyword_score
        
        # Normalizálás a tartalom hosszához képest
        normalized_score = min(100, (total_score / len(content)) * 10000)
        return round(normalized_score, 2)
    
    def readability_ai_score(self, content: str) -> Dict:
        """AI-alapú olvashatóság értékelés"""
        try:
            prompt = f"""
Értékeld ezt a tartalmat olvashatóság szempontjából 1-100 skálán:

{content[:1500]}...

Add meg JSON formátumban:
{{
    "clarity_score": <1-100>,
    "engagement_score": <1-100>, 
    "structure_score": <1-100>,
    "ai_friendliness": <1-100>,
    "overall_score": <1-100>,
    "improvements": ["javaslat1", "javaslat2"]
}}
"""
            
            # Egyszerű AI hívás szimuláció (valós implementációban Claude API)
            ai_response = self._simulate_ai_response("readability", content)
            return ai_response
            
        except Exception as e:
            print(f"    ⚠️ AI olvashatóság hiba: {e}")
            return self._fallback_readability_score(content)
    
    def factual_accuracy_check(self, content: str) -> Dict:
        """Faktualitás ellenőrzése"""
        # Állítások kigyűjtése
        claims = self._extract_claims(content)
        
        accuracy_indicators = {
            "citations_present": len(re.findall(r'\[[\d,\s]+\]|(?:forrás|source|according to)', content.lower())),
            "numbers_with_units": len(re.findall(r'\d+(?:[.,]\d+)?\s*(?:%-|kg|m|km|€|Ft|\$)', content)),
            "hedging_language": len(re.findall(r'\b(?:körülbelül|kb|approximately|estimated|around)\b', content.lower())),
            "absolute_claims": len(re.findall(r'\b(?:minden|all|soha|never|mindig|always)\b', content.lower())),
            "date_references": len(re.findall(r'\b\d{4}\b|\b(?:202[0-9])\b', content))
        }
        
        # Faktualitás pontszám kalkuláció
        factual_score = min(100, (
            accuracy_indicators["citations_present"] * 15 +
            accuracy_indicators["numbers_with_units"] * 10 +
            accuracy_indicators["hedging_language"] * 5 +
            accuracy_indicators["date_references"] * 8 -
            accuracy_indicators["absolute_claims"] * 3  # Levonás túl kategorikus állításokért
        ))
        
        return {
            "factual_score": max(0, factual_score),
            "accuracy_indicators": accuracy_indicators,
            "extracted_claims": len(claims),
            "confidence_level": "medium" if factual_score > 50 else "low"
        }
    
    def platform_specific_evaluation(self, content: str, platform: str) -> Dict:
        """Platform-specifikus értékelés"""
        evaluations = {
            'chatgpt': self._evaluate_for_chatgpt(content),
            'claude': self._evaluate_for_claude(content),
            'gemini': self._evaluate_for_gemini(content),
            'bing_chat': self._evaluate_for_bing(content)
        }
        
        return evaluations.get(platform, {"error": f"Unknown platform: {platform}"})
    
    def _truncate_content(self, content: str) -> str:
        """Tartalom rövidítése token limit miatt"""
        if len(content) <= self.max_content_length:
            return content
        
        # Okos rövidítés - megpróbáljuk megőrizni a struktúrát
        sentences = content.split('. ')
        truncated = []
        current_length = 0
        
        for sentence in sentences:
            if current_length + len(sentence) > self.max_content_length:
                break
            truncated.append(sentence)
            current_length += len(sentence)
        
        return '. '.join(truncated) + '...'
    
    def _request_ai_evaluation(self, content: str, platforms: List[str]) -> Dict:
        """AI értékelés kérés - szimuláció valós API helyett"""
        # Valós implementációban itt lenne a Claude API hívás
        # Most heurisztikus alapú "AI" választ szimulálunk
        
        word_count = len(content.split())
        question_count = content.count('?')
        list_count = content.count('\n-') + content.count('\n•') + len(re.findall(r'\n\d+\.', content))
        
        # "AI" pontszám szimuláció
        ai_scores = {}
        for platform in platforms:
            base_score = min(100, (
                word_count * 0.05 +  # Hosszabb tartalom jobb
                question_count * 8 +  # Q&A formátum
                list_count * 12 +     # Strukturált tartalom
                50  # Alappontszám
            ))
            
            # Platform-specifikus módosítók
            if platform == 'chatgpt':
                base_score += list_count * 5  # ChatGPT szereti a listákat
            elif platform == 'claude':
                base_score += (word_count > 500) * 10  # Claude hosszabb tartalmat preferál
            elif platform == 'gemini':
                base_score += content.count('https://') * 3  # Gemini szereti a hivatkozásokat
            
            ai_scores[platform] = min(100, max(0, base_score))
        
        return {
            "ai_quality_scores": ai_scores,
            "overall_ai_score": sum(ai_scores.values()) / len(ai_scores),
            "ai_recommendations": self._generate_ai_recommendations(content, ai_scores),
            "evaluation_timestamp": time.time()
        }
    
    def _fallback_heuristic_evaluation(self, content: str, platforms: List[str]) -> Dict:
        """Fallback heurisztikus értékelés"""
        # Alapmetrikák
        word_count = len(content.split())
        sentence_count = len(re.split(r'[.!?]+', content))
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Heurisztikus pontszám
        heuristic_score = min(100, (
            (50 if 300 <= word_count <= 2000 else 30) +  # Optimális hossz
            (20 if 10 <= avg_sentence_length <= 25 else 10) +  # Optimális mondathossz
            (15 if content.count('?') >= 2 else 5) +  # Kérdések jelenléte
            (15 if len(re.findall(r'\n[-•]\s', content)) >= 2 else 5)  # Listák
        ))
        
        return {
            "ai_quality_scores": {platform: heuristic_score for platform in platforms},
            "overall_ai_score": heuristic_score,
            "ai_recommendations": ["Alapértelmezett heurisztikus értékelés"],
            "evaluation_method": "heuristic_fallback"
        }
    
    def _fallback_readability_score(self, content: str) -> Dict:
        """Fallback olvashatóság pontszám"""
        words = content.split()
        sentences = re.split(r'[.!?]+', content)
        
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        clarity_score = max(0, 100 - (avg_word_length - 5) * 10 - (avg_sentence_length - 15) * 2)
        
        return {
            "clarity_score": round(clarity_score, 1),
            "engagement_score": 60,  # Alapértelmezett
            "structure_score": 50,   # Alapértelmezett
            "ai_friendliness": round((clarity_score + 50) / 2, 1),
            "overall_score": round((clarity_score + 50) / 2, 1),
            "improvements": ["Egyszerűbb mondatok használata", "Több strukturált tartalom"]
        }
    
    def _extract_claims(self, content: str) -> List[str]:
        """Állítások kigyűjtése a tartalomból"""
        # Egyszerű implementáció - mondatok, amik számokat vagy kategorikus állításokat tartalmaznak
        sentences = re.split(r'[.!?]+', content)
        claims = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
                
            # Számokat tartalmazó mondatok
            if re.search(r'\d+(?:[.,]\d+)?%?', sentence):
                claims.append(sentence)
            # Kategorikus állítások
            elif re.search(r'\b(?:minden|all|soha|never|mindig|always|legjobb|best|worst|legrosszabb)\b', sentence.lower()):
                claims.append(sentence)
        
        return claims[:10]  # Maximum 10 claim
    
    def _evaluate_for_chatgpt(self, content: str) -> Dict:
        """ChatGPT-specifikus értékelés"""
        step_indicators = len(re.findall(r'\b(?:lépés|step)\s*\d+|\d+\.\s+[A-ZÁÉÍÓÖŐÚÜŰ]', content, re.I))
        list_count = content.count('\n-') + content.count('\n•') + len(re.findall(r'\n\d+\.', content))
        question_count = content.count('?')
        
        score = min(100, step_indicators * 15 + list_count * 10 + question_count * 8 + 40)
        
        return {
            "platform_score": score,
            "step_by_step_content": step_indicators,
            "structured_lists": list_count,
            "interactive_elements": question_count,
            "optimization_suggestions": [
                "Több számozott lépés hozzáadása" if step_indicators < 3 else "Jó step-by-step struktúra",
                "FAQ szekció bővítése" if question_count < 3 else "Megfelelő Q&A tartalom"
            ]
        }
    
    def _evaluate_for_claude(self, content: str) -> Dict:
        """Claude-specifikus értékelés"""
        word_count = len(content.split())
        context_indicators = len(re.findall(r'\b(?:kontextus|background|áttekintés|however|nevertheless)\b', content.lower()))
        citations = len(re.findall(r'(?:forrás|source|according to|based on)', content.lower()))
        
        score = min(100, (
            (25 if word_count > 800 else 15) +
            context_indicators * 8 +
            citations * 12 +
            30
        ))
        
        return {
            "platform_score": score,
            "content_depth": word_count,
            "contextual_information": context_indicators,
            "citation_quality": citations,
            "optimization_suggestions": [
                "Tartalom bővítése kontextussal" if word_count < 800 else "Megfelelő tartalom hossz",
                "Több hivatkozás hozzáadása" if citations < 3 else "Jó forrás használat"
            ]
        }
    
    def _evaluate_for_gemini(self, content: str) -> Dict:
        """Gemini-specifikus értékelés"""
        image_refs = content.lower().count('kép') + content.lower().count('image') + content.lower().count('ábra')
        fresh_indicators = len(re.findall(r'\b(?:202[4-5]|friss|new|latest|aktuális)\b', content.lower()))
        links = content.count('http')
        
        score = min(100, image_refs * 15 + fresh_indicators * 12 + links * 8 + 35)
        
        return {
            "platform_score": score,
            "multimedia_references": image_refs,
            "freshness_indicators": fresh_indicators,
            "external_links": links,
            "optimization_suggestions": [
                "Multimédia tartalom hozzáadása" if image_refs < 2 else "Jó vizuális elemek",
                "Frissebb információk hangsúlyozása" if fresh_indicators < 3 else "Aktuális tartalom"
            ]
        }
    
    def _evaluate_for_bing(self, content: str) -> Dict:
        """Bing Chat-specifikus értékelés"""
        source_indicators = len(re.findall(r'\b(?:forrás|source|according to|based on)\b', content.lower()))
        external_refs = content.count('http')
        time_sensitive = len(re.findall(r'\b(?:ma|today|mostani|current|aktuális)\b', content.lower()))
        
        score = min(100, source_indicators * 15 + external_refs * 10 + time_sensitive * 8 + 30)
        
        return {
            "platform_score": score,
            "source_citations": source_indicators,
            "external_references": external_refs,
            "time_sensitivity": time_sensitive,
            "optimization_suggestions": [
                "Több külső hivatkozás" if external_refs < 3 else "Megfelelő hivatkozás sűrűség",
                "Időszerű információk kiemelése" if time_sensitive < 2 else "Jó időszerűség"
            ]
        }
    
    def _generate_ai_recommendations(self, content: str, scores: Dict) -> List[str]:
        """AI alapú ajánlások generálása"""
        recommendations = []
        
        avg_score = sum(scores.values()) / len(scores)
        
        if avg_score < 50:
            recommendations.append("Tartalom alapvető átstrukturálása szükséges")
        elif avg_score < 70:
            recommendations.append("Néhány platform-specifikus optimalizálás ajánlott")
        else:
            recommendations.append("Jó AI kompatibilitás, finomhangolás elegendő")
        
        # Platform-specifikus ajánlások
        lowest_platform = min(scores, key=scores.get)
        if scores[lowest_platform] < 60:
            recommendations.append(f"{lowest_platform.title()} platform optimalizálás prioritás")
        
        return recommendations
    
    def _simulate_ai_response(self, evaluation_type: str, content: str) -> Dict:
        """AI válasz szimuláció fejlesztési célokra"""
        # Ez egy placeholder - valós implementációban Claude API hívás lenne itt
        if evaluation_type == "readability":
            return {
                "clarity_score": 75,
                "engagement_score": 68,
                "structure_score": 70,
                "ai_friendliness": 72,
                "overall_score": 71,
                "improvements": ["Több alszekció hozzáadása", "Kérdés-válasz blokkok beépítése"]
            }
        
        return {}