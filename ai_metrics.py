import re
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from urllib.parse import urlparse
import json


class AISpecificMetrics:
    """AI-specifikus metrikák elemzése GEO optimalizáláshoz"""
    
    def __init__(self):
        self.question_patterns = [
            r'\b(mi|mikor|hol|hogyan|miért|milyen|mennyi|ki|melyik)\b',
            r'\b(what|when|where|how|why|which|who|whom)\b',
            r'\?',
        ]
        
        self.answer_indicators = [
            'válasz', 'answer', 'megoldás', 'solution', 'eredmény', 'result'
        ]
    
    def analyze_ai_readiness(self, html: str, url: str) -> Dict:
        """Komplex AI-readiness elemzés"""
        soup = BeautifulSoup(html, 'html.parser')
        text_content = soup.get_text()
        
        return {
            "content_structure": self._analyze_content_structure(soup),
            "qa_format": self._detect_qa_format(soup, text_content),
            "entity_markup": self._check_entity_markup(soup),
            "content_freshness": self._check_content_freshness(soup),
            "citation_readiness": self._check_citations(soup),
            "ai_friendly_formatting": self._check_ai_formatting(soup),
            "knowledge_depth": self._analyze_knowledge_depth(text_content),
            "conversational_elements": self._detect_conversational_elements(text_content)
        }
    
    def _analyze_content_structure(self, soup: BeautifulSoup) -> Dict:
        """Tartalom strukturáltság elemzése AI számára"""
        
        # Listák és felsorolások
        ordered_lists = len(soup.find_all('ol'))
        unordered_lists = len(soup.find_all('ul'))
        list_items = len(soup.find_all('li'))
        
        # Táblázatok
        tables = len(soup.find_all('table'))
        table_headers = len(soup.find_all('th'))
        
        # Bekezdések és hosszúságuk
        paragraphs = soup.find_all('p')
        para_lengths = [len(p.get_text().strip()) for p in paragraphs if p.get_text().strip()]
        avg_para_length = sum(para_lengths) / len(para_lengths) if para_lengths else 0
        
        # Címek és alcímek
        headings = {}
        for i in range(1, 7):
            headings[f'h{i}'] = len(soup.find_all(f'h{i}'))
        
        # Kód blokkok (fejlesztői tartalom esetén)
        code_blocks = len(soup.find_all(['code', 'pre']))
        
        return {
            "lists": {
                "ordered": ordered_lists,
                "unordered": unordered_lists,
                "total_items": list_items,
                "has_structured_lists": list_items > 0
            },
            "tables": {
                "count": tables,
                "headers": table_headers,
                "structured_data": tables > 0 and table_headers > 0
            },
            "paragraphs": {
                "count": len(para_lengths),
                "avg_length": round(avg_para_length, 1),
                "optimal_length": 100 <= avg_para_length <= 300
            },
            "headings": headings,
            "code_blocks": code_blocks,
            "structure_score": self._calculate_structure_score(
                ordered_lists, unordered_lists, list_items, tables, 
                table_headers, avg_para_length, headings
            )
        }
    
    def _detect_qa_format(self, soup: BeautifulSoup, text: str) -> Dict:
        """Q&A formátum detektálása"""
        
        # FAQ schema detektálás
        faq_schemas = soup.find_all("script", type="application/ld+json")
        has_faq_schema = False
        faq_count = 0
        
        for script in faq_schemas:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get("@type") == "FAQPage":
                    has_faq_schema = True
                    faq_count = len(data.get("mainEntity", []))
                    break
            except (json.JSONDecodeError, AttributeError):
                continue
        
        # Kérdés mintázatok keresése
        questions_found = 0
        for pattern in self.question_patterns:
            questions_found += len(re.findall(pattern, text.lower()))
        
        # FAQ specifikus HTML elemek
        faq_elements = len(soup.find_all(['details', 'summary'])) + \
                      len(soup.find_all(class_=re.compile(r'faq|question|answer', re.I)))
        
        # Válasz indikátorok
        answer_indicators = 0
        for indicator in self.answer_indicators:
            answer_indicators += text.lower().count(indicator)
        
        return {
            "has_faq_schema": has_faq_schema,
            "faq_schema_count": faq_count,
            "question_patterns_count": questions_found,
            "faq_html_elements": faq_elements,
            "answer_indicators": answer_indicators,
            "qa_score": min(100, (questions_found * 10 + faq_elements * 15 + 
                                 (50 if has_faq_schema else 0)) / 2)
        }
    
    def _check_entity_markup(self, soup: BeautifulSoup) -> Dict:
        """Entitás markup ellenőrzése"""
        
        # Schema.org entitások
        schema_entities = {
            "Person": len(soup.find_all(attrs={"itemtype": re.compile(r"schema\.org/Person")})),
            "Organization": len(soup.find_all(attrs={"itemtype": re.compile(r"schema\.org/Organization")})),
            "Place": len(soup.find_all(attrs={"itemtype": re.compile(r"schema\.org/Place")})),
            "Product": len(soup.find_all(attrs={"itemtype": re.compile(r"schema\.org/Product")})),
            "Event": len(soup.find_all(attrs={"itemtype": re.compile(r"schema\.org/Event")}))
        }
        
        # JSON-LD entitások
        jsonld_entities = []
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    entity_type = data.get("@type")
                    if entity_type:
                        jsonld_entities.append(entity_type)
            except (json.JSONDecodeError, AttributeError):
                continue
        
        # Microdata
        microdata_items = len(soup.find_all(attrs={"itemscope": True}))
        
        return {
            "schema_entities": schema_entities,
            "jsonld_entities": list(set(jsonld_entities)),
            "microdata_items": microdata_items,
            "total_entities": sum(schema_entities.values()) + len(jsonld_entities) + microdata_items,
            "entity_score": min(100, (sum(schema_entities.values()) * 10 + 
                                    len(jsonld_entities) * 15 + microdata_items * 5))
        }
    
    def _check_content_freshness(self, soup: BeautifulSoup) -> Dict:
        """Tartalom frissesség ellenőrzése"""
        
        # Dátum meta tagek
        date_metas = soup.find_all('meta', attrs={
            'property': re.compile(r'article:(published|modified)_time|og:updated_time'),
            'name': re.compile(r'date|published|modified|updated')
        })
        
        # Dátum szövegek keresése
        text = soup.get_text()
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{1,2}\. \w+ \d{4}',  # 15. január 2024
            r'frissítve|updated|módosítva|utolsó módosítás'
        ]
        
        date_mentions = 0
        for pattern in date_patterns:
            date_mentions += len(re.findall(pattern, text.lower()))
        
        # Schema.org datePublished/dateModified
        jsonld_dates = False
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if "datePublished" in data or "dateModified" in data:
                        jsonld_dates = True
                        break
            except (json.JSONDecodeError, AttributeError):
                continue
        
        return {
            "date_meta_tags": len(date_metas),
            "date_mentions": date_mentions,
            "has_jsonld_dates": jsonld_dates,
            "freshness_score": min(100, len(date_metas) * 25 + date_mentions * 5 + 
                                  (30 if jsonld_dates else 0))
        }
    
    def _check_citations(self, soup: BeautifulSoup) -> Dict:
        """Hivatkozások és idézetek ellenőrzése"""
        
        # Külső linkek
        links = soup.find_all('a', href=True)
        external_links = [
            link for link in links 
            if link.get('href', '').startswith(('http://', 'https://'))
            and 'rel' in link.attrs
        ]
        
        # Idézetek és hivatkozások
        citations = len(soup.find_all(['cite', 'blockquote']))
        footnotes = len(soup.find_all(class_=re.compile(r'footnote|reference|citation', re.I)))
        
        # Schema.org citation markup
        citation_schema = False
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and "citation" in str(data).lower():
                    citation_schema = True
                    break
            except (json.JSONDecodeError, AttributeError):
                continue
        
        return {
            "external_links": len(external_links),
            "citations": citations,
            "footnotes": footnotes,
            "has_citation_schema": citation_schema,
            "citation_score": min(100, len(external_links) * 3 + citations * 15 + 
                                 footnotes * 10 + (20 if citation_schema else 0))
        }
    
    def _check_ai_formatting(self, soup: BeautifulSoup) -> Dict:
        """AI-barát formázás ellenőrzése"""
        
        # Táblázatok caption-ekkel
        tables_with_captions = len(soup.find_all('table', lambda tag: tag.find('caption')))
        total_tables = len(soup.find_all('table'))
        
        # Képek alt texttel
        images = soup.find_all('img')
        images_with_alt = len([img for img in images if img.get('alt')])
        
        # Listák title/aria-label-lel
        lists = soup.find_all(['ul', 'ol'])
        lists_with_labels = len([lst for lst in lists if lst.get('aria-label') or lst.get('title')])
        
        # Strukturált navigáció
        nav_elements = len(soup.find_all(['nav', '[role="navigation"]']))
        breadcrumbs = len(soup.find_all(class_=re.compile(r'breadcrumb', re.I)))
        
        return {
            "tables_with_captions": tables_with_captions,
            "total_tables": total_tables,
            "images_with_alt": images_with_alt,
            "total_images": len(images),
            "lists_with_labels": lists_with_labels,
            "total_lists": len(lists),
            "navigation_elements": nav_elements,
            "breadcrumbs": breadcrumbs,
            "formatting_score": self._calculate_formatting_score(
                tables_with_captions, total_tables, images_with_alt, 
                len(images), lists_with_labels, len(lists), nav_elements, breadcrumbs
            )
        }
    
    def _analyze_knowledge_depth(self, text: str) -> Dict:
        """Tudás mélység elemzése"""
        
        # Szöveg hossz és komplexitás
        word_count = len(text.split())
        sentence_count = len(re.split(r'[.!?]+', text))
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Szakmai kifejezések és kulcsszavak
        technical_words = len(re.findall(r'\b[A-Z]{2,}\b|\b\w+(?:ás|és|ség|ság)\b', text))
        
        # Számok és statisztikák
        numbers = len(re.findall(r'\b\d+(?:[.,]\d+)?%?\b', text))
        
        # Definíciók és magyarázatok
        definitions = len(re.findall(r'\b(például|azaz|vagyis|jelentése|definíció)\b', text.lower()))
        
        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "technical_words": technical_words,
            "numbers_statistics": numbers,
            "definitions": definitions,
            "depth_score": min(100, (word_count / 50) + (technical_words * 2) + 
                              (numbers * 3) + (definitions * 10))
        }
    
    def _detect_conversational_elements(self, text: str) -> Dict:
        """Beszélgetős elemek detektálása"""
        
        # Közvetlen megszólítás
        direct_address = len(re.findall(r'\b(ön|te|maga|önt|téged)\b', text.lower()))
        
        # Kérdések és felkiáltások
        questions = text.count('?')
        exclamations = text.count('!')
        
        # Beszélgetős kifejezések
        conversational_phrases = len(re.findall(
            r'\b(tudod|látod|érted|gondold|képzeld|nézd|figyelj)\b', text.lower()
        ))
        
        return {
            "direct_address": direct_address,
            "questions": questions,
            "exclamations": exclamations,
            "conversational_phrases": conversational_phrases,
            "conversational_score": min(100, direct_address * 5 + questions * 3 + 
                                       exclamations * 2 + conversational_phrases * 8)
        }
    
    def _calculate_structure_score(self, ordered_lists: int, unordered_lists: int, 
                                 list_items: int, tables: int, table_headers: int,
                                 avg_para_length: float, headings: Dict) -> int:
        """Struktúra pontszám számítása"""
        score = 0
        
        # Listák pontszám
        if list_items > 0:
            score += min(30, list_items * 2)
        
        # Táblázatok pontszám
        if tables > 0 and table_headers > 0:
            score += min(25, tables * 10 + table_headers * 2)
        
        # Bekezdés hossz pontszám
        if 100 <= avg_para_length <= 300:
            score += 20
        elif 50 <= avg_para_length <= 500:
            score += 10
        
        # Heading hierarchia pontszám
        h1_count = headings.get('h1', 0)
        if h1_count == 1:
            score += 15
        elif h1_count > 1:
            score -= 10
        
        if headings.get('h2', 0) > 0:
            score += 10
        
        return min(100, score)
    
    def _calculate_formatting_score(self, tables_with_captions: int, total_tables: int,
                                  images_with_alt: int, total_images: int,
                                  lists_with_labels: int, total_lists: int,
                                  nav_elements: int, breadcrumbs: int) -> int:
        """Formázás pontszám számítása"""
        score = 0
        
        # Táblázatok
        if total_tables > 0:
            score += (tables_with_captions / total_tables) * 25
        
        # Képek
        if total_images > 0:
            score += (images_with_alt / total_images) * 30
        else:
            score += 10  # Ha nincs kép, az is rendben van
        
        # Listák
        if total_lists > 0:
            score += (lists_with_labels / total_lists) * 20
        
        # Navigáció
        score += min(15, nav_elements * 7)
        score += min(10, breadcrumbs * 10)
        
        return min(100, score)
    
    def get_ai_readiness_summary(self, metrics: Dict) -> Dict:
        """AI-readiness összefoglaló"""
        
        scores = {
            "structure": metrics.get("content_structure", {}).get("structure_score", 0),
            "qa_format": metrics.get("qa_format", {}).get("qa_score", 0),
            "entities": metrics.get("entity_markup", {}).get("entity_score", 0),
            "freshness": metrics.get("content_freshness", {}).get("freshness_score", 0),
            "citations": metrics.get("citation_readiness", {}).get("citation_score", 0),
            "formatting": metrics.get("ai_friendly_formatting", {}).get("formatting_score", 0),
            "depth": metrics.get("knowledge_depth", {}).get("depth_score", 0),
            "conversational": metrics.get("conversational_elements", {}).get("conversational_score", 0)
        }
        
        # Súlyozott átlag
        weights = {
            "structure": 0.20,
            "qa_format": 0.15,
            "entities": 0.15,
            "freshness": 0.10,
            "citations": 0.10,
            "formatting": 0.15,
            "depth": 0.10,
            "conversational": 0.05
        }
        
        total_score = sum(scores[key] * weights[key] for key in scores)
        
        return {
            "individual_scores": scores,
            "weighted_average": round(total_score, 1),
            "level": self._get_readiness_level(total_score),
            "top_strengths": self._get_top_areas(scores, top=True),
            "improvement_areas": self._get_top_areas(scores, top=False)
        }
    
    def _get_readiness_level(self, score: float) -> str:
        """AI-readiness szint meghatározása"""
        if score >= 80:
            return "Kiváló"
        elif score >= 60:
            return "Jó"
        elif score >= 40:
            return "Közepes"
        else:
            return "Fejlesztendő"
    
    def _get_top_areas(self, scores: Dict, top: bool = True) -> List[str]:
        """Legjobb/leggyengébb területek"""
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=top)
        return [area for area, score in sorted_scores[:3]]