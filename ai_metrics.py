import re
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import json
from collections import Counter
import statistics


class AISpecificMetrics:
    """TURBÓZOTT AI-specifikus metrikák elemzése GEO optimalizáláshoz"""
    
    def __init__(self):
        # Fejlett kérdés pattern-ek - több nyelven és formátumban
        self.question_patterns = [
            # Magyar kérdőszavak
            r'\b(mi(?:t|nek|ért|kor|lyen|nden)?|hol|hogy(?:an)?|miért|melyik|mennyi|ki(?:t|nek)?|mikor)\b',
            # Angol kérdőszavak
            r'\b(what|when|where|how|why|which|who|whom|whose|how\s+(?:to|do|does|can|much|many))\b',
            # Kérdőjelek és pattern-ek
            r'\?',
            # Step-by-step jelzők
            r'\b(lépés|step|phase|stage|először|first|második|second|harmadik|third)\b',
            # Tutorial jelzők
            r'\b(útmutató|tutorial|guide|how-to|hogyan)\b'
        ]
        
        self.answer_indicators = [
            'válasz', 'answer', 'megoldás', 'solution', 'eredmény', 'result',
            'következő', 'next', 'végül', 'finally', 'összefoglalva', 'summary'
        ]
        
        # AI-barát tartalom jelek
        self.ai_friendly_patterns = {
            'step_by_step': [
                r'\b\d+\.\s',  # 1. 2. 3.
                r'\bstep\s+\d+',  # step 1, step 2
                r'\b(első|második|harmadik|negyedik|ötödik)\s+(lépés|phase)',
                r'\b(first|second|third|fourth|fifth)\s+(step|stage)',
                r'(kezdésként|first|először|to\s+start)',
                r'(végül|finally|last|utoljára)'
            ],
            'code_examples': [
                r'<code[^>]*>.*?</code>',
                r'```[\s\S]*?```',
                r'<pre[^>]*>.*?</pre>',
                r'\b(példa|example|code|kód):\s*\n',
                r'function\s+\w+\s*\(',
                r'def\s+\w+\s*\(',
                r'class\s+\w+',
                r'import\s+\w+'
            ],
            'interactive_elements': [
                r'<button[^>]*>',
                r'<input[^>]*>',
                r'onclick\s*=',
                r'addEventListener',
                r'\b(kattints|click|select|choose|válassz)\b'
            ]
        }

    def analyze_ai_readiness(self, html: str, url: str) -> Dict:
        """TURBÓZOTT AI-readiness elemzés - minden AI platform igényére optimalizálva"""
        soup = BeautifulSoup(html, 'html.parser')
        text_content = soup.get_text()
        
        return {
            "content_structure": self._analyze_enhanced_content_structure(soup, text_content),
            "qa_format": self._detect_enhanced_qa_format(soup, text_content),
            "entity_markup": self._check_enhanced_entity_markup(soup),
            "content_freshness": self._check_enhanced_content_freshness(soup, text_content),
            "citation_readiness": self._check_enhanced_citations(soup, text_content),
            "ai_friendly_formatting": self._check_enhanced_ai_formatting(soup, text_content),
            "knowledge_depth": self._analyze_enhanced_knowledge_depth(text_content, soup),
            "conversational_elements": self._detect_enhanced_conversational_elements(text_content, soup)
        }

    def _analyze_enhanced_content_structure(self, soup: BeautifulSoup, text: str) -> Dict:
        """TURBÓZOTT tartalom strukturáltság elemzése - AI platformok preferenciáira optimalizálva"""
        
        # Alapvető struktúra elemzés
        ordered_lists = soup.find_all('ol')
        unordered_lists = soup.find_all('ul') 
        list_items = soup.find_all('li')
        
        # Fejlett lista elemzés
        numbered_lists = len([ol for ol in ordered_lists if len(ol.find_all('li')) >= 3])
        step_lists = len([ol for ol in ordered_lists if 
                         any(re.search(r'\b(step|lépés)\b', li.get_text().lower()) for li in ol.find_all('li'))])
        
        # Táblázatok és adatstruktúrák
        tables = soup.find_all('table')
        data_tables = len([t for t in tables if len(t.find_all('tr')) >= 3 and len(t.find_all('th')) > 0])
        
        # Bekezdések minősége
        paragraphs = soup.find_all('p')
        para_texts = [p.get_text().strip() for p in paragraphs if p.get_text().strip()]
        para_lengths = [len(text) for text in para_texts]
        
        # Optimális bekezdés hossz AI-hez (100-300 karakter)
        optimal_paras = len([length for length in para_lengths if 100 <= length <= 300])
        
        # Címek és hierarchia
        headings = {}
        heading_texts = {}
        for i in range(1, 7):
            h_tags = soup.find_all(f'h{i}')
            headings[f'h{i}'] = len(h_tags)
            heading_texts[f'h{i}'] = [h.get_text().strip() for h in h_tags]
        
        # Heading SEO minőség
        descriptive_headings = 0
        for level, texts in heading_texts.items():
            for text in texts:
                if len(text) > 3 and any(char.isalpha() for char in text):
                    descriptive_headings += 1
        
        # Kód blokkok és példák (AI-k szeretik)
        code_blocks = len(soup.find_all(['code', 'pre']))
        inline_code = len(soup.find_all('code'))
        
        # Interaktív elemek
        interactive_elements = len(soup.find_all(['button', 'input', 'select', 'textarea']))
        
        # Step-by-step tartalom detektálása
        step_indicators = 0
        for pattern in self.ai_friendly_patterns['step_by_step']:
            step_indicators += len(re.findall(pattern, text, re.IGNORECASE))
        
        return {
            "lists": {
                "ordered": len(ordered_lists),
                "unordered": len(unordered_lists), 
                "total_items": len(list_items),
                "numbered_lists": numbered_lists,
                "step_by_step_lists": step_lists,
                "has_structured_lists": len(list_items) > 0,
                "list_quality_score": self._calculate_list_quality(ordered_lists, unordered_lists, step_lists)
            },
            "tables": {
                "count": len(tables),
                "data_tables": data_tables,
                "headers": len(soup.find_all('th')),
                "structured_data": data_tables > 0,
                "table_quality_score": min(100, data_tables * 25)
            },
            "paragraphs": {
                "count": len(para_texts),
                "avg_length": round(statistics.mean(para_lengths), 1) if para_lengths else 0,
                "optimal_length_count": optimal_paras,
                "optimal_percentage": round((optimal_paras / len(para_texts)) * 100, 1) if para_texts else 0,
                "quality_score": min(100, (optimal_paras / max(1, len(para_texts))) * 100)
            },
            "headings": {
                **headings,
                "total_headings": sum(headings.values()),
                "descriptive_headings": descriptive_headings,
                "hierarchy_score": self._calculate_heading_hierarchy_score(headings),
                "quality_score": min(100, (descriptive_headings / max(1, sum(headings.values()))) * 100)
            },
            "code_and_examples": {
                "code_blocks": code_blocks,
                "inline_code": inline_code,
                "has_examples": code_blocks > 0,
                "code_quality_score": min(100, code_blocks * 15 + inline_code * 5)
            },
            "interactivity": {
                "interactive_elements": interactive_elements,
                "step_indicators": step_indicators,
                "has_step_by_step": step_indicators >= 3,
                "interactivity_score": min(100, interactive_elements * 10 + (20 if step_indicators >= 3 else 0))
            },
            "structure_score": self._calculate_enhanced_structure_score(
                len(ordered_lists), len(unordered_lists), len(list_items), 
                data_tables, optimal_paras, len(para_texts), headings, 
                descriptive_headings, code_blocks, step_indicators
            )
        }

    def _detect_enhanced_qa_format(self, soup: BeautifulSoup, text: str) -> Dict:
        """TURBÓZOTT Q&A formátum detektálása - robusztus JSON parsing és modern pattern-ek"""
        
        # FAQ schema detektálás - TURBÓZOTT verzió
        faq_schemas = soup.find_all("script", type="application/ld+json")
        has_faq_schema = False
        faq_count = 0
        qa_schemas = []
        
        for script in faq_schemas:
            try:
                script_content = script.string
                if not script_content:
                    continue
                    
                # Tisztítás és normalizálás
                script_content = script_content.strip()
                # Gyakori problémák javítása
                script_content = re.sub(r',\s*}', '}', script_content)  # trailing commas
                script_content = re.sub(r',\s*]', ']', script_content)  # trailing commas in arrays
                
                try:
                    data = json.loads(script_content)
                except json.JSONDecodeError:
                    # Fallback: próbáljunk meg részleges JSON-t kinyerni
                    faq_match = re.search(r'"@type"\s*:\s*"FAQPage"', script_content)
                    if faq_match:
                        has_faq_schema = True
                        # Próbáljuk meg a mainEntity-k számát megbecsülni
                        entity_matches = re.findall(r'"@type"\s*:\s*"Question"', script_content)
                        faq_count = max(faq_count, len(entity_matches))
                    continue
                
                # Rekurzív keresés minden schema típusra
                found_schemas = self._find_qa_schemas_recursive(data)
                qa_schemas.extend(found_schemas)
                
                for schema in found_schemas:
                    if schema['type'] == 'FAQPage':
                        has_faq_schema = True
                        faq_count = max(faq_count, schema['count'])
                        
            except Exception:
                # Teljesen silent fallback
                continue
        
        # Fejlett kérdés-válasz pattern keresés
        questions_found = 0
        question_types = {'direct': 0, 'indirect': 0, 'numbered': 0}
        
        for pattern in self.question_patterns:
            matches = re.findall(pattern, text.lower())
            questions_found += len(matches)
            
            # Kérdés típusok azonosítása
            if any(word in pattern for word in ['mi', 'what', 'how']):
                question_types['direct'] += len(matches)
            elif any(word in pattern for word in ['step', 'lépés']):
                question_types['numbered'] += len(matches)
            else:
                question_types['indirect'] += len(matches)
        
        # HTML FAQ elemek - TURBÓZOTT verzió
        faq_elements = len(soup.find_all(['details', 'summary']))
        faq_classes = len(soup.find_all(class_=re.compile(r'faq|question|answer|qa|qanda', re.I)))
        accordion_elements = len(soup.find_all(class_=re.compile(r'accordion|collapse|toggle', re.I)))
        
        # Válasz indikátorok és párosítás
        answer_indicators = 0
        qa_pairs = 0
        
        for indicator in self.answer_indicators:
            count = text.lower().count(indicator)
            answer_indicators += count
            
        # Q&A párok becslése
        qa_pairs = min(questions_found, answer_indicators)
        
        # Modern Q&A formátumok
        structured_qa = self._detect_structured_qa_patterns(soup, text)
        
        # AI-barát Q&A jellemzők
        ai_qa_features = {
            'has_numbered_questions': question_types['numbered'] > 0,
            'has_step_by_step': any(re.search(pattern, text, re.I) for pattern in self.ai_friendly_patterns['step_by_step']),
            'has_clear_answers': answer_indicators >= questions_found * 0.5,
            'has_html_structure': faq_elements > 0 or accordion_elements > 0
        }
        
        # Fejlett pontozás
        qa_score = self._calculate_enhanced_qa_score(
            has_faq_schema, faq_count, questions_found, faq_elements + faq_classes,
            answer_indicators, qa_pairs, structured_qa, ai_qa_features
        )
        
        return {
            "has_faq_schema": has_faq_schema,
            "faq_schema_count": faq_count,
            "qa_schemas_found": qa_schemas,
            "question_patterns_count": questions_found,
            "question_types": question_types,
            "faq_html_elements": faq_elements + faq_classes + accordion_elements,
            "answer_indicators": answer_indicators,
            "estimated_qa_pairs": qa_pairs,
            "structured_qa_patterns": structured_qa,
            "ai_qa_features": ai_qa_features,
            "qa_score": qa_score
        }

    def _check_enhanced_entity_markup(self, soup: BeautifulSoup) -> Dict:
        """TURBÓZOTT entitás markup ellenőrzése - több schema típus és jobb detektálás"""
        
        # Kibővített Schema.org entitások
        entity_types = {
            "Person": ["Person", "author", "contributor"],
            "Organization": ["Organization", "Corporation", "NGO", "brand"],
            "Place": ["Place", "LocalBusiness", "Restaurant", "Store"],
            "Product": ["Product", "SoftwareApplication", "Book", "Movie"],
            "Event": ["Event", "Conference", "Concert", "Workshop"],
            "Article": ["Article", "BlogPosting", "NewsArticle", "TechArticle"],
            "Service": ["Service", "ProfessionalService", "FinancialService"],
            "CreativeWork": ["CreativeWork", "VideoObject", "ImageObject", "Dataset"]
        }
        
        schema_entities = {}
        for category, types in entity_types.items():
            count = 0
            for schema_type in types:
                count += len(soup.find_all(attrs={"itemtype": re.compile(rf"schema\.org/{schema_type}", re.I)}))
            schema_entities[category] = count
        
        # JSON-LD entitások - TURBÓZOTT parsing
        jsonld_entities = []
        jsonld_entity_details = {}
        
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                script_content = script.string
                if not script_content:
                    continue
                    
                # Tisztítás
                script_content = script_content.strip()
                data = json.loads(script_content)
                
                entities = self._extract_entities_recursive(data)
                jsonld_entities.extend(entities)
                
                # Entitás részletek gyűjtése
                for entity in entities:
                    if entity not in jsonld_entity_details:
                        jsonld_entity_details[entity] = 0
                    jsonld_entity_details[entity] += 1
                    
            except (json.JSONDecodeError, AttributeError, TypeError):
                continue
        
        # Microdata és RDFa
        microdata_items = len(soup.find_all(attrs={"itemscope": True}))
        rdfa_items = len(soup.find_all(attrs={"typeof": True}))
        
        # Szemantikai gazdagság értékelése
        semantic_richness = self._calculate_semantic_richness(
            schema_entities, jsonld_entity_details, microdata_items, rdfa_items
        )
        
        # AI platform specifikus entitás értékelés
        ai_entity_value = self._calculate_ai_entity_value(jsonld_entity_details, schema_entities)
        
        return {
            "schema_entities": schema_entities,
            "jsonld_entities": list(set(jsonld_entities)),
            "jsonld_entity_details": jsonld_entity_details,
            "microdata_items": microdata_items,
            "rdfa_items": rdfa_items,
            "total_entities": sum(schema_entities.values()) + len(jsonld_entities) + microdata_items + rdfa_items,
            "semantic_richness": semantic_richness,
            "ai_entity_value": ai_entity_value,
            "entity_score": min(100, sum(schema_entities.values()) * 8 + 
                               len(set(jsonld_entities)) * 12 + microdata_items * 4 + 
                               semantic_richness * 0.3 + ai_entity_value * 0.2)
        }

    def _check_enhanced_content_freshness(self, soup: BeautifulSoup, text: str) -> Dict:
        """TURBÓZOTT tartalom frissesség ellenőrzése"""
        
        # Kibővített dátum meta tagek
        date_meta_selectors = [
            'meta[property^="article:"]',
            'meta[name*="date"]',
            'meta[name*="published"]', 
            'meta[name*="modified"]',
            'meta[name*="updated"]',
            'meta[property="og:updated_time"]',
            'meta[name="last-modified"]',
            'meta[name="revised"]'
        ]
        
        date_metas = []
        for selector in date_meta_selectors:
            date_metas.extend(soup.select(selector))
        
        # Fejlett dátum pattern keresés
        date_patterns = [
            # ISO formátumok
            (r'\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2})?(?:Z|[+-]\d{2}:\d{2})?', 'iso'),
            # Amerikai formátum
            (r'\d{1,2}/\d{1,2}/\d{4}', 'us'),
            # Európai formátum
            (r'\d{1,2}\.\d{1,2}\.\d{4}', 'eu'),
            # Magyar formátum
            (r'\d{4}\.\s*(?:január|február|március|április|május|június|július|augusztus|szeptember|október|november|december)\s*\d{1,2}', 'hu'),
            # Angol hónapok
            (r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}', 'en'),
            # Relatív dátumok
            (r'\b(?:today|yesterday|törtenap|ma|tegnap|\d+\s+(?:days?|napja?|weeks?|hete?|months?|hónapja?)\s+ago)\b', 'relative')
        ]
        
        date_mentions = {}
        total_date_mentions = 0
        
        for pattern, date_type in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            date_mentions[date_type] = len(matches)
            total_date_mentions += len(matches)
        
        # Frissítési indikátorok keresése
        freshness_indicators = [
            r'\b(?:friss(?:ítve|ített)|updated?|last\s+(?:modified|updated)|utolj(?:ára\s+)?(?:módosítva|frissítve))\b',
            r'\b(?:új|new|latest|legújabb|aktuális|current)\b',
            r'\b(?:nemrég|recently|lately|not\s+long\s+ago)\b',
            r'\b\d{4}(?:\.|-)(?:0[1-9]|1[0-2])(?:\.|-)(?:0[1-9]|[12]\d|3[01])\b'  # timestamp pattern
        ]
        
        freshness_signals = 0
        for pattern in freshness_indicators:
            freshness_signals += len(re.findall(pattern, text, re.IGNORECASE))
        
        # JSON-LD dátum mezők
        jsonld_dates = self._extract_jsonld_dates(soup)
        
        # Time elemek HTML5-ben
        time_elements = soup.find_all('time')
        datetime_attrs = len([t for t in time_elements if t.get('datetime')])
        
        # Schema.org publishedDate, modifiedDate
        schema_date_fields = self._check_schema_date_fields(soup)
        
        return {
            "date_meta_tags": len(date_metas),
            "date_mentions": date_mentions,
            "total_date_mentions": total_date_mentions,
            "freshness_signals": freshness_signals,
            "has_jsonld_dates": len(jsonld_dates) > 0,
            "jsonld_date_fields": jsonld_dates,
            "time_elements": len(time_elements),
            "datetime_attributes": datetime_attrs,
            "schema_date_fields": schema_date_fields,
            "freshness_score": min(100, len(date_metas) * 20 + total_date_mentions * 3 + 
                                 freshness_signals * 5 + len(jsonld_dates) * 15 + 
                                 datetime_attrs * 10 + len(schema_date_fields) * 8)
        }

    def _check_enhanced_citations(self, soup: BeautifulSoup, text: str) -> Dict:
        """TURBÓZOTT hivatkozások és idézetek ellenőrzése"""
        
        # Külső linkek részletes elemzése
        all_links = soup.find_all('a', href=True)
        external_links = []
        internal_links = []
        
        for link in all_links:
            href = link.get('href', '')
            if href.startswith(('http://', 'https://')):
                external_links.append(link)
            elif href.startswith(('#', '/', 'mailto:', 'tel:')):
                internal_links.append(link)
        
        # Hivatkozás minőség elemzése
        quality_external_links = [
            link for link in external_links 
            if any(domain in link.get('href', '') for domain in [
                'wikipedia.org', 'gov', 'edu', 'academic', 'research',
                'pubmed', 'scholar.google', 'researchgate', 'arxiv'
            ])
        ]
        
        # Idézetek és hivatkozások
        citations = soup.find_all(['cite', 'blockquote'])
        quality_citations = [
            cite for cite in citations 
            if len(cite.get_text().strip()) > 20  # Minimum length for quality
        ]
        
        # Footnotes és referenciák
        footnotes = soup.find_all(class_=re.compile(r'footnote|reference|citation|biblio', re.I))
        
        # Numerikus hivatkozások [1], [2] stb.
        numeric_refs = re.findall(r'\[\d+\]', text)
        
        # DOI és arXiv linkek
        doi_pattern = r'(?:doi:|DOI:)\s*10\.\d{4,}\/[^\s]+'
        arxiv_pattern = r'arXiv:\d{4}\.\d{4,5}'
        
        doi_links = re.findall(doi_pattern, text)
        arxiv_links = re.findall(arxiv_pattern, text)
        
        # Schema.org citation markup
        citation_schema = self._check_citation_schema(soup)
        
        # Forrás minőség indikátorok
        source_quality_indicators = [
            r'\b(?:forrás|source|references?|bibliography|irodalom)\s*:',
            r'\b(?:according\s+to|szerint|alapján|hivatkozva)\b',
            r'\b(?:study|research|kutatás|tanulmány|vizsgálat)\b',
            r'\b(?:egyetem|university|akadémia|academy|institute)\b'
        ]
        
        source_quality_score = 0
        for pattern in source_quality_indicators:
            source_quality_score += len(re.findall(pattern, text, re.IGNORECASE))
        
        return {
            "external_links": len(external_links),
            "quality_external_links": len(quality_external_links),
            "internal_links": len(internal_links),
            "citations": len(citations),
            "quality_citations": len(quality_citations),
            "footnotes": len(footnotes),
            "numeric_references": len(numeric_refs),
            "doi_links": len(doi_links),
            "arxiv_links": len(arxiv_links),
            "has_citation_schema": len(citation_schema) > 0,
            "citation_schema_types": citation_schema,
            "source_quality_indicators": source_quality_score,
            "citation_score": min(100, len(external_links) * 2 + len(quality_external_links) * 8 + 
                                 len(quality_citations) * 12 + len(footnotes) * 8 + 
                                 len(numeric_refs) * 5 + (len(doi_links) + len(arxiv_links)) * 15 + 
                                 len(citation_schema) * 20 + source_quality_score * 3)
        }

    def _check_enhanced_ai_formatting(self, soup: BeautifulSoup, text: str) -> Dict:
        """TURBÓZOTT AI-barát formázás ellenőrzése"""
        
        # Táblázatok minőségi elemzése
        tables = soup.find_all('table')
        tables_with_captions = len([t for t in tables if t.find('caption')])
        tables_with_headers = len([t for t in tables if t.find('thead') or t.find('th')])
        data_rich_tables = len([t for t in tables if len(t.find_all('tr')) >= 3])
        
        # Képek és média elemzése
        images = soup.find_all('img')
        images_with_alt = len([img for img in images if img.get('alt') and len(img.get('alt').strip()) > 3])
        images_with_title = len([img for img in images if img.get('title')])
        figures_with_captions = len(soup.find_all('figure', lambda fig: fig.find('figcaption')))
        
        # Listák minőségi elemzése
        lists = soup.find_all(['ul', 'ol'])
        lists_with_labels = len([lst for lst in lists if lst.get('aria-label') or lst.get('title')])
        nested_lists = len([lst for lst in lists if lst.find(['ul', 'ol'])])
        
        # Navigáció és struktúra
        nav_elements = len(soup.find_all(['nav', '[role="navigation"]']))
        breadcrumbs = len(soup.find_all(class_=re.compile(r'breadcrumb', re.I)))
        landmarks = len(soup.find_all(attrs={'role': re.compile(r'main|banner|navigation|complementary|contentinfo')}))
        
        # ARIA és accessibility
        aria_labels = len(soup.find_all(attrs={'aria-label': True}))
        aria_describedby = len(soup.find_all(attrs={'aria-describedby': True}))
        
        # Szemantikus HTML5 elemek
        semantic_elements = len(soup.find_all(['article', 'section', 'header', 'footer', 'aside', 'main']))
        
        # Kód formázás AI-hez
        code_quality = self._analyze_code_formatting(soup)
        
        # Step-by-step formázás
        step_formatting = self._analyze_step_formatting(soup, text)
        
        return {
            "tables": {
                "total": len(tables),
                "with_captions": tables_with_captions,
                "with_headers": tables_with_headers,
                "data_rich": data_rich_tables,
                "quality_score": self._calculate_table_quality_score(tables, tables_with_captions, tables_with_headers, data_rich_tables)
            },
            "images": {
                "total": len(images),
                "with_alt": images_with_alt,
                "with_title": images_with_title,
                "figures_with_captions": figures_with_captions,
                "quality_score": self._calculate_image_quality_score(images, images_with_alt, figures_with_captions)
            },
            "lists": {
                "total": len(lists),
                "with_labels": lists_with_labels,
                "nested": nested_lists,
                "quality_score": min(100, (lists_with_labels / max(1, len(lists))) * 50 + (nested_lists / max(1, len(lists))) * 50)
            },
            "navigation": {
                "nav_elements": nav_elements,
                "breadcrumbs": breadcrumbs,
                "landmarks": landmarks,
                "navigation_score": min(100, nav_elements * 20 + breadcrumbs * 25 + landmarks * 10)
            },
            "accessibility": {
                "aria_labels": aria_labels,
                "aria_describedby": aria_describedby,
                "semantic_elements": semantic_elements,
                "accessibility_score": min(100, aria_labels * 5 + aria_describedby * 8 + semantic_elements * 8)
            },
            "code_formatting": code_quality,
            "step_formatting": step_formatting,
            "formatting_score": self._calculate_enhanced_formatting_score(
                tables_with_captions, len(tables), images_with_alt, len(images),
                lists_with_labels, len(lists), nav_elements, breadcrumbs,
                code_quality, step_formatting, semantic_elements
            )
        }

    def _analyze_enhanced_knowledge_depth(self, text: str, soup: BeautifulSoup) -> Dict:
        """TURBÓZOTT tudás mélység elemzése"""
        
        # Alapvető metrikák
        words = text.split()
        word_count = len(words)
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Szókincs gazdagság és komplexitás
        unique_words = set(word.lower().strip('.,!?;:"()[]{}') for word in words if word.isalpha())
        vocabulary_richness = len(unique_words) / word_count if word_count > 0 else 0
        
        # Hosszú és komplex szavak
        long_words = [word for word in words if len(word) > 6]
        complex_words = [word for word in words if len(word) > 8]
        
        # Szakmai és technikai kifejezések
        technical_patterns = [
            r'\b[A-Z]{2,}\b',  # Acronyms
            r'\b\w+(?:ás|és|ség|ság|tat|tel|kor|ban|ben)\b',  # Magyar szakmai képzők
            r'\b(?:algorithm|protocol|framework|methodology|implementation|optimization)\b',  # Angol technikai
            r'\b\w+(?:ing|tion|sion|ment|ness|ity|acy|ism)\b'  # Angol szakmai képzők
        ]
        
        technical_terms = 0
        for pattern in technical_patterns:
            technical_terms += len(re.findall(pattern, text))
        
        # Számok, statisztikák, mértékegységek
        numbers = re.findall(r'\b\d+(?:[.,]\d+)?(?:%|kg|g|m|cm|mm|km|l|ml|€|$|Ft|°C|°F)?\b', text)
        percentages = re.findall(r'\b\d+(?:[.,]\d+)?%\b', text)
        ranges = re.findall(r'\b\d+(?:[.,]\d+)?\s*[-–—]\s*\d+(?:[.,]\d+)?\b', text)
        
        # Definíciók és magyarázatok
        definition_patterns = [
            r'\b(?:például|azaz|vagyis|jelentése|definíció|that\s+is|i\.e\.|e\.g\.|namely|specifically)\b',
            r'\b\w+\s+(?:azt\s+jelenti|means|refers\s+to|is\s+defined\s+as)\b',
            r':\s*[A-Z]',  # Definíció pattern
        ]
        
        definitions = 0
        for pattern in definition_patterns:
            definitions += len(re.findall(pattern, text, re.IGNORECASE))
        
        # Példák és esettanulmányok
        example_patterns = [
            r'\b(?:például|for\s+example|for\s+instance|such\s+as|like)\b',
            r'\b(?:case\s+study|esettanulmány|example|példa)\b',
            r'\b(?:consider|képzelje\s+el|imagine|suppose)\b'
        ]
        
        examples = 0
        for pattern in example_patterns:
            examples += len(re.findall(pattern, text, re.IGNORECASE))
        
        # Adatok és hivatkozások mélysége
        data_depth_indicators = [
            r'\b(?:research|kutatás|study|tanulmány|survey|felmérés|analysis|elemzés)\b',
            r'\b(?:data|adat|statistics|statisztika|findings|eredmények)\b',
            r'\b(?:according\s+to|szerint|based\s+on|alapján)\b'
        ]
        
        data_depth = 0
        for pattern in data_depth_indicators:
            data_depth += len(re.findall(pattern, text, re.IGNORECASE))
        
        # Tartalmi struktúra mélysége (HTML alapján)
        content_sections = len(soup.find_all(['section', 'article', 'div'], class_=re.compile(r'content|article|section', re.I)))
        subheadings = len(soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6']))
        
        return {
            "word_metrics": {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "avg_sentence_length": round(avg_sentence_length, 1),
                "vocabulary_richness": round(vocabulary_richness, 3),
                "long_words": len(long_words),
                "complex_words": len(complex_words)
            },
            "technical_depth": {
                "technical_terms": technical_terms,
                "numbers_statistics": len(numbers),
                "percentages": len(percentages),
                "ranges": len(ranges),
                "technical_density": round(technical_terms / word_count * 1000, 1) if word_count > 0 else 0
            },
            "explanatory_content": {
                "definitions": definitions,
                "examples": examples,
                "data_depth_indicators": data_depth,
                "explanation_ratio": round((definitions + examples) / sentence_count * 100, 1) if sentence_count > 0 else 0
            },
            "content_structure": {
                "content_sections": content_sections,
                "subheadings": subheadings,
                "structural_depth": subheadings / max(1, content_sections)
            },
            "depth_score": min(100, (word_count / 50) + (technical_terms * 2) + 
                             (len(numbers) * 3) + (definitions * 8) + 
                             (examples * 6) + (data_depth * 4) + 
                             (vocabulary_richness * 50) + (subheadings * 2))
        }

    def _detect_enhanced_conversational_elements(self, text: str, soup: BeautifulSoup) -> Dict:
        """TURBÓZOTT beszélgetős elemek detektálása"""
        
        # Közvetlen megszólítás - fejlettebb pattern-ek
        direct_address_patterns = [
            r'\b(?:ön|te|maga|önt|téged|you|your)\b',
            r'\b(?:kedves\s+(?:olvasó|látogató)|dear\s+(?:reader|visitor))\b',
            r'\b(?:ha\s+(?:ön|te|you)|if\s+you)\b'
        ]
        
        direct_address = 0
        for pattern in direct_address_patterns:
            direct_address += len(re.findall(pattern, text.lower()))
        
        # Kérdések és felkiáltások
        questions = text.count('?')
        exclamations = text.count('!')
        
        # Retorikai kérdések
        rhetorical_questions = len(re.findall(r'\b(?:vajon|ugye|nem\s+igaz|isn\'t\s+it|right|don\'t\s+you\s+think)\b.*?\?', text, re.IGNORECASE))
        
        # Beszélgetős kifejezések
        conversational_patterns = [
            r'\b(?:tudod|látod|érted|gondold|képzeld|nézd|figyelj)\b',
            r'\b(?:you\s+know|you\s+see|you\s+understand|look|listen|imagine)\b',
            r'\b(?:egyszerűen|simply|just|merely|csak|csupán)\b',
            r'\b(?:természetesen|obviously|of\s+course|clearly|nyilvánvalóan)\b'
        ]
        
        conversational_phrases = 0
        for pattern in conversational_patterns:
            conversational_phrases += len(re.findall(pattern, text.lower()))
        
        # Informális nyelvi elemek
        informal_elements = [
            r'\b(?:na|well|so|szóval|tehát|persze|sure|yeah|okay|oké)\b',
            r'\b(?:amúgy|egyébként|by\s+the\s+way|btw|incidentally)\b',
            r'\.{3}|\.\.\.',  # Three dots
            r'!\s*!\s*!',     # Multiple exclamations
        ]
        
        informal_count = 0
        for pattern in informal_elements:
            informal_count += len(re.findall(pattern, text.lower()))
        
        # Empátia és kapcsolódás
        empathy_patterns = [
            r'\b(?:értem|understand|tudom|know|érzem|feel)\b.*\b(?:hogy|that|mit|what)\b',
            r'\b(?:természetes|natural|normális|normal|érthető|understandable)\b',
            r'\b(?:segíteni|help|támogatni|support|könnyíteni|make\s+easier)\b'
        ]
        
        empathy_expressions = 0
        for pattern in empathy_patterns:
            empathy_expressions += len(re.findall(pattern, text.lower()))
        
        # Interaktív elemek
        interactive_words = len(re.findall(r'\b(?:kattints|click|válassz|choose|próbáld|try|teszteld|test)\b', text.lower()))
        
        # CTA (Call to Action) elemek
        cta_patterns = [
            r'\b(?:kattints|click|regisztrálj|sign\s+up|iratkozz\s+fel|subscribe)\b',
            r'\b(?:töltsd\s+le|download|vásárolj|buy|rendelj|order)\b',
            r'\b(?:kezdd\s+el|start|próbáld\s+ki|try\s+it|tanuld\s+meg|learn)\b'
        ]
        
        cta_elements = 0
        for pattern in cta_patterns:
            cta_elements += len(re.findall(pattern, text.lower()))
        
        # Personal pronouns és birtokos névmások
        personal_pronouns = len(re.findall(r'\b(?:én|te|ő|mi|ti|ők|i|you|he|she|we|they|my|your|his|her|our|their)\b', text.lower()))
        
        return {
            "direct_address": direct_address,
            "questions": questions,
            "exclamations": exclamations,
            "rhetorical_questions": rhetorical_questions,
            "conversational_phrases": conversational_phrases,
            "informal_elements": informal_count,
            "empathy_expressions": empathy_expressions,
            "interactive_words": interactive_words,
            "cta_elements": cta_elements,
            "personal_pronouns": personal_pronouns,
            "conversational_score": min(100, 
                direct_address * 4 + questions * 2 + exclamations * 1 + 
                rhetorical_questions * 8 + conversational_phrases * 6 + 
                informal_count * 3 + empathy_expressions * 10 + 
                interactive_words * 5 + cta_elements * 7 + 
                personal_pronouns * 0.5)
        }

    # HELPER METHODS - Számítási és segédfüggvények
    
    def _calculate_list_quality(self, ordered_lists, unordered_lists, step_lists) -> int:
        """Lista minőség számítása"""
        total_lists = len(ordered_lists) + len(unordered_lists)
        if total_lists == 0:
            return 0
        
        quality_score = 0
        
        # Ordered lists are better for AI
        quality_score += len(ordered_lists) * 15
        quality_score += len(unordered_lists) * 10
        quality_score += step_lists * 25  # Step-by-step lists are excellent
        
        # List item depth check
        for ol in ordered_lists:
            items = ol.find_all('li')
            if len(items) >= 3:  # Good length
                quality_score += 10
            if any(len(item.get_text().strip()) > 20 for item in items):  # Descriptive items
                quality_score += 5
        
        return min(100, quality_score)

    def _calculate_heading_hierarchy_score(self, headings: Dict) -> int:
        """Heading hierarchia pontszám"""
        score = 0
        
        # H1 should be exactly 1
        h1_count = headings.get('h1', 0)
        if h1_count == 1:
            score += 30
        elif h1_count == 0:
            score -= 20
        else:  # More than 1
            score -= 10
        
        # Good hierarchy progression
        for i in range(2, 6):
            current = headings.get(f'h{i}', 0)
            previous = headings.get(f'h{i-1}', 0)
            
            if current > 0 and previous == 0 and i > 2:
                score -= 10  # Skipped level
            elif current > 0:
                score += 5   # Has this level
        
        return max(0, min(100, score + 40))  # Base score + adjustments

    def _calculate_enhanced_structure_score(self, ordered_lists: int, unordered_lists: int, 
                                          list_items: int, data_tables: int, optimal_paras: int,
                                          total_paras: int, headings: Dict, descriptive_headings: int,
                                          code_blocks: int, step_indicators: int) -> int:
        """Enhanced struktúra pontszám számítása"""
        score = 0
        
        # Lists (max 25 points)
        if list_items > 0:
            score += min(25, ordered_lists * 8 + unordered_lists * 5 + (step_indicators >= 3) * 12)
        
        # Tables (max 20 points)
        if data_tables > 0:
            score += min(20, data_tables * 15)
        
        # Paragraphs (max 20 points)
        if total_paras > 0:
            para_quality = (optimal_paras / total_paras) * 20
            score += para_quality
        
        # Headings (max 20 points)
        heading_score = self._calculate_heading_hierarchy_score(headings)
        score += (heading_score / 100) * 20
        
        # Code blocks (max 10 points) - AI-k szeretik a kódpéldákat
        score += min(10, code_blocks * 5)
        
        # Step-by-step indicators (max 5 points)
        if step_indicators >= 3:
            score += 5
        
        return min(100, score)

    def _find_qa_schemas_recursive(self, data, schemas=None) -> List[Dict]:
        """Rekurzív schema keresés Q&A típusokra"""
        if schemas is None:
            schemas = []
        
        if isinstance(data, dict):
            schema_type = data.get("@type")
            if schema_type == "FAQPage":
                main_entity = data.get("mainEntity", [])
                schemas.append({
                    "type": "FAQPage",
                    "count": len(main_entity) if isinstance(main_entity, list) else 1
                })
            elif schema_type == "QAPage":
                schemas.append({"type": "QAPage", "count": 1})
            elif schema_type in ["Question", "Answer"]:
                schemas.append({"type": schema_type, "count": 1})
            
            # Rekurzív keresés
            for value in data.values():
                self._find_qa_schemas_recursive(value, schemas)
                
        elif isinstance(data, list):
            for item in data:
                self._find_qa_schemas_recursive(item, schemas)
        
        return schemas

    def _detect_structured_qa_patterns(self, soup: BeautifulSoup, text: str) -> Dict:
        """Strukturált Q&A minták detektálása"""
        patterns = {
            "numbered_qa": 0,
            "bulleted_qa": 0,
            "accordion_qa": 0,
            "definition_lists": 0
        }
        
        # Numbered Q&A
        numbered_qa = re.findall(r'\d+\.\s*(?:mi|what|how|ki|who|hol|where|mikor|when|miért|why)', text, re.IGNORECASE)
        patterns["numbered_qa"] = len(numbered_qa)
        
        # Bulleted Q&A
        bulleted_qa = re.findall(r'[•▪▫◦]\s*(?:mi|what|how|ki|who|hol|where|mikor|when|miért|why)', text, re.IGNORECASE)
        patterns["bulleted_qa"] = len(bulleted_qa)
        
        # Accordion/collapsible elements
        patterns["accordion_qa"] = len(soup.find_all(class_=re.compile(r'accordion|collapse|toggle|expand', re.I)))
        
        # Definition lists (dl, dt, dd)
        definition_lists = soup.find_all('dl')
        patterns["definition_lists"] = len(definition_lists)
        
        return patterns

    def _calculate_enhanced_qa_score(self, has_faq_schema: bool, faq_count: int, 
                                   questions_found: int, html_elements: int,
                                   answer_indicators: int, qa_pairs: int,
                                   structured_qa: Dict, ai_qa_features: Dict) -> int:
        """Enhanced Q&A pontszám számítása"""
        score = 0
        
        # Schema markup (max 30 points)
        if has_faq_schema:
            score += 20 + min(10, faq_count * 2)
        
        # Questions found (max 25 points)
        score += min(25, questions_found * 2)
        
        # HTML elements (max 20 points)
        score += min(20, html_elements * 5)
        
        # Q&A pairs (max 15 points)
        score += min(15, qa_pairs * 3)
        
        # AI-friendly features (max 10 points)
        ai_features_score = sum(ai_qa_features.values()) * 2.5
        score += min(10, ai_features_score)
        
        return min(100, score)

    def _extract_entities_recursive(self, data, entities=None) -> List[str]:
        """Rekurzív entitás kinyerés JSON-LD-ből"""
        if entities is None:
            entities = []
        
        if isinstance(data, dict):
            schema_type = data.get("@type")
            if schema_type:
                if isinstance(schema_type, list):
                    entities.extend(schema_type)
                else:
                    entities.append(schema_type)
            
            for value in data.values():
                self._extract_entities_recursive(value, entities)
                
        elif isinstance(data, list):
            for item in data:
                self._extract_entities_recursive(item, entities)
        
        return entities

    def _calculate_semantic_richness(self, schema_entities: Dict, jsonld_entities: Dict, 
                                   microdata: int, rdfa: int) -> int:
        """Szemantikai gazdagság számítása"""
        total_schema = sum(schema_entities.values())
        total_jsonld = sum(jsonld_entities.values())
        
        # Diversity bonus
        schema_diversity = len([v for v in schema_entities.values() if v > 0])
        jsonld_diversity = len(jsonld_entities.keys())
        
        richness = (total_schema + total_jsonld + microdata + rdfa + 
                   schema_diversity * 5 + jsonld_diversity * 3)
        
        return min(100, richness)

    def _calculate_ai_entity_value(self, jsonld_entities: Dict, schema_entities: Dict) -> int:
        """AI platform specifikus entitás érték"""
        high_value_entities = [
            'Person', 'Organization', 'Product', 'Article', 'HowTo', 'Recipe',
            'FAQPage', 'QAPage', 'Course', 'VideoObject', 'WebPage'
        ]
        
        value = 0
        for entity in high_value_entities:
            value += jsonld_entities.get(entity, 0) * 10
            value += schema_entities.get(entity, 0) * 8
        
        return min(100, value)

    def _extract_jsonld_dates(self, soup: BeautifulSoup) -> List[str]:
        """JSON-LD dátum mezők kinyerése"""
        date_fields = []
        scripts = soup.find_all("script", type="application/ld+json")
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                self._find_date_fields_recursive(data, date_fields)
            except (json.JSONDecodeError, AttributeError, TypeError):
                continue
        
        return list(set(date_fields))

    def _find_date_fields_recursive(self, data, date_fields) -> None:
        """Rekurzív dátum mező keresés"""
        if isinstance(data, dict):
            for key, value in data.items():
                if key in ['datePublished', 'dateModified', 'dateCreated', 'uploadDate', 'releaseDate']:
                    date_fields.append(key)
                elif isinstance(value, (dict, list)):
                    self._find_date_fields_recursive(value, date_fields)
        elif isinstance(data, list):
            for item in data:
                self._find_date_fields_recursive(item, date_fields)

    def _check_schema_date_fields(self, soup: BeautifulSoup) -> List[str]:
        """Schema.org dátum mezők ellenőrzése"""
        date_fields = []
        date_props = ['datePublished', 'dateModified', 'dateCreated']
        
        for prop in date_props:
            elements = soup.find_all(attrs={'itemprop': prop})
            if elements:
                date_fields.append(prop)
        
        return date_fields

    def _check_citation_schema(self, soup: BeautifulSoup) -> List[str]:
        """Idézet schema ellenőrzése"""
        citation_schemas = []
        scripts = soup.find_all("script", type="application/ld+json")
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                if self._has_citation_in_schema(data):
                    citation_schemas.append("Citation")
            except:
                continue
        
        return citation_schemas

    def _has_citation_in_schema(self, data) -> bool:
        """Rekurzív citation keresés schema-ban"""
        if isinstance(data, dict):
            if 'citation' in data or '@type' in data and 'citation' in str(data).lower():
                return True
            return any(self._has_citation_in_schema(v) for v in data.values())
        elif isinstance(data, list):
            return any(self._has_citation_in_schema(item) for item in data)
        return False

    def _calculate_table_quality_score(self, tables, with_captions: int, 
                                     with_headers: int, data_rich: int) -> int:
        """Táblázat minőség pontszám"""
        if not tables:
            return 100  # No tables is okay
        
        total_tables = len(tables)
        score = 0
        
        score += (with_captions / total_tables) * 30
        score += (with_headers / total_tables) * 40  
        score += (data_rich / total_tables) * 30
        
        return min(100, score)

    def _calculate_image_quality_score(self, images, with_alt: int, with_captions: int) -> int:
        """Kép minőség pontszám"""
        if not images:
            return 100  # No images is okay
        
        total_images = len(images)
        score = 0
        
        score += (with_alt / total_images) * 70     # Alt text is crucial
        score += (with_captions / total_images) * 30  # Captions are nice
        
        return min(100, score)

    def _analyze_code_formatting(self, soup: BeautifulSoup) -> Dict:
        """Kód formázás elemzése"""
        code_blocks = soup.find_all(['pre', 'code'])
        syntax_highlighted = len([block for block in code_blocks 
                                if block.get('class') and any('language' in cls or 'highlight' in cls 
                                                            for cls in block.get('class'))])
        
        return {
            "total_code_blocks": len(code_blocks),
            "syntax_highlighted": syntax_highlighted,
            "code_quality_score": min(100, len(code_blocks) * 20 + syntax_highlighted * 10)
        }

    def _analyze_step_formatting(self, soup: BeautifulSoup, text: str) -> Dict:
        """Step-by-step formázás elemzése"""
        numbered_steps = len(re.findall(r'\b(?:step\s+)?\d+[.)]\s+', text, re.IGNORECASE))
        ordered_lists_with_steps = len([ol for ol in soup.find_all('ol') 
                                      if any(re.search(r'\b(?:step|lépés)\b', li.get_text(), re.I) 
                                           for li in ol.find_all('li'))])
        
        return {
            "numbered_steps": numbered_steps,
            "step_lists": ordered_lists_with_steps,
            "step_formatting_score": min(100, numbered_steps * 10 + ordered_lists_with_steps * 20)
        }

    def _calculate_enhanced_formatting_score(self, tables_with_captions: int, total_tables: int,
                                           images_with_alt: int, total_images: int,
                                           lists_with_labels: int, total_lists: int,
                                           nav_elements: int, breadcrumbs: int,
                                           code_quality: Dict, step_formatting: Dict,
                                           semantic_elements: int) -> int:
        """Enhanced formázás pontszám számítása"""
        score = 0
        
        # Táblázatok (max 15 points)
        if total_tables > 0:
            score += (tables_with_captions / total_tables) * 15
        else:
            score += 5  # No tables penalty is small
        
        # Képek (max 20 points)
        if total_images > 0:
            score += (images_with_alt / total_images) * 20
        else:
            score += 10  # No images is okay
        
        # Listák (max 10 points)
        if total_lists > 0:
            score += (lists_with_labels / total_lists) * 10
        else:
            score += 5
        
        # Navigáció (max 15 points)
        score += min(15, nav_elements * 8 + breadcrumbs * 7)
        
        # Kód formázás (max 15 points)
        score += (code_quality.get('code_quality_score', 0) / 100) * 15
        
        # Step formázás (max 10 points)
        score += (step_formatting.get('step_formatting_score', 0) / 100) * 10
        
        # Szemantikus elemek (max 15 points)
        score += min(15, semantic_elements * 3)
        
        return min(100, score)

    # MAIN API METHODS

    def get_ai_readiness_summary(self, metrics: Dict) -> Dict:
        """TURBÓZOTT AI-readiness összefoglaló - fejlett súlyozással és kategorizálással"""
        
        # Extract individual scores with enhanced error handling
        scores = {}
        score_weights = {}
        
        # Enhanced scoring system with dynamic weights
        metric_configs = {
            "structure": {
                "path": ["content_structure", "structure_score"],
                "weight": 0.20,
                "ai_importance": "high"  # AI-k szeretik a jó struktúrát
            },
            "qa_format": {
                "path": ["qa_format", "qa_score"], 
                "weight": 0.18,
                "ai_importance": "critical"  # Q&A formátum nagyon fontos
            },
            "entities": {
                "path": ["entity_markup", "entity_score"],
                "weight": 0.15,
                "ai_importance": "high"
            },
            "freshness": {
                "path": ["content_freshness", "freshness_score"],
                "weight": 0.08,
                "ai_importance": "medium"
            },
            "citations": {
                "path": ["citation_readiness", "citation_score"], 
                "weight": 0.12,
                "ai_importance": "high"
            },
            "formatting": {
                "path": ["ai_friendly_formatting", "formatting_score"],
                "weight": 0.15,
                "ai_importance": "high"
            },
            "depth": {
                "path": ["knowledge_depth", "depth_score"],
                "weight": 0.10,
                "ai_importance": "medium"
            },
            "conversational": {
                "path": ["conversational_elements", "conversational_score"],
                "weight": 0.02,
                "ai_importance": "low"  # Kevésbé fontos, de hasznos
            }
        }
        
        # Extract scores safely
        for key, config in metric_configs.items():
            try:
                value = metrics
                for path_part in config["path"]:
                    value = value.get(path_part, {})
                
                if isinstance(value, (int, float)):
                    scores[key] = max(0, min(100, value))  # Clamp to 0-100
                    score_weights[key] = config["weight"]
                else:
                    scores[key] = 0
                    score_weights[key] = config["weight"]
                    
            except (AttributeError, TypeError, KeyError):
                scores[key] = 0
                score_weights[key] = config["weight"]
        
        # Calculate weighted average
        total_score = sum(scores[key] * score_weights[key] for key in scores)
        
        # AI enhancement bonus (if available)
        enhancement_bonus = 0
        if metrics.get("ai_content_evaluation"):
            enhancement_bonus = 5  # Bonus for AI-enhanced analysis
        
        final_score = min(100, total_score + enhancement_bonus)
        
        return {
            "individual_scores": scores,
            "score_weights": score_weights,
            "weighted_average": round(final_score, 1),
            "level": self._get_enhanced_readiness_level(final_score),
            "category_performance": self._analyze_category_performance(scores),
            "top_strengths": self._get_top_areas(scores, top=True),
            "improvement_areas": self._get_top_areas(scores, top=False),
            "ai_optimization_suggestions": self._generate_ai_optimization_suggestions(scores, metric_configs),
            "score_breakdown": {
                "excellent": len([s for s in scores.values() if s >= 80]),
                "good": len([s for s in scores.values() if 60 <= s < 80]),
                "fair": len([s for s in scores.values() if 40 <= s < 60]),
                "poor": len([s for s in scores.values() if s < 40])
            }
        }

    def _get_enhanced_readiness_level(self, score: float) -> str:
        """Enhanced AI-readiness szint meghatározása"""
        if score >= 85:
            return "Kiváló - AI platformokra optimalizált"
        elif score >= 70:
            return "Jó - Kisebb finomhangolással tökéletes"
        elif score >= 55:
            return "Közepes - Jelentős fejlesztések szükségesek"
        elif score >= 40:
            return "Fejlesztendő - Alapvető optimalizálás szükséges"
        else:
            return "Kritikus - Teljes átdolgozás javasolt"

    def _analyze_category_performance(self, scores: Dict) -> Dict:
        """Kategória teljesítmény elemzése"""
        categories = {
            "structural": ["structure", "formatting"],
            "content": ["qa_format", "depth", "conversational"], 
            "semantic": ["entities", "citations"],
            "technical": ["freshness"]
        }
        
        category_scores = {}
        for category, metrics in categories.items():
            category_score = statistics.mean([scores.get(metric, 0) for metric in metrics])
            category_scores[category] = round(category_score, 1)
        
        return category_scores

    def _generate_ai_optimization_suggestions(self, scores: Dict, configs: Dict) -> List[Dict]:
        """AI optimalizálási javaslatok generálása"""
        suggestions = []
        
        for metric, score in scores.items():
            config = configs.get(metric, {})
            importance = config.get("ai_importance", "medium")
            
            if score < 60:  # Needs improvement
                priority = "high" if importance == "critical" else "medium" if importance == "high" else "low"
                
                suggestion = {
                    "metric": metric,
                    "current_score": score,
                    "priority": priority,
                    "suggestion": self._get_specific_suggestion(metric, score),
                    "expected_improvement": self._estimate_improvement_potential(metric, score),
                    "ai_importance": importance
                }
                suggestions.append(suggestion)
        
        # Sort by priority and potential impact
        priority_order = {"high": 3, "medium": 2, "low": 1}
        suggestions.sort(key=lambda x: (priority_order.get(x["priority"], 0), x["expected_improvement"]), reverse=True)
        
        return suggestions[:5]  # Top 5 suggestions

    def _get_specific_suggestion(self, metric: str, score: float) -> str:
        """Metric-specifikus javaslatok"""
        suggestions = {
            "structure": "Hozz létre számozott listákat és javítsd a heading hierarchiát. AI-k jobban értik a strukturált tartalmat.",
            "qa_format": "Implementálj FAQ schema markup-ot és hozz létre Q&A szekciót. Ez kritikus az AI platformoknak.",
            "entities": "Adj hozzá Schema.org markup-ot személyekhez, helyekhez és termékekhez. Segíti az AI megértést.",
            "freshness": "Adj hozzá publikálási és módosítási dátumokat. Friss tartalom magasabb prioritást kap.",
            "citations": "Hivatkozz külső forrásokra és adj hozzá idézeteket. Növeli a tartalom hitelességét.",
            "formatting": "Javítsd a képek alt szövegeit és add hozzá a táblázat feliratokat. AI-barát formázás.",
            "depth": "Bővítsd ki a tartalmat példákkal és részletes magyarázatokkal. Mélyebb tudás jobb AI értékelést ad.",
            "conversational": "Használj kérdéseket és közvetlen megszólítást. Beszélgetős stílus jobban működik chatbotokkal."
        }
        
        return suggestions.get(metric, "Általános optimalizálás szükséges ezen a területen.")

    def _estimate_improvement_potential(self, metric: str, current_score: float) -> int:
        """Fejlesztési potenciál becslése"""
        max_potential = 100 - current_score
        
        # Metric-specific multipliers based on how easy they are to improve
        difficulty_multipliers = {
            "structure": 0.8,      # Relatively easy
            "qa_format": 0.9,      # Easy with schema
            "entities": 0.7,       # Requires technical knowledge
            "freshness": 0.9,      # Very easy
            "citations": 0.6,      # Requires content work
            "formatting": 0.8,     # Technical but straightforward  
            "depth": 0.5,          # Content-heavy
            "conversational": 0.7  # Style change needed
        }
        
        multiplier = difficulty_multipliers.get(metric, 0.6)
        return round(max_potential * multiplier)

    def _get_top_areas(self, scores: Dict, top: bool = True) -> List[Dict]:
        """Legjobb/leggyengébb területek részletes elemzéssel"""
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=top)
        
        areas = []
        for area, score in sorted_scores[:3]:
            areas.append({
                "area": area,
                "score": score,
                "level": self._get_area_level(score),
                "description": self._get_area_description(area)
            })
        
        return areas

    def _get_area_level(self, score: float) -> str:
        """Terület szint meghatározása"""
        if score >= 80:
            return "Kiváló"
        elif score >= 60:
            return "Jó" 
        elif score >= 40:
            return "Közepes"
        else:
            return "Gyenge"

    def _get_area_description(self, area: str) -> str:
        """Terület leírása"""
        descriptions = {
            "structure": "Tartalom strukturáltsága és szervezettsége",
            "qa_format": "Kérdés-válasz formátum és FAQ elemek",
            "entities": "Szemantikus jelölések és entitások", 
            "freshness": "Tartalom frissessége és időszerűsége",
            "citations": "Hivatkozások és források megléte",
            "formatting": "AI-barát formázás és hozzáférhetőség",
            "depth": "Tudás mélysége és részletessége",
            "conversational": "Beszélgetős elemek és interaktivitás"
        }
        
        return descriptions.get(area, "Ismeretlen terület")