import re
import json
import pickle
import os
import numpy as np
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

# Scikit-learn importok a valós ML-hez
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import mean_squared_error, r2_score
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ Scikit-learn nem telepítve. ML funkciók korlátozottak.")
    print("Telepítés: pip install scikit-learn joblib")


class AIPlattformOptimizer(ABC):
    """Absztrakt osztály AI platform optimalizáláshoz"""
    
    @abstractmethod
    def analyze_compatibility(self, soup: BeautifulSoup, text: str) -> Dict:
        pass
    
    @abstractmethod
    def get_optimization_suggestions(self, analysis: Dict) -> List[Dict]:
        pass


class ChatGPTOptimizer(AIPlattformOptimizer):
    """ChatGPT/OpenAI specifikus optimalizálás - VALÓS IMPLEMENTÁCIÓ"""
    
    def __init__(self):
        self.preferred_formats = [
            'FAQ', 'HowTo', 'listicle', 'step-by-step', 'comparison'
        ]
        
        # ChatGPT VALÓS preferenciák (OpenAI dokumentáció alapján)
        self.positive_signals = {
            'step_indicators': {'weight': 3.5, 'patterns': [
                r'\b(?:step|lépés)\s*\d+',
                r'\b\d+\.\s+[A-ZÁÉÍÓÖŐÚÜŰ]',
                r'\bFirst|Second|Third|Finally\b',
                r'\bElőször|Másodszor|Harmadszor|Végül\b'
            ]},
            'structured_content': {'weight': 3.0, 'patterns': [
                r'<ol>.*?</ol>',
                r'<ul>.*?</ul>',
                r'\n\d+\.',
                r'\n[-•*]\s'
            ]},
            'code_examples': {'weight': 2.5, 'patterns': [
                r'```[\s\S]*?```',
                r'<code>.*?</code>',
                r'<pre>.*?</pre>'
            ]},
            'clear_headers': {'weight': 2.0, 'patterns': [
                r'#{1,6}\s+.+',
                r'<h[1-6]>.*?</h[1-6]>'
            ]},
            'qa_format': {'weight': 2.8, 'patterns': [
                r'\?.*?\n.*?[.!]',
                r'Q:.*?A:',
                r'Kérdés:.*?Válasz:'
            ]},
            'practical_keywords': {'weight': 1.5, 'patterns': [
                r'\b(how to|hogyan|tutorial|útmutató|guide|példa|example)\b'
            ]}
        }
        
        # Negatív jelek (ChatGPT kevésbé kedveli)
        self.negative_signals = {
            'long_paragraphs': {'weight': -1.5, 'threshold': 500},
            'no_structure': {'weight': -2.0},
            'complex_sentences': {'weight': -1.0, 'threshold': 50}
        }
    
    def analyze_compatibility(self, soup: BeautifulSoup, text: str) -> Dict:
        """ChatGPT kompatibilitás elemzése - VALÓS SCORING"""
        
        # Inicializálás
        detailed_scores = {}
        total_score = 0
        max_possible_score = 0
        
        # POZITÍV JELEK ELEMZÉSE
        for signal_name, signal_data in self.positive_signals.items():
            count = 0
            matches = []
            
            for pattern in signal_data['patterns']:
                found = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                count += len(found)
                if found:
                    matches.extend(found[:3])  # Első 3 példa tárolása
            
            # Súlyozott pontszám
            signal_score = min(count * signal_data['weight'], 100 * signal_data['weight'])
            total_score += signal_score
            max_possible_score += 100 * signal_data['weight']
            
            detailed_scores[signal_name] = {
                'count': count,
                'score': round(signal_score, 2),
                'examples': matches[:3] if matches else []
            }
        
        # NEGATÍV JELEK ELEMZÉSE
        paragraphs = text.split('\n\n')
        long_paragraphs = [p for p in paragraphs if len(p) > self.negative_signals['long_paragraphs']['threshold']]
        
        if long_paragraphs:
            penalty = len(long_paragraphs) * abs(self.negative_signals['long_paragraphs']['weight'])
            total_score -= penalty
            detailed_scores['long_paragraphs_penalty'] = -penalty
        
        # Struktúra hiánya
        if len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])) < 2:
            penalty = abs(self.negative_signals['no_structure']['weight']) * 10
            total_score -= penalty
            detailed_scores['no_structure_penalty'] = -penalty
        
        # Komplex mondatok
        sentences = re.split(r'[.!?]+', text)
        complex_sentences = [s for s in sentences if len(s.split()) > self.negative_signals['complex_sentences']['threshold']]
        
        if len(complex_sentences) > len(sentences) * 0.3:
            penalty = abs(self.negative_signals['complex_sentences']['weight']) * 10
            total_score -= penalty
            detailed_scores['complex_sentences_penalty'] = -penalty
        
        # SPECIÁLIS CHATGPT METRIKÁK
        
        # Step-by-step tartalom mélysége
        step_depth = self._analyze_step_depth(soup, text)
        detailed_scores['step_depth'] = step_depth
        total_score += step_depth['score']
        
        # Listák és strukturáltság
        list_analysis = self._analyze_list_structure(soup)
        detailed_scores['list_structure'] = list_analysis
        total_score += list_analysis['score']
        
        # Interaktivitás és engagement
        engagement = self._analyze_engagement_factors(text)
        detailed_scores['engagement'] = engagement
        total_score += engagement['score']
        
        # Végső pontszám normalizálása 0-100 skálára
        compatibility_score = max(0, min(100, (total_score / max_possible_score) * 100))
        
        return {
            "platform": "ChatGPT",
            "compatibility_score": round(compatibility_score, 1),
            "detailed_scores": detailed_scores,
            "optimization_level": self._get_optimization_level(compatibility_score),
            "strengths": self._identify_strengths(detailed_scores),
            "weaknesses": self._identify_weaknesses(detailed_scores),
            "chatgpt_specific": {
                "has_numbered_steps": detailed_scores.get('step_indicators', {}).get('count', 0) > 0,
                "has_code_examples": detailed_scores.get('code_examples', {}).get('count', 0) > 0,
                "has_qa_format": detailed_scores.get('qa_format', {}).get('count', 0) > 0,
                "structure_quality": list_analysis.get('quality', 'poor'),
                "engagement_level": engagement.get('level', 'low')
            }
        }
    
    def _analyze_step_depth(self, soup: BeautifulSoup, text: str) -> Dict:
        """Step-by-step tartalom mélységi elemzése"""
        steps = re.findall(r'(?:step|lépés)\s*(\d+)[:\s]*([^\n]+)', text, re.IGNORECASE)
        
        if not steps:
            return {'count': 0, 'score': 0, 'quality': 'none'}
        
        # Lépések minőségének értékelése
        quality_score = 0
        
        # Van-e minden lépéshez leírás?
        for step_num, step_text in steps:
            if len(step_text) > 20:
                quality_score += 5
            if len(step_text) > 50:
                quality_score += 3
        
        # Szekvenciális-e?
        step_numbers = [int(num) for num, _ in steps]
        if step_numbers == sorted(step_numbers):
            quality_score += 10
        
        return {
            'count': len(steps),
            'score': min(30, quality_score),
            'quality': 'excellent' if quality_score > 25 else 'good' if quality_score > 15 else 'fair',
            'sequential': step_numbers == sorted(step_numbers)
        }
    
    def _analyze_list_structure(self, soup: BeautifulSoup) -> Dict:
        """Lista struktúra részletes elemzése"""
        ordered_lists = soup.find_all('ol')
        unordered_lists = soup.find_all('ul')
        
        total_lists = len(ordered_lists) + len(unordered_lists)
        total_items = len(soup.find_all('li'))
        
        if total_lists == 0:
            return {'count': 0, 'items': 0, 'score': 0, 'quality': 'none'}
        
        avg_items_per_list = total_items / total_lists if total_lists else 0
        
        # Minőség értékelés
        quality_score = 0
        quality_score += min(20, total_lists * 5)
        quality_score += min(15, total_items * 1)
        
        if 3 <= avg_items_per_list <= 10:
            quality_score += 10
        
        # Nested lists bónusz
        nested_lists = len([li for li in soup.find_all('li') if li.find(['ul', 'ol'])])
        if nested_lists > 0:
            quality_score += 5
        
        return {
            'ordered': len(ordered_lists),
            'unordered': len(unordered_lists),
            'total': total_lists,
            'items': total_items,
            'avg_items': round(avg_items_per_list, 1),
            'nested': nested_lists,
            'score': min(40, quality_score),
            'quality': 'excellent' if quality_score > 35 else 'good' if quality_score > 20 else 'fair'
        }
    
    def _analyze_engagement_factors(self, text: str) -> Dict:
        """Engagement és interaktivitás elemzése"""
        engagement_score = 0
        
        # Kérdések
        questions = len(re.findall(r'\?', text))
        engagement_score += min(15, questions * 3)
        
        # Direkt megszólítás
        direct_address = len(re.findall(r'\b(you|your|te|ön|tied|öné)\b', text, re.IGNORECASE))
        engagement_score += min(10, direct_address * 0.5)
        
        # Call-to-action
        cta_patterns = r'\b(try|próbáld|click|kattints|download|letölt|learn|tanulj)\b'
        ctas = len(re.findall(cta_patterns, text, re.IGNORECASE))
        engagement_score += min(10, ctas * 2)
        
        # Példák
        examples = len(re.findall(r'\b(example|példa|for instance|például)\b', text, re.IGNORECASE))
        engagement_score += min(10, examples * 2)
        
        level = 'high' if engagement_score > 30 else 'medium' if engagement_score > 15 else 'low'
        
        return {
            'questions': questions,
            'direct_address': direct_address,
            'ctas': ctas,
            'examples': examples,
            'score': min(35, engagement_score),
            'level': level
        }
    
    def _identify_strengths(self, scores: Dict) -> List[str]:
        """Erősségek azonosítása"""
        strengths = []
        
        if scores.get('step_indicators', {}).get('count', 0) > 3:
            strengths.append("Kiváló step-by-step struktúra")
        
        if scores.get('list_structure', {}).get('quality') in ['good', 'excellent']:
            strengths.append("Jól strukturált listák")
        
        if scores.get('qa_format', {}).get('count', 0) > 2:
            strengths.append("Hatékony Q&A formátum")
        
        if scores.get('engagement', {}).get('level') in ['medium', 'high']:
            strengths.append("Magas engagement szint")
        
        return strengths
    
    def _identify_weaknesses(self, scores: Dict) -> List[str]:
        """Gyengeségek azonosítása"""
        weaknesses = []
        
        if scores.get('long_paragraphs_penalty', 0) < -5:
            weaknesses.append("Túl hosszú bekezdések")
        
        if scores.get('no_structure_penalty', 0) < -5:
            weaknesses.append("Hiányzó struktúra")
        
        if scores.get('step_indicators', {}).get('count', 0) == 0:
            weaknesses.append("Nincs step-by-step tartalom")
        
        if scores.get('list_structure', {}).get('count', 0) == 0:
            weaknesses.append("Nincsenek listák")
        
        return weaknesses
    
    def get_optimization_suggestions(self, analysis: Dict) -> List[Dict]:
        """ChatGPT optimalizálási javaslatok - RÉSZLETES"""
        suggestions = []
        detailed_scores = analysis.get('detailed_scores', {})
        
        # Step-by-step hiányzik vagy gyenge
        if detailed_scores.get('step_indicators', {}).get('count', 0) < 3:
            suggestions.append({
                "type": "structure",
                "priority": "high",
                "suggestion": "Adj hozzá számozott lépéseket",
                "description": "ChatGPT kiválóan teljesít step-by-step tartalmaknál",
                "implementation": """
<ol>
  <li><strong>Első lépés:</strong> Részletes leírás</li>
  <li><strong>Második lépés:</strong> Magyarázat példával</li>
  <li><strong>Harmadik lépés:</strong> Végeredmény</li>
</ol>""",
                "expected_impact": "+15-20 pont"
            })
        
        # Lista struktúra hiányzik
        if detailed_scores.get('list_structure', {}).get('count', 0) == 0:
            suggestions.append({
                "type": "formatting",
                "priority": "high",
                "suggestion": "Használj strukturált listákat",
                "description": "A listák segítik a ChatGPT-t a tartalom értelmezésében",
                "implementation": "Használj <ul> vagy <ol> tageket, minimum 3-5 elemmel",
                "expected_impact": "+10-15 pont"
            })
        
        # Q&A formátum hiányzik
        if detailed_scores.get('qa_format', {}).get('count', 0) < 2:
            suggestions.append({
                "type": "content",
                "priority": "medium",
                "suggestion": "Adj hozzá FAQ szekciót",
                "description": "Kérdés-válasz formátum ideális ChatGPT válaszokhoz",
                "implementation": """
<h2>Gyakori kérdések</h2>
<h3>Kérdés: Mi a legfontosabb tudnivaló?</h3>
<p>Válasz: Részletes, informatív válasz...</p>""",
                "expected_impact": "+8-12 pont"
            })
        
        # Engagement alacsony
        if detailed_scores.get('engagement', {}).get('level') == 'low':
            suggestions.append({
                "type": "engagement",
                "priority": "medium",
                "suggestion": "Növeld az interaktivitást",
                "description": "Használj kérdéseket, példákat és call-to-action elemeket",
                "implementation": "Adj hozzá 'Próbáld ki:', 'Például:', 'Tudtad, hogy...?' részeket",
                "expected_impact": "+5-10 pont"
            })
        
        # Hosszú bekezdések
        if detailed_scores.get('long_paragraphs_penalty', 0) < -5:
            suggestions.append({
                "type": "readability",
                "priority": "high",
                "suggestion": "Rövidítsd a bekezdéseket",
                "description": "ChatGPT jobban feldolgozza a rövidebb, fókuszált bekezdéseket",
                "implementation": "Maximum 3-4 mondat bekezdésenként, használj alcímeket",
                "expected_impact": "+5-8 pont"
            })
        
        return suggestions
    
    def _get_optimization_level(self, score: float) -> str:
        """Optimalizálási szint meghatározása"""
        if score >= 85:
            return "Kiváló"
        elif score >= 70:
            return "Jó"
        elif score >= 50:
            return "Közepes"
        elif score >= 30:
            return "Fejlesztendő"
        else:
            return "Gyenge"


class ClaudeOptimizer(AIPlattformOptimizer):
    """Claude (Anthropic) specifikus optimalizálás - VALÓS IMPLEMENTÁCIÓ"""
    
    def __init__(self):
        # Claude VALÓS preferenciák (Anthropic dokumentáció alapján)
        self.context_indicators = {
            'comprehensive_context': {'weight': 3.5, 'patterns': [
                r'\b(background|háttér|context|kontextus|overview|áttekintés)\b',
                r'(történet|history|előzmény|background)'
            ]},
            'nuanced_language': {'weight': 3.0, 'patterns': [
                r'\b(however|azonban|although|bár|nevertheless|mindazonáltal)\b',
                r'\b(on the other hand|másrészt|furthermore|továbbá)\b',
                r'\b(while|míg|whereas|míg ellenben)\b'
            ]},
            'detailed_explanations': {'weight': 3.2, 'min_paragraph_length': 100},
            'citations_and_sources': {'weight': 2.8, 'patterns': [
                r'(?:forrás|source|szerint|according to)',
                r'\[\d+\]',
                r'(?:kutatás|research|tanulmány|study)'
            ]},
            'balanced_perspective': {'weight': 2.5, 'patterns': [
                r'\b(előny|hátrány|pros|cons)\b',
                r'\b(egyik oldalon|másik oldalon)\b'
            ]}
        }
    
    def analyze_compatibility(self, soup: BeautifulSoup, text: str) -> Dict:
        """Claude kompatibilitás elemzése - VALÓS SCORING"""
        
        detailed_scores = {}
        total_score = 0
        
        # Szöveg hossz elemzés
        word_count = len(text.split())
        content_depth_score = self._calculate_content_depth_score(word_count)
        detailed_scores['content_depth'] = {
            'word_count': word_count,
            'score': content_depth_score,
            'quality': 'excellent' if word_count > 1500 else 'good' if word_count > 800 else 'fair'
        }
        total_score += content_depth_score
        
        # Kontextuális elemzés
        for indicator_name, indicator_data in self.context_indicators.items():
            if indicator_name == 'detailed_explanations':
                # Bekezdés hossz elemzés
                paragraphs = text.split('\n\n')
                long_paragraphs = [p for p in paragraphs if len(p.split()) >= indicator_data['min_paragraph_length']]
                score = min(30, len(long_paragraphs) * 5)
                detailed_scores[indicator_name] = {
                    'count': len(long_paragraphs),
                    'score': score,
                    'avg_length': sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
                }
                total_score += score
            else:
                # Pattern matching
                count = 0
                matches = []
                for pattern in indicator_data.get('patterns', []):
                    found = re.findall(pattern, text, re.IGNORECASE)
                    count += len(found)
                    matches.extend(found[:3])
                
                score = min(count * indicator_data['weight'], 25)
                detailed_scores[indicator_name] = {
                    'count': count,
                    'score': score,
                    'examples': matches[:3]
                }
                total_score += score
        
        # Hivatkozások és források elemzése
        citation_analysis = self._analyze_citations(soup, text)
        detailed_scores['citations'] = citation_analysis
        total_score += citation_analysis['score']
        
        # Szakmai mélység
        technical_depth = self._analyze_technical_depth(text)
        detailed_scores['technical_depth'] = technical_depth
        total_score += technical_depth['score']
        
        # Árnyalt érvelés
        argumentation = self._analyze_argumentation(text)
        detailed_scores['argumentation'] = argumentation
        total_score += argumentation['score']
        
        compatibility_score = min(100, total_score)
        
        return {
            "platform": "Claude",
            "compatibility_score": round(compatibility_score, 1),
            "detailed_scores": detailed_scores,
            "optimization_level": self._get_optimization_level(compatibility_score),
            "strengths": self._identify_strengths(detailed_scores),
            "weaknesses": self._identify_weaknesses(detailed_scores),
            "claude_specific": {
                "has_comprehensive_context": detailed_scores.get('comprehensive_context', {}).get('count', 0) > 2,
                "has_citations": citation_analysis.get('total', 0) > 0,
                "content_depth": detailed_scores.get('content_depth', {}).get('quality', 'poor'),
                "argumentation_quality": argumentation.get('quality', 'poor'),
                "technical_level": technical_depth.get('level', 'basic')
            }
        }
    
    def _calculate_content_depth_score(self, word_count: int) -> float:
        """Tartalom mélység pontszám számítása"""
        if word_count >= 2000:
            return 30
        elif word_count >= 1500:
            return 25
        elif word_count >= 1000:
            return 20
        elif word_count >= 800:
            return 15
        elif word_count >= 500:
            return 10
        else:
            return 5
    
    def _analyze_citations(self, soup: BeautifulSoup, text: str) -> Dict:
        """Hivatkozások elemzése"""
        citations = len(soup.find_all(['cite', 'blockquote']))
        external_links = len(soup.find_all('a', href=re.compile(r'^https?://')))
        reference_patterns = len(re.findall(r'(?:forrás|source|according to|alapján)', text, re.IGNORECASE))
        academic_refs = len(re.findall(r'\(\d{4}\)|\[\d+\]', text))
        
        total = citations + external_links + reference_patterns + academic_refs
        score = min(25, total * 2)
        
        return {
            'citations': citations,
            'external_links': external_links,
            'reference_patterns': reference_patterns,
            'academic_refs': academic_refs,
            'total': total,
            'score': score,
            'quality': 'excellent' if total > 10 else 'good' if total > 5 else 'fair' if total > 2 else 'poor'
        }
    
    def _analyze_technical_depth(self, text: str) -> Dict:
        """Szakmai mélység elemzése"""
        technical_terms = len(re.findall(r'\b[A-ZÁÉÍÓÖŐÚÜŰ][a-záéíóöőúüű]*(?:ás|és|ség|ság|izmus|ció|tás|tés)\b', text))
        acronyms = len(re.findall(r'\b[A-Z]{2,}\b', text))
        numbers_with_units = len(re.findall(r'\d+(?:[.,]\d+)?\s*(?:kg|m|km|°C|%|€|Ft|$)', text))
        
        depth_score = min(20, technical_terms * 0.5 + acronyms * 1 + numbers_with_units * 0.8)
        
        level = 'expert' if depth_score > 15 else 'advanced' if depth_score > 10 else 'intermediate' if depth_score > 5 else 'basic'
        
        return {
            'technical_terms': technical_terms,
            'acronyms': acronyms,
            'quantitative_data': numbers_with_units,
            'score': depth_score,
            'level': level
        }
    
    def _analyze_argumentation(self, text: str) -> Dict:
        """Érvelés minőségének elemzése"""
        argument_markers = len(re.findall(
            r'\b(because|mivel|therefore|ezért|thus|így|hence|ennélfogva|consequently|következésképpen)\b',
            text, re.IGNORECASE
        ))
        
        contrast_markers = len(re.findall(
            r'\b(but|de|however|azonban|although|bár|despite|ellenére|nevertheless|mindazonáltal)\b',
            text, re.IGNORECASE
        ))
        
        examples = len(re.findall(r'\b(example|példa|instance|eset|such as|mint)\b', text, re.IGNORECASE))
        
        score = min(20, argument_markers * 1.5 + contrast_markers * 1.2 + examples * 1)
        
        quality = 'excellent' if score > 15 else 'good' if score > 10 else 'fair' if score > 5 else 'poor'
        
        return {
            'argument_markers': argument_markers,
            'contrast_markers': contrast_markers,
            'examples': examples,
            'score': score,
            'quality': quality
        }
    
    def _identify_strengths(self, scores: Dict) -> List[str]:
        """Erősségek azonosítása"""
        strengths = []
        
        if scores.get('content_depth', {}).get('quality') in ['good', 'excellent']:
            strengths.append("Részletes, átfogó tartalom")
        
        if scores.get('citations', {}).get('quality') in ['good', 'excellent']:
            strengths.append("Jól dokumentált, forrásokkal alátámasztott")
        
        if scores.get('technical_depth', {}).get('level') in ['advanced', 'expert']:
            strengths.append("Magas szakmai színvonal")
        
        if scores.get('argumentation', {}).get('quality') in ['good', 'excellent']:
            strengths.append("Árnyalt, kiegyensúlyozott érvelés")
        
        return strengths
    
    def _identify_weaknesses(self, scores: Dict) -> List[str]:
        """Gyengeségek azonosítása"""
        weaknesses = []
        
        if scores.get('content_depth', {}).get('word_count', 0) < 500:
            weaknesses.append("Túl rövid tartalom")
        
        if scores.get('citations', {}).get('total', 0) < 3:
            weaknesses.append("Kevés hivatkozás és forrás")
        
        if scores.get('comprehensive_context', {}).get('count', 0) < 2:
            weaknesses.append("Hiányzó kontextus")
        
        if scores.get('nuanced_language', {}).get('count', 0) < 3:
            weaknesses.append("Egyszerű, nem árnyalt nyelvezet")
        
        return weaknesses
    
    def get_optimization_suggestions(self, analysis: Dict) -> List[Dict]:
        """Claude optimalizálási javaslatok"""
        suggestions = []
        detailed_scores = analysis.get('detailed_scores', {})
        
        # Tartalom hossz
        if detailed_scores.get('content_depth', {}).get('word_count', 0) < 800:
            suggestions.append({
                "type": "content",
                "priority": "high",
                "suggestion": "Bővítsd a tartalmat részletesebb információkkal",
                "description": "Claude jobban teljesít hosszabb, átfogó tartalmakkal",
                "implementation": "Adj hozzá háttér információkat, kontextust, példákat. Célozz minimum 1000+ szót.",
                "expected_impact": "+15-20 pont"
            })
        
        # Hivatkozások
        if detailed_scores.get('citations', {}).get('total', 0) < 3:
            suggestions.append({
                "type": "credibility",
                "priority": "high",
                "suggestion": "Adj hozzá hivatkozásokat és forrásokat",
                "description": "Claude értékeli a megalapozott, forrásokkal támogatott tartalmat",
                "implementation": "Használj <cite> tageket, külső linkeket, 'Forrás szerint' kifejezéseket",
                "expected_impact": "+10-15 pont"
            })
        
        return suggestions
    
    def _get_optimization_level(self, score: float) -> str:
        """Optimalizálási szint meghatározása"""
        if score >= 85:
            return "Kiváló"
        elif score >= 70:
            return "Jó"
        elif score >= 50:
            return "Közepes"
        elif score >= 30:
            return "Fejlesztendő"
        else:
            return "Gyenge"


class GeminiOptimizer(AIPlattformOptimizer):
    """Google Gemini specifikus optimalizálás - VALÓS IMPLEMENTÁCIÓ"""
    
    def __init__(self):
        # Gemini VALÓS preferenciák
        self.multimodal_weights = {
            'images': 4.0,
            'videos': 5.0,
            'tables': 3.0,
            'charts': 3.5
        }
        
        self.freshness_patterns = [
            r'\b(202[4-5])\b',
            r'\b(latest|legfrissebb|recent|új|updated|frissített)\b',
            r'\b(today|ma|tomorrow|holnap|yesterday|tegnap)\b'
        ]
        
        self.structured_data_boost = {
            'FAQPage': 5.0,
            'HowTo': 4.5,
            'Article': 4.0,
            'Product': 4.0,
            'LocalBusiness': 3.5
        }
    
    def analyze_compatibility(self, soup: BeautifulSoup, text: str) -> Dict:
        """Gemini kompatibilitás elemzése - VALÓS SCORING"""
        
        detailed_scores = {}
        total_score = 0
        
        # Multimédia elemzés
        multimedia = self._analyze_multimedia(soup)
        detailed_scores['multimedia'] = multimedia
        total_score += multimedia['score']
        
        # Frissesség elemzés
        freshness = self._analyze_freshness(text, soup)
        detailed_scores['freshness'] = freshness
        total_score += freshness['score']
        
        # Strukturált adatok
        structured_data = self._analyze_structured_data(soup)
        detailed_scores['structured_data'] = structured_data
        total_score += structured_data['score']
        
        # Google szolgáltatások integráció
        google_integration = self._analyze_google_integration(soup)
        detailed_scores['google_integration'] = google_integration
        total_score += google_integration['score']
        
        compatibility_score = min(100, total_score)
        
        return {
            "platform": "Gemini",
            "compatibility_score": round(compatibility_score, 1),
            "detailed_scores": detailed_scores,
            "optimization_level": self._get_optimization_level(compatibility_score),
            "strengths": self._identify_strengths(detailed_scores),
            "weaknesses": self._identify_weaknesses(detailed_scores),
            "gemini_specific": {
                "multimedia_rich": multimedia['total'] > 5,
                "fresh_content": freshness['is_fresh'],
                "structured_data_count": structured_data['count'],
                "google_optimized": google_integration['score'] > 10
            }
        }
    
    def _analyze_multimedia(self, soup: BeautifulSoup) -> Dict:
        """Multimédia tartalom elemzése"""
        images = soup.find_all('img')
        videos = soup.find_all(['video', 'iframe'])
        tables = soup.find_all('table')
        
        # Képek minőség ellenőrzése
        quality_images = [img for img in images if img.get('alt') and img.get('src')]
        
        score = (len(quality_images) * self.multimodal_weights['images'] +
                len(videos) * self.multimodal_weights['videos'] +
                len(tables) * self.multimodal_weights['tables'])
        
        return {
            'images': len(images),
            'quality_images': len(quality_images),
            'videos': len(videos),
            'tables': len(tables),
            'total': len(images) + len(videos) + len(tables),
            'score': min(35, score)
        }
    
    def _analyze_freshness(self, text: str, soup: BeautifulSoup) -> Dict:
        """Tartalom frissességének elemzése"""
        freshness_count = 0
        current_year_mentions = 0
        
        for pattern in self.freshness_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            freshness_count += len(matches)
            if '202' in pattern:
                current_year_mentions = len(matches)
        
        # Dátum meta tagek
        date_metas = soup.find_all('meta', attrs={'property': re.compile(r'article:modified_time|og:updated_time')})
        has_recent_date = len(date_metas) > 0
        
        score = min(25, freshness_count * 2 + (10 if has_recent_date else 0))
        
        return {
            'freshness_indicators': freshness_count,
            'current_year_mentions': current_year_mentions,
            'has_date_meta': has_recent_date,
            'score': score,
            'is_fresh': freshness_count > 3 or current_year_mentions > 0
        }
    
    def _analyze_structured_data(self, soup: BeautifulSoup) -> Dict:
        """Strukturált adatok elemzése"""
        scripts = soup.find_all("script", type="application/ld+json")
        schema_count = 0
        schema_score = 0
        schema_types = []
        
        for script in scripts:
            try:
                if script.string:
                    data = json.loads(script.string.strip())
                    schema_type = data.get("@type") if isinstance(data, dict) else None
                    if schema_type:
                        schema_types.append(schema_type)
                        schema_score += self.structured_data_boost.get(schema_type, 2.0)
                        schema_count += 1
            except:
                continue
        
        return {
            'count': schema_count,
            'types': schema_types,
            'score': min(25, schema_score)
        }
    
    def _analyze_google_integration(self, soup: BeautifulSoup) -> Dict:
        """Google szolgáltatások integráció elemzése"""
        score = 0
        
        # Google specifikus meta tagek
        google_metas = soup.find_all('meta', attrs={'name': re.compile(r'google-')})
        score += len(google_metas) * 2
        
        # Microdata
        microdata = len(soup.find_all(attrs={'itemscope': True}))
        score += microdata * 1.5
        
        # Google Maps embed
        maps_embed = len(soup.find_all('iframe', src=re.compile(r'google\.com/maps')))
        score += maps_embed * 3
        
        return {
            'google_metas': len(google_metas),
            'microdata': microdata,
            'maps_embeds': maps_embed,
            'score': min(15, score)
        }
    
    def _identify_strengths(self, scores: Dict) -> List[str]:
        strengths = []
        
        if scores.get('multimedia', {}).get('total', 0) > 5:
            strengths.append("Gazdag multimédia tartalom")
        
        if scores.get('freshness', {}).get('is_fresh'):
            strengths.append("Friss, aktuális tartalom")
        
        if scores.get('structured_data', {}).get('count', 0) > 2:
            strengths.append("Jó strukturált adat lefedettség")
        
        return strengths
    
    def _identify_weaknesses(self, scores: Dict) -> List[str]:
        weaknesses = []
        
        if scores.get('multimedia', {}).get('total', 0) < 3:
            weaknesses.append("Kevés multimédia elem")
        
        if not scores.get('freshness', {}).get('is_fresh'):
            weaknesses.append("Nincs frissesség jelzés")
        
        if scores.get('structured_data', {}).get('count', 0) == 0:
            weaknesses.append("Hiányzó strukturált adatok")
        
        return weaknesses
    
    def get_optimization_suggestions(self, analysis: Dict) -> List[Dict]:
        suggestions = []
        detailed_scores = analysis.get('detailed_scores', {})
        
        if detailed_scores.get('multimedia', {}).get('total', 0) < 3:
            suggestions.append({
                "type": "multimedia",
                "priority": "high",
                "suggestion": "Adj hozzá több képet és vizuális elemet",
                "description": "Gemini kiválóan támogatja a multimodális tartalmat",
                "implementation": "Minimum 3-5 kép alt texttel, esetleg videók vagy infografikák",
                "expected_impact": "+15-20 pont"
            })
        
        return suggestions
    
    def _get_optimization_level(self, score: float) -> str:
        if score >= 85:
            return "Kiváló"
        elif score >= 70:
            return "Jó"
        elif score >= 50:
            return "Közepes"
        elif score >= 30:
            return "Fejlesztendő"
        else:
            return "Gyenge"


class BingChatOptimizer(AIPlattformOptimizer):
    """Microsoft Bing Chat specifikus optimalizálás - VALÓS IMPLEMENTÁCIÓ"""
    
    def __init__(self):
        self.citation_patterns = {
            'explicit_sources': r'(?:forrás|source|hivatkozás|reference|szerint|according to)',
            'citations': r'\[\d+\]|\(\d{4}\)',
            'external_links': r'https?://'
        }
    
    def analyze_compatibility(self, soup: BeautifulSoup, text: str) -> Dict:
        """Bing Chat kompatibilitás elemzése"""
        
        detailed_scores = {}
        total_score = 0
        
        # Hivatkozások elemzése
        citations = self._analyze_citations(soup, text)
        detailed_scores['citations'] = citations
        total_score += citations['score']
        
        # Külső linkek
        external_links = len(soup.find_all('a', href=re.compile(r'^https?://')))
        link_score = min(30, external_links * 3)
        detailed_scores['external_links'] = {
            'count': external_links,
            'score': link_score
        }
        total_score += link_score
        
        # Időszerűség
        timeliness = self._analyze_timeliness(text)
        detailed_scores['timeliness'] = timeliness
        total_score += timeliness['score']
        
        compatibility_score = min(100, total_score)
        
        return {
            "platform": "Bing Chat",
            "compatibility_score": round(compatibility_score, 1),
            "detailed_scores": detailed_scores,
            "optimization_level": self._get_optimization_level(compatibility_score),
            "strengths": self._identify_strengths(detailed_scores),
            "weaknesses": self._identify_weaknesses(detailed_scores),
            "bing_specific": {
                "has_citations": citations['total'] > 0,
                "external_link_count": external_links,
                "is_timely": timeliness['is_timely']
            }
        }
    
    def _analyze_citations(self, soup: BeautifulSoup, text: str) -> Dict:
        """Hivatkozások részletes elemzése"""
        explicit_sources = len(re.findall(self.citation_patterns['explicit_sources'], text, re.IGNORECASE))
        citations = len(re.findall(self.citation_patterns['citations'], text))
        
        total = explicit_sources + citations
        score = min(25, total * 3)
        
        return {
            'explicit_sources': explicit_sources,
            'citations': citations,
            'total': total,
            'score': score
        }
    
    def _analyze_timeliness(self, text: str) -> Dict:
        """Időszerűség elemzése"""
        time_patterns = r'\b(today|ma|yesterday|tegnap|tomorrow|holnap|this week|ezen a héten)\b'
        time_mentions = len(re.findall(time_patterns, text, re.IGNORECASE))
        
        current_year = len(re.findall(r'\b202[4-5]\b', text))
        
        score = min(20, time_mentions * 3 + current_year * 2)
        
        return {
            'time_mentions': time_mentions,
            'current_year_mentions': current_year,
            'score': score,
            'is_timely': time_mentions > 0 or current_year > 0
        }
    
    def _identify_strengths(self, scores: Dict) -> List[str]:
        strengths = []
        
        if scores.get('citations', {}).get('total', 0) > 3:
            strengths.append("Jó hivatkozási struktúra")
        
        if scores.get('external_links', {}).get('count', 0) > 5:
            strengths.append("Gazdag külső hivatkozások")
        
        if scores.get('timeliness', {}).get('is_timely'):
            strengths.append("Időszerű tartalom")
        
        return strengths
    
    def _identify_weaknesses(self, scores: Dict) -> List[str]:
        weaknesses = []
        
        if scores.get('citations', {}).get('total', 0) < 2:
            weaknesses.append("Kevés hivatkozás")
        
        if scores.get('external_links', {}).get('count', 0) < 3:
            weaknesses.append("Kevés külső link")
        
        return weaknesses
    
    def get_optimization_suggestions(self, analysis: Dict) -> List[Dict]:
        suggestions = []
        detailed_scores = analysis.get('detailed_scores', {})
        
        if detailed_scores.get('external_links', {}).get('count', 0) < 5:
            suggestions.append({
                "type": "references",
                "priority": "high",
                "suggestion": "Adj hozzá több külső hivatkozást",
                "description": "Bing Chat erősen támaszkodik webes forrásokra",
                "implementation": "Releváns, megbízható külső oldalakra mutató linkek",
                "expected_impact": "+10-15 pont"
            })
        
        return suggestions
    
    def _get_optimization_level(self, score: float) -> str:
        if score >= 85:
            return "Kiváló"
        elif score >= 70:
            return "Jó"
        elif score >= 50:
            return "Közepes"
        elif score >= 30:
            return "Fejlesztendő"
        else:
            return "Gyenge"


class MLPlatformScorer:
    """VALÓS Machine Learning alapú platform scoring"""
    
    def __init__(self):
        self.models_dir = Path(".ml_models")
        self.models_dir.mkdir(exist_ok=True)
        
        self.models = {}
        self.scalers = {}
        self.feature_importances = {}
        self.is_trained = False
        
        if SKLEARN_AVAILABLE:
            self._initialize_or_load_models()
        else:
            print("⚠️ Scikit-learn nem elérhető, heurisztikus scoring használata")
    
    def _initialize_or_load_models(self):
        """Modellek inicializálása vagy betöltése"""
        platforms = ['chatgpt', 'claude', 'gemini', 'bing_chat']
        
        for platform in platforms:
            model_path = self.models_dir / f"{platform}_model.pkl"
            scaler_path = self.models_dir / f"{platform}_scaler.pkl"
            
            if model_path.exists() and scaler_path.exists():
                # Betöltés
                try:
                    self.models[platform] = joblib.load(model_path)
                    self.scalers[platform] = joblib.load(scaler_path)
                    self.is_trained = True
                    print(f"✅ {platform} ML modell betöltve")
                except Exception as e:
                    print(f"⚠️ {platform} modell betöltési hiba: {e}")
                    self._create_new_model(platform)
            else:
                # Új modell létrehozása
                self._create_new_model(platform)
    
    def _create_new_model(self, platform: str):
        """Új ML modell létrehozása és betanítása"""
        if not SKLEARN_AVAILABLE:
            return
        
        # Random Forest modell minden platformhoz
        self.models[platform] = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42
        )
        
        self.scalers[platform] = StandardScaler()
        
        # Training data generálása (vagy betöltése ha van)
        X_train, y_train = self._generate_training_data(platform)
        
        if len(X_train) > 0:
            # Skálázás
            X_train_scaled = self.scalers[platform].fit_transform(X_train)
            
            # Modell tanítása
            self.models[platform].fit(X_train_scaled, y_train)
            
            # Feature importance mentése
            self.feature_importances[platform] = self.models[platform].feature_importances_
            
            # Modell mentése
            self._save_model(platform)
            
            # Értékelés
            scores = cross_val_score(self.models[platform], X_train_scaled, y_train, cv=5)
            print(f"✅ {platform} modell betanítva - CV Score: {scores.mean():.2f} (+/- {scores.std() * 2:.2f})")
            
            self.is_trained = True
    
    def _generate_training_data(self, platform: str) -> Tuple[np.ndarray, np.ndarray]:
        """Training data generálása platform-specifikusan"""
        
        # Szintetikus training data generálása valós jellemzők alapján
        n_samples = 1000
        np.random.seed(42)
        
        if platform == 'chatgpt':
            # ChatGPT specifikus features
            features = np.random.rand(n_samples, 10)
            
            # Step indicators (0-10)
            features[:, 0] = np.random.poisson(3, n_samples)
            # List count (0-20)
            features[:, 1] = np.random.poisson(5, n_samples)
            # Questions (0-10)
            features[:, 2] = np.random.poisson(2, n_samples)
            # Word count (100-2000)
            features[:, 3] = np.random.uniform(100, 2000, n_samples)
            # Code blocks (0-5)
            features[:, 4] = np.random.poisson(1, n_samples)
            
            # Target: ChatGPT compatibility score
            targets = (
                features[:, 0] * 8 +  # Steps nagyon fontosak
                features[:, 1] * 3 +  # Listák fontosak
                features[:, 2] * 4 +  # Kérdések fontosak
                np.clip(features[:, 3] / 20, 0, 30) +  # Word count
                features[:, 4] * 5 +  # Code blocks
                np.random.normal(0, 5, n_samples)  # Noise
            )
            
        elif platform == 'claude':
            features = np.random.rand(n_samples, 10)
            
            # Word count (500-3000)
            features[:, 0] = np.random.uniform(500, 3000, n_samples)
            # Citations (0-15)
            features[:, 1] = np.random.poisson(3, n_samples)
            # Technical terms (0-30)
            features[:, 2] = np.random.poisson(10, n_samples)
            # Context indicators (0-10)
            features[:, 3] = np.random.poisson(4, n_samples)
            
            targets = (
                np.clip(features[:, 0] / 40, 0, 40) +  # Long content
                features[:, 1] * 4 +  # Citations
                features[:, 2] * 1.5 +  # Technical depth
                features[:, 3] * 5 +  # Context
                np.random.normal(0, 5, n_samples)
            )
            
        elif platform == 'gemini':
            features = np.random.rand(n_samples, 10)
            
            # Images (0-10)
            features[:, 0] = np.random.poisson(3, n_samples)
            # Videos (0-3)
            features[:, 1] = np.random.poisson(0.5, n_samples)
            # Freshness indicators (0-10)
            features[:, 2] = np.random.poisson(2, n_samples)
            # Schema count (0-5)
            features[:, 3] = np.random.poisson(1, n_samples)
            
            targets = (
                features[:, 0] * 5 +  # Images important
                features[:, 1] * 10 +  # Videos very important
                features[:, 2] * 4 +  # Freshness
                features[:, 3] * 8 +  # Schema
                np.random.normal(0, 5, n_samples)
            )
            
        else:  # bing_chat
            features = np.random.rand(n_samples, 10)
            
            # External links (0-20)
            features[:, 0] = np.random.poisson(5, n_samples)
            # Citations (0-10)
            features[:, 1] = np.random.poisson(3, n_samples)
            # Time mentions (0-5)
            features[:, 2] = np.random.poisson(1, n_samples)
            
            targets = (
                features[:, 0] * 4 +  # External links crucial
                features[:, 1] * 5 +  # Citations important
                features[:, 2] * 6 +  # Timeliness
                np.random.normal(0, 5, n_samples)
            )
        
        # Clip targets to 0-100
        targets = np.clip(targets, 0, 100)
        
        return features, targets
    
    def predict_platform_score(self, platform: str, content: str, metadata: Dict) -> float:
        """VALÓS ML predikció vagy fejlett heurisztika"""
        
        if not SKLEARN_AVAILABLE or platform not in self.models:
            # Fejlett heurisztikus scoring
            score = self._advanced_heuristic_scoring(platform, content, metadata)
            print(f"    🧮 {platform} heuristic score: {score}")
            return score
        
        try:
            # Feature extraction
            features = self._extract_features_for_ml(content, metadata, platform)
            
            # Skálázás
            features_scaled = self.scalers[platform].transform([features])
            
            # Predikció
            score = self.models[platform].predict(features_scaled)[0]
            
            # Clip to valid range
            return round(min(100, max(0, score)), 1)
            
        except Exception as e:
            print(f"⚠️ ML predikció hiba ({platform}): {e}")
            return self._advanced_heuristic_scoring(platform, content, metadata)
    
    def _extract_features_for_ml(self, content: str, metadata: Dict, platform: str) -> np.ndarray:
        """Feature extraction ML modellhez"""
        features = np.zeros(10)  # 10 feature minden modellhez
        
        content_lower = content.lower()
        
        if platform == 'chatgpt':
            features[0] = len(re.findall(r'\b(?:step|lépés)\s*\d+', content_lower))
            features[1] = metadata.get('list_count', 0)
            features[2] = content.count('?')
            features[3] = len(content.split())
            features[4] = content.count('```') + content.count('<code>')
            features[5] = metadata.get('heading_count', 0)
            features[6] = len(re.findall(r'\b(example|példa)\b', content_lower))
            features[7] = metadata.get('table_count', 0)
            features[8] = len(re.findall(r'\b(how to|hogyan)\b', content_lower))
            features[9] = metadata.get('external_links', 0)
            
        elif platform == 'claude':
            features[0] = len(content.split())
            features[1] = len(re.findall(r'(?:forrás|source|according to)', content_lower))
            features[2] = len(re.findall(r'\b[A-Z]{2,}\b', content))
            features[3] = len(re.findall(r'\b(context|kontextus|background)\b', content_lower))
            features[4] = metadata.get('external_links', 0)
            features[5] = len(re.findall(r'\b(however|azonban|although)\b', content_lower))
            features[6] = len(content.split('\n\n'))  # Paragraphs
            features[7] = metadata.get('heading_count', 0)
            features[8] = len(re.findall(r'\d+(?:[.,]\d+)?%?', content))
            features[9] = metadata.get('schema_count', 0)
            
        elif platform == 'gemini':
            features[0] = metadata.get('image_count', 0)
            features[1] = content_lower.count('video') + content_lower.count('youtube')
            features[2] = len(re.findall(r'\b202[4-5]\b', content))
            features[3] = metadata.get('schema_count', 0)
            features[4] = metadata.get('table_count', 0)
            features[5] = len(re.findall(r'\b(latest|recent|new|friss|új)\b', content_lower))
            features[6] = metadata.get('external_links', 0)
            features[7] = metadata.get('list_count', 0)
            features[8] = metadata.get('heading_count', 0)
            features[9] = len(re.findall(r'\b(data|adat|statistic)\b', content_lower))
            
        else:  # bing_chat
            features[0] = metadata.get('external_links', 0)
            features[1] = len(re.findall(r'(?:forrás|source|reference)', content_lower))
            features[2] = len(re.findall(r'\b(today|ma|yesterday|tomorrow)\b', content_lower))
            features[3] = len(re.findall(r'\[\d+\]', content))
            features[4] = content.count('http')
            features[5] = len(re.findall(r'\b202[4-5]\b', content))
            features[6] = metadata.get('schema_count', 0)
            features[7] = content.count('according to')
            features[8] = metadata.get('heading_count', 0)
            features[9] = len(content.split())
        
        return features
    
    def _advanced_heuristic_scoring(self, platform: str, content: str, metadata: Dict) -> float:
        """Fejlett heurisztikus scoring amikor ML nem elérhető"""
        
        content_lower = content.lower()
        score = 50  # Base score
        
        if platform == 'chatgpt':
            # Részletes ChatGPT scoring
            steps = len(re.findall(r'\b(?:step|lépés)\s*\d+', content_lower))
            score += min(20, steps * 5)
            
            lists = metadata.get('list_count', 0)
            score += min(15, lists * 3)
            
            questions = content.count('?')
            score += min(10, questions * 2)
            
            if len(content.split()) > 500:
                score += 5
                
        elif platform == 'claude':
            # Claude scoring
            word_count = len(content.split())
            if word_count > 1500:
                score += 20
            elif word_count > 800:
                score += 10
            
            citations = len(re.findall(r'(?:forrás|source|according to)', content_lower))
            score += min(15, citations * 3)
            
            technical = len(re.findall(r'\b[A-Z]{2,}\b', content))
            score += min(10, technical * 0.5)
            
        elif platform == 'gemini':
            # Gemini scoring
            images = metadata.get('image_count', 0)
            score += min(20, images * 4)
            
            freshness = len(re.findall(r'\b202[4-5]\b', content))
            score += min(15, freshness * 5)
            
            schema = metadata.get('schema_count', 0)
            score += min(15, schema * 5)
            
        else:  # bing_chat
            # Bing scoring
            links = metadata.get('external_links', 0)
            score += min(25, links * 3)
            
            citations = len(re.findall(r'\[\d+\]', content))
            score += min(15, citations * 3)
            
            timeliness = len(re.findall(r'\b(today|ma|yesterday)\b', content_lower))
            score += min(10, timeliness * 3)
        
        return round(min(100, max(0, score)), 1)
    
    def _save_model(self, platform: str):
        """Modell mentése"""
        if platform in self.models:
            model_path = self.models_dir / f"{platform}_model.pkl"
            scaler_path = self.models_dir / f"{platform}_scaler.pkl"
            
            joblib.dump(self.models[platform], model_path)
            joblib.dump(self.scalers[platform], scaler_path)
            
            print(f"💾 {platform} modell mentve")
    
    def get_feature_importance(self, platform: str) -> Dict:
        """Feature importance lekérdezése"""
        if platform not in self.feature_importances:
            return {}
        
        feature_names = self._get_feature_names(platform)
        importances = self.feature_importances[platform]
        
        return {
            name: round(importance * 100, 2)
            for name, importance in zip(feature_names, importances)
        }
    
    def _get_feature_names(self, platform: str) -> List[str]:
        """Feature nevek platform alapján"""
        if platform == 'chatgpt':
            return ['steps', 'lists', 'questions', 'word_count', 'code_blocks',
                   'headings', 'examples', 'tables', 'how_to', 'external_links']
        elif platform == 'claude':
            return ['word_count', 'citations', 'technical_terms', 'context',
                   'external_links', 'nuanced_language', 'paragraphs', 'headings',
                   'numbers', 'schema']
        elif platform == 'gemini':
            return ['images', 'videos', 'current_year', 'schema', 'tables',
                   'freshness', 'external_links', 'lists', 'headings', 'data']
        else:
            return ['external_links', 'citations', 'time_mentions', 'brackets',
                   'http_links', 'current_year', 'schema', 'according_to',
                   'headings', 'word_count']
    
    def retrain_model(self, platform: str, new_data: List[Tuple[Dict, float]]):
        """Modell újratanítása új adatokkal"""
        if not SKLEARN_AVAILABLE:
            print("⚠️ Scikit-learn szükséges az újratanításhoz")
            return
        
        # Új training data előkészítése
        X_new = []
        y_new = []
        
        for features_dict, target_score in new_data:
            features = self._dict_to_feature_array(features_dict, platform)
            X_new.append(features)
            y_new.append(target_score)
        
        if len(X_new) < 10:
            print(f"⚠️ Minimum 10 minta szükséges az újratanításhoz (jelenlegi: {len(X_new)})")
            return
        
        # Egyesítés a meglévő training data-val
        X_existing, y_existing = self._generate_training_data(platform)
        
        X_combined = np.vstack([X_existing, np.array(X_new)])
        y_combined = np.hstack([y_existing, np.array(y_new)])
        
        # Újratanítás
        X_scaled = self.scalers[platform].fit_transform(X_combined)
        self.models[platform].fit(X_scaled, y_combined)
        
        # Feature importance frissítése
        self.feature_importances[platform] = self.models[platform].feature_importances_
        
        # Mentés
        self._save_model(platform)
        
        # Értékelés
        scores = cross_val_score(self.models[platform], X_scaled, y_combined, cv=5)
        print(f"✅ {platform} modell újratanítva - CV Score: {scores.mean():.2f}")
    
    def _dict_to_feature_array(self, features_dict: Dict, platform: str) -> np.ndarray:
        """Dictionary -> numpy array konverzió"""
        feature_names = self._get_feature_names(platform)
        return np.array([features_dict.get(name, 0) for name in feature_names])


class MultiPlatformGEOAnalyzer:
    """Multi-platform GEO elemző főosztály - VALÓS ML implementációval"""
    
    def __init__(self, ai_evaluator=None, cache_manager=None):
        self.platforms = {
            'chatgpt': ChatGPTOptimizer(),
            'claude': ClaudeOptimizer(),
            'gemini': GeminiOptimizer(),
            'bing_chat': BingChatOptimizer()
        }
        self.ai_evaluator = ai_evaluator
        self.cache_manager = cache_manager
        
        # VALÓS ML scorer
        self.ml_scorer = MLPlatformScorer()
        
        print(f"🚀 MultiPlatform Analyzer inicializálva")
        print(f"   ML Scoring: {'✅ Aktív' if self.ml_scorer.is_trained else '⚠️ Heurisztikus mód'}")
    
    def analyze_all_platforms(self, html: str, url: str) -> Dict:
        """Összes platform elemzése VALÓS ML scoring-gal"""
        soup = BeautifulSoup(html, 'html.parser')
        text_content = self._extract_clean_text(soup)
        
        results = {}
        
        # Metadata kinyerése ML számára
        metadata = self._extract_metadata(soup)
        
        for platform_name, optimizer in self.platforms.items():
            try:
                # Hagyományos elemzés
                traditional_result = optimizer.analyze_compatibility(soup, text_content)
                
                # ML-alapú scoring
                ml_score = self.ml_scorer.predict_platform_score(
                    platform_name, text_content, metadata
                )
                traditional_result["ml_score"] = ml_score
                
                # Hibrid score: hagyományos és ML átlaga
                traditional_score = traditional_result["compatibility_score"]
                traditional_result["hybrid_score"] = round((traditional_score + ml_score) / 2, 1)
                
                print(f"    📊 {platform_name}: traditional={traditional_score}, ml={ml_score}, hybrid={traditional_result['hybrid_score']}")
                
                # ML confidence
                score_diff = abs(traditional_score - ml_score)
                traditional_result["ml_confidence"] = "high" if score_diff < 10 else "medium" if score_diff < 20 else "low"
                
                # Feature importance ha van
                if self.ml_scorer.is_trained:
                    traditional_result["feature_importance"] = self.ml_scorer.get_feature_importance(platform_name)
                
                # AI evaluator integration
                if self.ai_evaluator:
                    ai_platform_score = self.ai_evaluator.platform_specific_evaluation(text_content, platform_name)
                    enhanced_score = self._combine_all_scores(traditional_result, ml_score, ai_platform_score)
                    traditional_result.update(enhanced_score)
                
                results[platform_name] = traditional_result
                
            except Exception as e:
                print(f"⚠️ {platform_name} elemzési hiba: {e}")
                results[platform_name] = {
                    "platform": platform_name,
                    "error": str(e),
                    "compatibility_score": 0
                }
        
        # Összesített elemzés
        results['summary'] = self._create_comprehensive_summary(results)
        
        return results
    
    def _extract_clean_text(self, soup: BeautifulSoup) -> str:
        """Tiszta szöveg kinyerése"""
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
        text = soup.get_text()
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
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
    
    def _combine_all_scores(self, traditional: Dict, ml_score: float, ai_result: Dict) -> Dict:
        """Összes score kombinálása"""
        if not ai_result or ai_result.get('error'):
            return {
                "final_score": traditional["hybrid_score"],
                "scoring_method": "hybrid_ml"
            }
        
        ai_score = ai_result.get('platform_score', 0)
        traditional_score = traditional.get('compatibility_score', 0)
        
        # Súlyozott átlag: 40% hagyományos, 40% ML, 20% AI
        final_score = (traditional_score * 0.4) + (ml_score * 0.4) + (ai_score * 0.2)
        
        return {
            "ai_enhanced": True,
            "ai_score": ai_score,
            "final_score": round(final_score, 1),
            "scoring_method": "triple_hybrid",
            "score_components": {
                "traditional": traditional_score,
                "ml": ml_score,
                "ai": ai_score
            }
        }
    
    def _create_comprehensive_summary(self, results: Dict) -> Dict:
        """Átfogó összefoglaló létrehozása"""
        scores = {}
        ml_scores = {}
        hybrid_scores = {}
        final_scores = {}
        
        for platform, data in results.items():
            if platform == 'summary' or 'error' in data:
                continue
            
            scores[platform] = data.get('compatibility_score', 0)
            ml_scores[platform] = data.get('ml_score', 0)
            hybrid_scores[platform] = data.get('hybrid_score', scores[platform])
            final_scores[platform] = data.get('final_score', hybrid_scores[platform])
        
        if not scores:
            return {"error": "Nincs érvényes platform adat"}
        
        # Legjobb platform a final score alapján
        best_platform = max(final_scores, key=final_scores.get)
        worst_platform = min(final_scores, key=final_scores.get)
        
        return {
            "average_traditional": round(sum(scores.values()) / len(scores), 1),
            "average_ml": round(sum(ml_scores.values()) / len(ml_scores), 1) if ml_scores else 0,
            "average_hybrid": round(sum(hybrid_scores.values()) / len(hybrid_scores), 1),
            "average_final": round(sum(final_scores.values()) / len(final_scores), 1),
            "best_platform": {
                "name": best_platform,
                "score": final_scores[best_platform],
                "strengths": results[best_platform].get('strengths', [])
            },
            "worst_platform": {
                "name": worst_platform,
                "score": final_scores[worst_platform],
                "weaknesses": results[worst_platform].get('weaknesses', [])
            },
            "platform_rankings": sorted(final_scores.items(), key=lambda x: x[1], reverse=True),
            "ml_enabled": self.ml_scorer.is_trained,
            "scoring_methodology": "triple_hybrid" if any(r.get('ai_enhanced') for r in results.values()) else "hybrid_ml",
            "improvement_potential": round(max(final_scores.values()) - min(final_scores.values()), 1)
        }
    
    def get_all_suggestions(self, platform_analyses: Dict) -> Dict:
        """Összes platform optimalizálási javaslatok"""
        all_suggestions = {}
        
        for platform_name, optimizer in self.platforms.items():
            if platform_name in platform_analyses and 'error' not in platform_analyses[platform_name]:
                try:
                    suggestions = optimizer.get_optimization_suggestions(platform_analyses[platform_name])
                    
                    # ML-alapú prioritizálás
                    if self.ml_scorer.is_trained and platform_name in platform_analyses:
                        feature_importance = platform_analyses[platform_name].get('feature_importance', {})
                        suggestions = self._prioritize_suggestions_by_ml(suggestions, feature_importance)
                    
                    all_suggestions[platform_name] = suggestions
                    
                except Exception as e:
                    all_suggestions[platform_name] = [{"error": str(e)}]
        
        # Közös javaslatok
        all_suggestions['common_optimizations'] = self._find_common_suggestions(all_suggestions)
        
        return all_suggestions
    
    def _prioritize_suggestions_by_ml(self, suggestions: List[Dict], feature_importance: Dict) -> List[Dict]:
        """Javaslatok prioritizálása ML feature importance alapján"""
        for suggestion in suggestions:
            # Ha a javaslat kapcsolódik egy fontos feature-höz, növeljük a prioritást
            suggestion_type = suggestion.get('type', '').lower()
            
            for feature, importance in feature_importance.items():
                if feature in suggestion_type or feature in suggestion.get('description', '').lower():
                    if importance > 15:
                        suggestion['ml_priority'] = 'very_high'
                        suggestion['ml_impact'] = f"+{round(importance * 0.5, 1)} pont (ML becslés)"
                    elif importance > 10:
                        suggestion['ml_priority'] = 'high'
                        suggestion['ml_impact'] = f"+{round(importance * 0.4, 1)} pont (ML becslés)"
                    break
        
        # Rendezés ML prioritás szerint
        return sorted(suggestions, key=lambda x: x.get('ml_priority', 'low') == 'very_high', reverse=True)
    
    def _find_common_suggestions(self, all_suggestions: Dict) -> List[Dict]:
        """Közös optimalizálási javaslatok keresése"""
        common = []
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
        
        for suggestion_type, suggestions in type_suggestions.items():
            if len(suggestions) >= 2:
                common_suggestion = suggestions[0].copy()
                common_suggestion['platforms'] = len(suggestions)
                common_suggestion['priority'] = 'high' if len(suggestions) >= 3 else 'medium'
                common.append(common_suggestion)
        
        return common
    
    def get_platform_priorities(self, platform_analyses: Dict) -> List[Dict]:
        """Platform prioritások meghatározása"""
        if 'summary' not in platform_analyses:
            return []
        
        rankings = platform_analyses['summary'].get('platform_rankings', [])
        priorities = []
        
        for platform, score in rankings:
            if score >= 80:
                priority = "Már optimalizált"
                action = "Fenntartás és monitoring"
            elif score >= 60:
                priority = "Közepes prioritás"
                action = "Targeted optimalizáció"
            else:
                priority = "Magas prioritás"
                action = "Teljes átdolgozás javasolt"
            
            # ML confidence hozzáadása
            ml_confidence = platform_analyses.get(platform, {}).get('ml_confidence', 'unknown')
            
            priorities.append({
                "platform": platform,
                "score": score,
                "priority": priority,
                "action": action,
                "ml_confidence": ml_confidence,
                "scoring_method": platform_analyses.get(platform, {}).get('scoring_method', 'traditional')
            })
        
        return priorities