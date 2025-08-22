import json
import re
import time
import os
from typing import Dict, List, Optional
from openai import OpenAI
from config import OPENAI_API_KEY

# .env fájl betöltése - most már a config.py kezeli
# load_dotenv()  # Ezt már nem kell, mert a config.py kezeli

class AIContentEvaluator:
    """AI-alapú tartalom értékelő - OpenAI API használatával"""
    
    def __init__(self):
        # OpenAI kliens inicializálása
        api_key = OPENAI_API_KEY
        if not api_key:
            print("⚠️ FIGYELEM: OPENAI_API_KEY nincs beállítva!")
            print("Állítsd be a .env fájlban vagy Streamlit secrets-ben: OPENAI_API_KEY=your_api_key")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)
            print("✅ OpenAI API inicializálva")
        
        self.max_content_length = 6000  # Token limit miatt
        self.evaluation_cache = {}  # Egyszerű memória cache
        self.model = "gpt-4o-mini"  # Költséghatékony, de jó modell
        
    def evaluate_content_quality(self, content: str, target_platforms: List[str] = None) -> Dict:
        """AI-alapú tartalom minőség értékelés - VALÓS OpenAI API"""
        if not self.client:
            return self._fallback_heuristic_evaluation(content, target_platforms or ['chatgpt', 'claude', 'gemini'])
            
        if not target_platforms:
            target_platforms = ['chatgpt', 'claude', 'gemini', 'bing_chat']
        
        # Tartalom rövidítése ha túl hosszú
        truncated_content = self._truncate_content(content)
        
        # Cache ellenőrzés
        cache_key = f"quality_{hash(truncated_content)}"
        if cache_key in self.evaluation_cache:
            return self.evaluation_cache[cache_key]
        
        try:
            # Valós OpenAI API hívás
            evaluation = self._request_ai_evaluation(truncated_content, target_platforms)
            
            # Cache-eljük az eredményt
            self.evaluation_cache[cache_key] = evaluation
            
            return evaluation
            
        except Exception as e:
            print(f"    ⚠️ OpenAI API hiba: {e}")
            # Fallback heurisztikus értékelésre
            return self._fallback_heuristic_evaluation(content, target_platforms)
    
    def semantic_relevance_score(self, content: str, keywords: List[str]) -> float:
        """Szemantikai releváncia pontszám - OpenAI-val"""
        if not keywords or not self.client:
            return self._heuristic_semantic_relevance(content, keywords)
        
        try:
            prompt = f"""
Értékeld a következő tartalom szemantikai relevanciáját ezekhez a kulcsszavakhoz: {', '.join(keywords)}

Tartalom (első 1000 karakter):
{content[:1000]}

Adj egy pontszámot 0-100 között, ami megmutatja mennyire releváns a tartalom a kulcsszavakhoz.
Csak egy számot adj válaszul, semmi mást.
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Te egy SEO és tartalom releváncia szakértő vagy. Csak számokkal válaszolj."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=10
            )
            
            score_text = response.choices[0].message.content.strip()
            # Kinyerjük a számot a válaszból
            score = float(re.findall(r'\d+\.?\d*', score_text)[0])
            return min(100, max(0, score))
            
        except Exception as e:
            print(f"    ⚠️ Semantic relevance API hiba: {e}")
            return self._heuristic_semantic_relevance(content, keywords)
    
    def readability_ai_score(self, content: str) -> Dict:
        """AI-alapú olvashatóság értékelés - VALÓS OpenAI API"""
        if not self.client:
            return self._fallback_readability_score(content)
            
        try:
            prompt = f"""
Értékeld ezt a tartalmat olvashatóság szempontjából. 

Tartalom (első 1500 karakter):
{content[:1500]}

Válaszolj CSAK egy valid JSON objektummal, semmi mást ne írj:
{{
    "clarity_score": <1-100>,
    "engagement_score": <1-100>, 
    "structure_score": <1-100>,
    "ai_friendliness": <1-100>,
    "overall_score": <1-100>,
    "improvements": ["konkrét javaslat 1", "konkrét javaslat 2"]
}}
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Te egy tartalom minőség elemző szakértő vagy. CSAK valid JSON-nal válaszolj, semmi mást ne írj."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300,
                response_format={"type": "json_object"}  # JSON mód
            )
            
            ai_response = json.loads(response.choices[0].message.content)
            return ai_response
            
        except Exception as e:
            print(f"    ⚠️ Readability API hiba: {e}")
            return self._fallback_readability_score(content)
    
    def factual_accuracy_check(self, content: str) -> Dict:
        """Faktualitás ellenőrzése - VALÓS OpenAI API"""
        if not self.client:
            return self._heuristic_factual_check(content)
            
        try:
            prompt = f"""
Elemezd a következő tartalom faktualitását és megbízhatóságát.

Tartalom (első 2000 karakter):
{content[:2000]}

Értékeld a következő szempontok alapján:
1. Vannak-e hivatkozások vagy források?
2. Vannak-e konkrét számok mértékegységekkel?
3. Vannak-e ellenőrizhető állítások?
4. Mennyire tűnik megbízhatónak?

Válaszolj CSAK egy valid JSON objektummal:
{{
    "factual_score": <0-100>,
    "citations_present": <szám>,
    "numbers_with_units": <szám>,
    "verifiable_claims": <szám>,
    "confidence_level": "low/medium/high",
    "issues": ["probléma1", "probléma2"]
}}
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Te egy tényellenőrző szakértő vagy. CSAK valid JSON-nal válaszolj."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Kompatibilitás a régi formátummal
            result["accuracy_indicators"] = {
                "citations_present": result.get("citations_present", 0),
                "numbers_with_units": result.get("numbers_with_units", 0),
                "verifiable_claims": result.get("verifiable_claims", 0)
            }
            
            return result
            
        except Exception as e:
            print(f"    ⚠️ Factual check API hiba: {e}")
            return self._heuristic_factual_check(content)
    
    def platform_specific_evaluation(self, content: str, platform: str) -> Dict:
        """Platform-specifikus értékelés - VALÓS OpenAI API"""
        if not self.client:
            return self._heuristic_platform_evaluation(content, platform)
            
        platform_prompts = {
            'chatgpt': """
Értékeld mennyire alkalmas ez a tartalom ChatGPT válaszokhoz:
- Van-e step-by-step struktúra?
- Vannak-e számozott listák?
- Vannak-e kérdés-válasz blokkok?
- Mennyire praktikus és actionable?
""",
            'claude': """
Értékeld mennyire alkalmas ez a tartalom Claude válaszokhoz:
- Van-e részletes kontextus?
- Vannak-e hivatkozások és források?
- Mennyire árnyalt és kiegyensúlyozott?
- Van-e mélység a magyarázatokban?
""",
            'gemini': """
Értékeld mennyire alkalmas ez a tartalom Google Gemini válaszokhoz:
- Vannak-e friss információk és dátumok?
- Van-e multimédia tartalom említés?
- Vannak-e külső linkek?
- Mennyire strukturált az információ?
""",
            'bing_chat': """
Értékeld mennyire alkalmas ez a tartalom Bing Chat válaszokhoz:
- Vannak-e hivatkozások és források?
- Vannak-e külső linkek?
- Mennyire időszerű az információ?
- Vannak-e kereshető kifejezések?
"""
        }
        
        if platform not in platform_prompts:
            return {"error": f"Unknown platform: {platform}"}
            
        try:
            prompt = f"""
{platform_prompts[platform]}

Tartalom (első 2000 karakter):
{content[:2000]}

Válaszolj CSAK egy valid JSON objektummal:
{{
    "platform_score": <0-100>,
    "strengths": ["erősség1", "erősség2"],
    "weaknesses": ["gyengeség1", "gyengeség2"],
    "optimization_suggestions": ["javaslat1", "javaslat2", "javaslat3"]
}}
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"Te egy {platform} optimalizálási szakértő vagy. CSAK valid JSON-nal válaszolj."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=400,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            result["platform"] = platform
            result["evaluation_method"] = "openai_api"
            
            return result
            
        except Exception as e:
            print(f"    ⚠️ Platform evaluation API hiba ({platform}): {e}")
            return self._heuristic_platform_evaluation(content, platform)
    
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
        """AI értékelés kérés - VALÓS OpenAI API"""
        if not self.client:
            return self._fallback_heuristic_evaluation(content, platforms)
            
        try:
            platforms_str = ', '.join(platforms)
            prompt = f"""
Értékeld a következő tartalmat AI platformok ({platforms_str}) szempontjából.

Tartalom (első 3000 karakter):
{content[:3000]}

Értékeld minden platform szempontjából 0-100 skálán:
- Mennyire alkalmas az adott AI platform válaszaihoz?
- Mennyire könnyen feldolgozható?
- Mennyire strukturált és idézhető?

Válaszolj CSAK egy valid JSON objektummal:
{{
    "ai_quality_scores": {{
        "chatgpt": <0-100>,
        "claude": <0-100>,
        "gemini": <0-100>,
        "bing_chat": <0-100>
    }},
    "overall_ai_score": <átlag 0-100>,
    "ai_recommendations": ["javaslat1", "javaslat2", "javaslat3"],
    "best_platform": "platform_neve",
    "content_strengths": ["erősség1", "erősség2"],
    "content_weaknesses": ["gyengeség1", "gyengeség2"]
}}
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Te egy AI content optimization szakértő vagy. Értékeld a tartalmat különböző AI platformok szempontjából. CSAK valid JSON-nal válaszolj."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            result["evaluation_timestamp"] = time.time()
            result["evaluation_method"] = "openai_api"
            result["model_used"] = self.model
            
            # Csak a kért platformok pontszámait tartjuk meg
            filtered_scores = {
                platform: result["ai_quality_scores"].get(platform, 50)
                for platform in platforms
            }
            result["ai_quality_scores"] = filtered_scores
            
            # Átlag újraszámítása
            if filtered_scores:
                result["overall_ai_score"] = sum(filtered_scores.values()) / len(filtered_scores)
            
            return result
            
        except Exception as e:
            print(f"    ⚠️ AI evaluation API hiba: {e}")
            return self._fallback_heuristic_evaluation(content, platforms)
    
    # ========== FALLBACK / HEURISZTIKUS METÓDUSOK ==========
    
    def _fallback_heuristic_evaluation(self, content: str, platforms: List[str]) -> Dict:
        """Fallback heurisztikus értékelés ha nincs API"""
        word_count = len(content.split())
        sentence_count = len(re.split(r'[.!?]+', content))
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Heurisztikus pontszám
        heuristic_score = min(100, (
            (50 if 300 <= word_count <= 2000 else 30) +
            (20 if 10 <= avg_sentence_length <= 25 else 10) +
            (15 if content.count('?') >= 2 else 5) +
            (15 if len(re.findall(r'\n[-•]\s', content)) >= 2 else 5)
        ))
        
        return {
            "ai_quality_scores": {platform: heuristic_score for platform in platforms},
            "overall_ai_score": heuristic_score,
            "ai_recommendations": ["API kulcs nélküli alapértelmezett értékelés"],
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
            "engagement_score": 60,
            "structure_score": 50,
            "ai_friendliness": round((clarity_score + 50) / 2, 1),
            "overall_score": round((clarity_score + 50) / 2, 1),
            "improvements": ["API kulcs nélkül - heurisztikus értékelés"],
            "evaluation_method": "heuristic_fallback"
        }
    
    def _heuristic_semantic_relevance(self, content: str, keywords: List[str]) -> float:
        """Heurisztikus szemantikai releváncia"""
        if not keywords:
            return 0.0
        
        content_lower = content.lower()
        total_score = 0
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            direct_matches = content_lower.count(keyword_lower)
            total_score += direct_matches
        
        # Normalizálás
        normalized_score = min(100, (total_score / len(content)) * 10000)
        return round(normalized_score, 2)
    
    def _heuristic_factual_check(self, content: str) -> Dict:
        """Heurisztikus faktualitás ellenőrzés"""
        claims = self._extract_claims(content)
        
        accuracy_indicators = {
            "citations_present": len(re.findall(r'\[[\d,\s]+\]|(?:forrás|source|according to)', content.lower())),
            "numbers_with_units": len(re.findall(r'\d+(?:[.,]\d+)?\s*(?:%-|kg|m|km|€|Ft|\$)', content)),
            "verifiable_claims": len(claims)
        }
        
        factual_score = min(100, (
            accuracy_indicators["citations_present"] * 15 +
            accuracy_indicators["numbers_with_units"] * 10 +
            len(claims) * 5
        ))
        
        return {
            "factual_score": max(0, factual_score),
            "accuracy_indicators": accuracy_indicators,
            "extracted_claims": len(claims),
            "confidence_level": "medium" if factual_score > 50 else "low",
            "evaluation_method": "heuristic_fallback"
        }
    
    def _heuristic_platform_evaluation(self, content: str, platform: str) -> Dict:
        """Heurisztikus platform értékelés"""
        evaluations = {
            'chatgpt': self._evaluate_for_chatgpt_heuristic(content),
            'claude': self._evaluate_for_claude_heuristic(content),
            'gemini': self._evaluate_for_gemini_heuristic(content),
            'bing_chat': self._evaluate_for_bing_heuristic(content)
        }
        
        return evaluations.get(platform, {"error": f"Unknown platform: {platform}"})
    
    def _extract_claims(self, content: str) -> List[str]:
        """Állítások kigyűjtése a tartalomból"""
        sentences = re.split(r'[.!?]+', content)
        claims = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
                
            # Számokat vagy kategorikus állításokat tartalmazó mondatok
            if re.search(r'\d+(?:[.,]\d+)?%?', sentence):
                claims.append(sentence)
            elif re.search(r'\b(?:minden|all|soha|never|mindig|always|legjobb|best|worst|legrosszabb)\b', sentence.lower()):
                claims.append(sentence)
        
        return claims[:10]
    
    def _evaluate_for_chatgpt_heuristic(self, content: str) -> Dict:
        """ChatGPT-specifikus heurisztikus értékelés"""
        step_indicators = len(re.findall(r'\b(?:lépés|step)\s*\d+|\d+\.\s+[A-ZÁÉÍÓÖŐÚÜŰ]', content, re.I))
        list_count = content.count('\n-') + content.count('\n•') + len(re.findall(r'\n\d+\.', content))
        question_count = content.count('?')
        
        score = min(100, step_indicators * 15 + list_count * 10 + question_count * 8 + 40)
        
        return {
            "platform_score": score,
            "strengths": ["Strukturált tartalom"] if list_count > 2 else [],
            "weaknesses": ["Kevés lista"] if list_count < 2 else [],
            "optimization_suggestions": [
                "Több számozott lépés hozzáadása" if step_indicators < 3 else "Jó step-by-step struktúra",
                "FAQ szekció bővítése" if question_count < 3 else "Megfelelő Q&A tartalom"
            ],
            "evaluation_method": "heuristic"
        }
    
    def _evaluate_for_claude_heuristic(self, content: str) -> Dict:
        """Claude-specifikus heurisztikus értékelés"""
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
            "strengths": ["Részletes tartalom"] if word_count > 800 else [],
            "weaknesses": ["Rövid tartalom"] if word_count < 500 else [],
            "optimization_suggestions": [
                "Tartalom bővítése kontextussal" if word_count < 800 else "Megfelelő tartalom hossz",
                "Több hivatkozás hozzáadása" if citations < 3 else "Jó forrás használat"
            ],
            "evaluation_method": "heuristic"
        }
    
    def _evaluate_for_gemini_heuristic(self, content: str) -> Dict:
        """Gemini-specifikus heurisztikus értékelés"""
        image_refs = content.lower().count('kép') + content.lower().count('image') + content.lower().count('ábra')
        fresh_indicators = len(re.findall(r'\b(?:202[4-5]|friss|new|latest|aktuális)\b', content.lower()))
        links = content.count('http')
        
        score = min(100, image_refs * 15 + fresh_indicators * 12 + links * 8 + 35)
        
        return {
            "platform_score": score,
            "strengths": ["Multimédia tartalom"] if image_refs > 2 else [],
            "weaknesses": ["Kevés vizuális elem"] if image_refs < 2 else [],
            "optimization_suggestions": [
                "Multimédia tartalom hozzáadása" if image_refs < 2 else "Jó vizuális elemek",
                "Frissebb információk hangsúlyozása" if fresh_indicators < 3 else "Aktuális tartalom"
            ],
            "evaluation_method": "heuristic"
        }
    
    def _evaluate_for_bing_heuristic(self, content: str) -> Dict:
        """Bing Chat-specifikus heurisztikus értékelés"""
        source_indicators = len(re.findall(r'\b(?:forrás|source|according to|based on)\b', content.lower()))
        external_refs = content.count('http')
        time_sensitive = len(re.findall(r'\b(?:ma|today|mostani|current|aktuális)\b', content.lower()))
        
        score = min(100, source_indicators * 15 + external_refs * 10 + time_sensitive * 8 + 30)
        
        return {
            "platform_score": score,
            "strengths": ["Jó forrás használat"] if source_indicators > 3 else [],
            "weaknesses": ["Kevés hivatkozás"] if external_refs < 3 else [],
            "optimization_suggestions": [
                "Több külső hivatkozás" if external_refs < 3 else "Megfelelő hivatkozás sűrűség",
                "Időszerű információk kiemelése" if time_sensitive < 2 else "Jó időszerűség"
            ],
            "evaluation_method": "heuristic"
        }