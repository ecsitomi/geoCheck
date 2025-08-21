import re
import math
from typing import Dict, List, Tuple, Optional
from bs4 import BeautifulSoup
from collections import Counter
import urllib.parse


class ContentQualityAnalyzer:
    """Tartalom minőség és releváns elemzés AI optimalizáláshoz"""
    
    def __init__(self):
        # Magyar stop szavak
        self.stop_words = {
            'a', 'az', 'és', 'vagy', 'de', 'hogy', 'mint', 'egy', 'is', 'csak', 'nem', 
            'van', 'volt', 'lesz', 'lehet', 'kell', 'még', 'már', 'el', 'fel', 'ki', 
            'be', 'le', 'át', 'meg', 'vissza', 'össze', 'szét', 'rá', 'ide', 'oda',
            'minden', 'semmi', 'valami', 'ahol', 'amikor', 'ahogy', 'amíg', 'míg',
            'ha', 'akkor', 'ezért', 'mert', 'mivel', 'így', 'úgy', 'olyan', 'ilyen'
        }
        
        # Angol stop szavak (internationális oldalakhoz)
        self.english_stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'can', 'this', 'that', 'these', 'those', 'what', 'where',
            'when', 'why', 'how', 'who', 'which', 'all', 'any', 'some', 'no', 'not'
        }
        
        # Minőségi indikátorok
        self.quality_indicators = [
            'példa', 'például', 'case study', 'kutatás', 'research', 'study',
            'statisztika', 'statistics', 'adat', 'data', 'eredmény', 'result',
            'tapasztalat', 'experience', 'szakértő', 'expert', 'módszer', 'method'
        ]
        
        # Negatív indikátorok (spam jellegű)
        self.negative_indicators = [
            'kattints', 'click here', 'ingyen', 'free', 'garantált', 'guaranteed',
            'legjobb', 'best ever', 'csodálatos', 'amazing', 'hihetetlen', 'incredible',
            'titok', 'secret', 'sürgős', 'urgent', 'limitált', 'limited time'
        ]
    
    def analyze_content_quality(self, html: str, url: str) -> Dict:
        """Teljes tartalom minőség elemzés"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Tiszta szöveg kinyerése
        text_content = self._extract_clean_text(soup)
        
        return {
            "readability": self._analyze_readability(text_content),
            "keyword_analysis": self._analyze_keywords(text_content, url),
            "content_depth": self._analyze_content_depth(text_content, soup),
            "authority_signals": self._check_authority_signals(text_content, soup),
            "user_intent": self._analyze_user_intent(text_content, soup),
            "content_uniqueness": self._check_content_uniqueness(text_content),
            "semantic_richness": self._analyze_semantic_content(text_content),
            "engagement_factors": self._analyze_engagement_factors(soup),
            "overall_quality_score": 0  # Ezt utólag számoljuk ki
        }
    
    def _extract_clean_text(self, soup: BeautifulSoup) -> str:
        """Tiszta szöveg kinyerése HTML-ből"""
        # Script és style elemek eltávolítása
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Főtartalom keresése
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|post', re.I))
        
        if main_content:
            text = main_content.get_text()
        else:
            text = soup.get_text()
        
        # Szöveg tisztítása
        text = re.sub(r'\s+', ' ', text)  # Többszörös space-ek
        text = re.sub(r'\n+', '\n', text)  # Többszörös új sorok
        
        return text.strip()
    
    def _analyze_readability(self, text: str) -> Dict:
        """Olvashatóság elemzése"""
        
        # Alapstatisztikák
        words = [word.lower().strip('.,!?;:()[]{}') for word in text.split()]
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        word_count = len(words)
        sentence_count = len(sentences)
        
        if sentence_count == 0:
            return {"error": "Nincs értelmezhető szöveg"}
        
        # Átlagos mondathossz
        avg_sentence_length = word_count / sentence_count
        
        # Átlagos szóhossz
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        
        # Komplex szavak (5+ karakteres)
        complex_words = [word for word in words if len(word) >= 5]
        complex_word_ratio = len(complex_words) / word_count if word_count > 0 else 0
        
        # Flesch-kincaid adaptált pontozás (magyar nyelvre)
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * complex_word_ratio)
        flesch_score = max(0, min(100, flesch_score))
        
        # Bekezdés elemzés
        paragraphs = text.split('\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        avg_paragraph_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        
        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "paragraph_count": len(paragraphs),
            "avg_sentence_length": round(avg_sentence_length, 1),
            "avg_word_length": round(avg_word_length, 1),
            "avg_paragraph_length": round(avg_paragraph_length, 1),
            "complex_word_ratio": round(complex_word_ratio, 3),
            "flesch_score": round(flesch_score, 1),
            "readability_level": self._get_readability_level(flesch_score),
            "readability_score": self._calculate_readability_score(
                avg_sentence_length, avg_paragraph_length, complex_word_ratio, flesch_score
            )
        }
    
    def _analyze_keywords(self, text: str, url: str) -> Dict:
        """Kulcsszó elemzés és sűrűség"""
        
        # Szavak tisztítása és normalizálása
        words = re.findall(r'\b[a-záéíóöőúüű]{3,}\b', text.lower())
        words = [word for word in words if word not in self.stop_words and word not in self.english_stop_words]
        
        # Szógyakoriság
        word_freq = Counter(words)
        total_words = len(words)
        
        # Top kulcsszavak
        top_keywords = word_freq.most_common(10)
        
        # URL-ből kulcsszavak kinyerése
        url_path = urllib.parse.urlparse(url).path
        url_keywords = re.findall(r'[a-záéíóöőúüű]+', url_path.lower())
        url_keywords = [word for word in url_keywords if len(word) > 2]
        
        # Kulcsszó sűrűség számítás
        keyword_densities = {}
        for word, freq in top_keywords:
            density = (freq / total_words) * 100
            keyword_densities[word] = round(density, 2)
        
        # Title-ben és heading-ekben való megjelenés (ezt majd a soup-ból kell kinyerni)
        
        return {
            "total_words": total_words,
            "unique_words": len(word_freq),
            "vocabulary_richness": round(len(word_freq) / total_words, 3) if total_words > 0 else 0,
            "top_keywords": top_keywords,
            "keyword_densities": keyword_densities,
            "url_keywords": url_keywords,
            "keyword_score": self._calculate_keyword_score(keyword_densities, total_words)
        }
    
    def _analyze_content_depth(self, text: str, soup: BeautifulSoup) -> Dict:
        """Tartalom mélység elemzése"""
        
        # Szöveg hossz kategóriák
        word_count = len(text.split())
        
        # Témák és altémák (heading struktúra alapján)
        headings = {}
        for i in range(1, 7):
            headings[f'h{i}'] = [h.get_text().strip() for h in soup.find_all(f'h{i}')]
        
        # Szakmai tartalom indikátorok
        quality_mentions = sum(text.lower().count(indicator) for indicator in self.quality_indicators)
        
        # Példák és esettanulmányok
        examples = len(re.findall(r'\b(példa|example|eset|case|történet|story)\b', text.lower()))
        
        # Számadatok és statisztikák
        numbers = len(re.findall(r'\b\d+(?:[.,]\d+)?%?\b', text))
        
        # Hivatkozások és források
        external_refs = len(soup.find_all('a', href=re.compile(r'^https?://')))
        
        # Lista és felsorolások
        lists = len(soup.find_all(['ul', 'ol']))
        list_items = len(soup.find_all('li'))
        
        return {
            "content_length_category": self._get_content_length_category(word_count),
            "topic_coverage": len([h for headings_list in headings.values() for h in headings_list]),
            "heading_structure": headings,
            "quality_indicators": quality_mentions,
            "examples_count": examples,
            "statistics_count": numbers,
            "external_references": external_refs,
            "structured_content": {
                "lists": lists,
                "list_items": list_items
            },
            "depth_score": self._calculate_depth_score(
                word_count, quality_mentions, examples, numbers, external_refs, lists
            )
        }
    
    def _check_authority_signals(self, text: str, soup: BeautifulSoup) -> Dict:
        """Tekintély és hitelesség ellenőrzése"""
        
        # Szerző információk
        author_info = soup.find(['[rel="author"]', '[class*="author"]', '[id*="author"]'])
        has_author = bool(author_info)
        
        # Dátum információk
        date_elements = soup.find_all(['time', '[datetime]']) + \
                       soup.find_all(attrs={'class': re.compile(r'date|published|updated', re.I)})
        has_dates = len(date_elements) > 0
        
        # Kapcsolat és social linkek
        contact_info = len(soup.find_all(['[href*="contact"]', '[href*="about"]', '[href*="kapcsolat"]']))
        social_links = len(soup.find_all('a', href=re.compile(r'facebook|twitter|linkedin|instagram|youtube')))
        
        # Szakmai kifejezések és jargon
        professional_terms = len(re.findall(r'\b[A-ZÁÉÍÓÖŐÚÜŰ][a-záéíóöőúüű]*(?:ás|és|ség|ság|izmus|ció|tás|tés)\b', text))
        
        # Negatív spam indikátorok
        spam_indicators = sum(text.lower().count(neg) for neg in self.negative_indicators)
        
        # Tanúsítványok és award-ok említése
        credentials = len(re.findall(r'\b(tanúsítvány|certificate|díj|award|elismerés|akkreditáció)\b', text.lower()))
        
        return {
            "has_author_info": has_author,
            "has_publication_dates": has_dates,
            "contact_information": contact_info,
            "social_presence": social_links,
            "professional_terminology": professional_terms,
            "spam_indicators": spam_indicators,
            "credentials_mentions": credentials,
            "authority_score": self._calculate_authority_score(
                has_author, has_dates, contact_info, social_links, 
                professional_terms, spam_indicators, credentials
            )
        }
    
    def _analyze_user_intent(self, text: str, soup: BeautifulSoup) -> Dict:
        """Felhasználói szándék elemzése"""
        
        # Intent típusok detektálása
        informational_keywords = [
            'mi', 'what', 'hogyan', 'how', 'miért', 'why', 'mikor', 'when',
            'hol', 'where', 'ki', 'who', 'melyik', 'which', 'útmutató', 'guide'
        ]
        
        transactional_keywords = [
            'vásárlás', 'buy', 'rendelés', 'order', 'ár', 'price', 'költség', 'cost',
            'kedvezmény', 'discount', 'akció', 'sale', 'bolt', 'shop', 'store'
        ]
        
        navigational_keywords = [
            'bejelentkezés', 'login', 'regisztráció', 'register', 'kapcsolat', 'contact',
            'rólunk', 'about', 'szolgáltatás', 'service', 'termék', 'product'
        ]
        
        # Intent erősség számítása
        informational_score = sum(text.lower().count(kw) for kw in informational_keywords)
        transactional_score = sum(text.lower().count(kw) for kw in transactional_keywords)
        navigational_score = sum(text.lower().count(kw) for kw in navigational_keywords)
        
        # Domináns intent meghatározása
        intent_scores = {
            'informational': informational_score,
            'transactional': transactional_score,
            'navigational': navigational_score
        }
        
        primary_intent = max(intent_scores, key=intent_scores.get)
        
        # CTA elemek
        cta_elements = len(soup.find_all(['button', '[role="button"]'])) + \
                      len(soup.find_all('a', class_=re.compile(r'btn|button|cta', re.I)))
        
        return {
            "intent_scores": intent_scores,
            "primary_intent": primary_intent,
            "intent_clarity": max(intent_scores.values()) / sum(intent_scores.values()) if sum(intent_scores.values()) > 0 else 0,
            "cta_elements": cta_elements,
            "intent_match_score": self._calculate_intent_score(intent_scores, cta_elements)
        }
    
    def _check_content_uniqueness(self, text: str) -> Dict:
        """Tartalom egyediség ellenőrzése"""
        
        # Mondatok elemzése
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        # Ismétlődő mondatok keresése
        sentence_freq = Counter(sentences)
        repeated_sentences = sum(1 for count in sentence_freq.values() if count > 1)
        
        # Szóismétlés elemzése
        words = text.lower().split()
        word_freq = Counter(words)
        
        # Túl gyakori szavak (spam gyanús)
        overused_words = sum(1 for word, count in word_freq.items() 
                           if count > len(words) * 0.05 and len(word) > 3)
        
        # Boilerplate tartalom detektálása
        boilerplate_phrases = [
            'minden jog fenntartva', 'all rights reserved', 'cookie-k használata',
            'adatvédelem', 'privacy policy', 'felhasználási feltételek', 'terms of use'
        ]
        
        boilerplate_count = sum(text.lower().count(phrase) for phrase in boilerplate_phrases)
        
        return {
            "total_sentences": len(sentences),
            "repeated_sentences": repeated_sentences,
            "overused_words": overused_words,
            "boilerplate_content": boilerplate_count,
            "uniqueness_score": self._calculate_uniqueness_score(
                len(sentences), repeated_sentences, overused_words, boilerplate_count
            )
        }
    
    def _analyze_semantic_content(self, text: str) -> Dict:
        """Szemantikus tartalom elemzése"""
        
        # Entitások keresése (személyek, helyek, szervezetek)
        person_patterns = r'\b[A-ZÁÉÍÓÖŐÚÜŰ][a-záéíóöőúüű]+ [A-ZÁÉÍÓÖŐÚÜŰ][a-záéíóöőúüű]+\b'
        persons = len(re.findall(person_patterns, text))
        
        # Helyek (nagybetűs szavak)
        places = len(re.findall(r'\b[A-ZÁÉÍÓÖŐÚÜŰ][a-záéíóöőúüű]{2,}(?:ban|ben|ra|re|ról|ről|nál|nél)\b', text))
        
        # Dátumok és időpontok
        dates = len(re.findall(r'\b\d{4}\.?\s*(?:január|február|március|április|május|június|július|augusztus|szeptember|október|november|december)|\d{1,2}\.\s*\d{1,2}\.\s*\d{4}', text))
        
        # Számok és mértékegységek
        measurements = len(re.findall(r'\b\d+(?:[.,]\d+)?\s*(?:kg|g|km|m|cm|mm|l|ml|°C|€|Ft|$|%)\b', text))
        
        # Témakörök (szakzsargon alapján)
        tech_terms = len(re.findall(r'\b(?:API|HTML|CSS|JavaScript|Python|SEO|UX|UI|AI|ML|IoT|SaaS)\b', text))
        business_terms = len(re.findall(r'\b(?:marketing|sales|ROI|KPI|B2B|B2C|startup|business|vállalkozás)\b', text.lower()))
        
        return {
            "entities": {
                "persons": persons,
                "places": places,
                "dates": dates,
                "measurements": measurements
            },
            "domain_expertise": {
                "technology": tech_terms,
                "business": business_terms
            },
            "semantic_richness": persons + places + dates + measurements + tech_terms + business_terms,
            "semantic_score": min(100, (persons * 3 + places * 2 + dates * 2 + 
                                       measurements * 2 + tech_terms * 5 + business_terms * 3))
        }
    
    def _analyze_engagement_factors(self, soup: BeautifulSoup) -> Dict:
        """Engagement tényezők elemzése"""
        
        # Multimédia tartalom
        images = len(soup.find_all('img'))
        videos = len(soup.find_all(['video', 'iframe[src*="youtube"]', 'iframe[src*="vimeo"]']))
        
        # Interaktív elemek
        forms = len(soup.find_all('form'))
        buttons = len(soup.find_all(['button', 'input[type="submit"]', 'input[type="button"]']))
        
        # Közösségi funkciók
        comments = len(soup.find_all(class_=re.compile(r'comment|discussion', re.I)))
        sharing = len(soup.find_all(['[data-share]', '[class*="share"]']))
        
        # Navigációs elemek
        internal_links = len(soup.find_all('a', href=re.compile(r'^(?!https?://)')))
        
        return {
            "multimedia": {
                "images": images,
                "videos": videos
            },
            "interactivity": {
                "forms": forms,
                "buttons": buttons
            },
            "social_features": {
                "comments": comments,
                "sharing_buttons": sharing
            },
            "internal_links": internal_links,
            "engagement_score": min(100, images * 2 + videos * 10 + forms * 5 + 
                                   buttons * 3 + comments * 8 + sharing * 5 + 
                                   min(internal_links, 20) * 2)
        }
    
    # Pontszám számító metódusok
    def _get_readability_level(self, flesch_score: float) -> str:
        """Olvashatóság szint meghatározása"""
        if flesch_score >= 80:
            return "Nagyon könnyű"
        elif flesch_score >= 60:
            return "Könnyű"
        elif flesch_score >= 40:
            return "Közepes"
        elif flesch_score >= 20:
            return "Nehéz"
        else:
            return "Nagyon nehéz"
    
    def _get_content_length_category(self, word_count: int) -> str:
        """Tartalom hossz kategória"""
        if word_count < 300:
            return "Rövid"
        elif word_count < 1000:
            return "Közepes"
        elif word_count < 2500:
            return "Hosszú"
        else:
            return "Nagyon hosszú"
    
    def _calculate_readability_score(self, avg_sentence: float, avg_paragraph: float, 
                                   complex_ratio: float, flesch: float) -> int:
        """Olvashatóság pontszám"""
        score = flesch * 0.4
        
        # Optimális mondathossz: 15-25 szó
        if 15 <= avg_sentence <= 25:
            score += 20
        elif 10 <= avg_sentence <= 30:
            score += 10
        
        # Optimális bekezdéshossz: 50-150 szó
        if 50 <= avg_paragraph <= 150:
            score += 20
        elif 30 <= avg_paragraph <= 200:
            score += 10
        
        # Komplex szavak aránya ne legyen túl magas
        if complex_ratio < 0.3:
            score += 20
        elif complex_ratio < 0.5:
            score += 10
        
        return min(100, score)
    
    def _calculate_keyword_score(self, densities: Dict, total_words: int) -> int:
        """Kulcsszó pontszám"""
        if not densities or total_words < 100:
            return 0
        
        score = 0
        
        # Optimális kulcsszó sűrűség: 1-3%
        for word, density in densities.items():
            if 1 <= density <= 3:
                score += 20
            elif 0.5 <= density <= 5:
                score += 10
            elif density > 5:
                score -= 10  # Túl magas sűrűség (spam gyanús)
        
        # Kulcsszó diverzitás
        if len(densities) >= 5:
            score += 20
        elif len(densities) >= 3:
            score += 10
        
        return min(100, max(0, score))
    
    def _calculate_depth_score(self, word_count: int, quality: int, examples: int,
                             numbers: int, refs: int, lists: int) -> int:
        """Tartalom mélység pontszám"""
        score = 0
        
        # Szöveg hossz
        if word_count >= 1000:
            score += 25
        elif word_count >= 500:
            score += 15
        elif word_count >= 300:
            score += 10
        
        # Minőségi tartalom
        score += min(20, quality * 4)
        score += min(15, examples * 5)
        score += min(15, numbers * 2)
        score += min(15, refs * 3)
        score += min(10, lists * 5)
        
        return min(100, score)
    
    def _calculate_authority_score(self, author: bool, dates: bool, contact: int,
                                 social: int, prof_terms: int, spam: int, creds: int) -> int:
        """Tekintély pontszám"""
        score = 0
        
        if author:
            score += 20
        if dates:
            score += 15
        
        score += min(15, contact * 7)
        score += min(10, social * 2)
        score += min(20, prof_terms * 2)
        score += min(10, creds * 10)
        
        # Spam levonás
        score -= min(30, spam * 10)
        
        return min(100, max(0, score))
    
    def _calculate_intent_score(self, intents: Dict, cta: int) -> int:
        """Intent matching pontszám"""
        total_intent = sum(intents.values())
        if total_intent == 0:
            return 0
        
        # Intent clarity
        max_intent = max(intents.values())
        clarity = (max_intent / total_intent) * 50
        
        # CTA megfelelőség
        cta_score = min(50, cta * 10)
        
        return min(100, clarity + cta_score)
    
    def _calculate_uniqueness_score(self, total_sent: int, repeated: int,
                                  overused: int, boilerplate: int) -> int:
        """Egyediség pontszám"""
        if total_sent == 0:
            return 0
        
        score = 100
        
        # Ismétlődő mondatok levonása
        if repeated > 0:
            score -= (repeated / total_sent) * 50
        
        # Túlhasznált szavak
        score -= min(30, overused * 5)
        
        # Boilerplate tartalom
        score -= min(20, boilerplate * 10)
        
        return max(0, score)
    
    def calculate_overall_quality_score(self, analysis: Dict) -> int:
        """Összesített minőség pontszám"""
        scores = {
            "readability": analysis.get("readability", {}).get("readability_score", 0),
            "keywords": analysis.get("keyword_analysis", {}).get("keyword_score", 0),
            "depth": analysis.get("content_depth", {}).get("depth_score", 0),
            "authority": analysis.get("authority_signals", {}).get("authority_score", 0),
            "intent": analysis.get("user_intent", {}).get("intent_match_score", 0),
            "uniqueness": analysis.get("content_uniqueness", {}).get("uniqueness_score", 0),
            "semantic": analysis.get("semantic_richness", {}).get("semantic_score", 0),
            "engagement": analysis.get("engagement_factors", {}).get("engagement_score", 0)
        }
        
        # Súlyozott átlag
        weights = {
            "readability": 0.15,
            "keywords": 0.15,
            "depth": 0.20,
            "authority": 0.15,
            "intent": 0.10,
            "uniqueness": 0.10,
            "semantic": 0.10,
            "engagement": 0.05
        }
        
        weighted_score = sum(scores[key] * weights[key] for key in scores)
        return round(weighted_score, 1)