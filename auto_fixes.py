import re
import json
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from string import Template
from datetime import datetime


class AutoFixGenerator:
    """Enhanced automatikus javítási javaslatok generálása - Turbózott verzió"""
    
    def __init__(self):
        # Bővített meta template-ek iparág-specifikus variánsokkal
        self.meta_templates = {
            "title": {
                "template": "<title>{title}</title>",
                "optimal_length": (30, 60),
                "industry_patterns": {
                    "ecommerce": [
                        "{product} - {brand} | Legjobb Ár Garancia",
                        "{category} Online - {brand} Webáruház",
                        "{product} Vásárlás | {discount}% Kedvezmény - {brand}"
                    ],
                    "blog": [
                        "{topic} - Teljes Útmutató {year}",
                        "Top {number} {topic} Tipp | {brand} Blog",
                        "{topic}: Amit Tudnod Kell [{year} Frissítve]"
                    ],
                    "service": [
                        "{service} Szakértők - {location} | {brand}",
                        "Professzionális {service} - Azonnali Árajánlat",
                        "{brand} - {service} Megoldások | Garancia"
                    ],
                    "corporate": [
                        "{company} - {tagline}",
                        "{company} | {industry} Vezető Vállalat",
                        "{company} - Innováció és Megbízhatóság {year} Óta"
                    ]
                }
            },
            "description": {
                "template": '<meta name="description" content="{description}">',
                "optimal_length": (120, 160),
                "industry_patterns": {
                    "ecommerce": [
                        "⭐ {product} széles választékban, kedvező áron. ✓ Ingyenes szállítás ✓ 30 napos visszaküldés ✓ Garancia. Rendelj most!",
                        "Fedezd fel {category} kínálatunkat! {number}+ termék raktárról, azonnali szállítás. Hivatalos forgalmazó, eredeti termékek.",
                    ],
                    "blog": [
                        "Részletes {topic} útmutató szakértőktől. Gyakorlati tippek, lépésről-lépésre oktatóanyagok és valós példák. Olvasd el most!",
                        "Minden amit {topic} témában tudni érdemes. Friss tartalom, szakmai elemzések, hasznos tanácsok {year}-ben."
                    ],
                    "service": [
                        "Professzionális {service} szolgáltatások {location} területén. ✓ {years}+ év tapasztalat ✓ Ingyenes felmérés ✓ Garancia",
                        "Keresel megbízható {service} szakembert? Certified szakértők, versenyképes árak, gyors kivitelezés. Kérj árajánlatot!"
                    ]
                }
            }
        }
        
        # Jelentősen bővített schema template-ek
        self.schema_templates = self._initialize_schema_templates()
        
        # Platform-specifikus követelmények részletesen
        self.platform_requirements = self._initialize_platform_requirements()
        
        # Kulcsszó adatbázis magyar és angol nyelven
        self.keywords_db = self._initialize_keywords_database()
        
        # Fix prioritás súlyok (impact vs effort)
        self.priority_weights = {
            "critical": {"impact": 10, "effort": 1, "roi": 10},
            "high": {"impact": 8, "effort": 3, "roi": 2.67},
            "medium": {"impact": 5, "effort": 5, "roi": 1},
            "low": {"impact": 2, "effort": 8, "roi": 0.25}
        }
    
    def _initialize_schema_templates(self) -> Dict:
        """Bővített schema template készlet inicializálása"""
        return {
            "organization": Template("""{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "$company_name",
  "alternateName": "$company_alt_name",
  "url": "$website_url",
  "logo": "$logo_url",
  "description": "$company_description",
  "foundingDate": "$founding_date",
  "founders": [{
    "@type": "Person",
    "name": "$founder_name"
  }],
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "$street_address",
    "addressLocality": "$city",
    "addressRegion": "$region",
    "postalCode": "$postal_code",
    "addressCountry": "$country"
  },
  "contactPoint": [{
    "@type": "ContactPoint",
    "telephone": "$phone",
    "contactType": "customer service",
    "availableLanguage": ["Hungarian", "English"],
    "areaServed": "$area_served"
  }],
  "sameAs": [
    "$facebook_url",
    "$linkedin_url",
    "$twitter_url",
    "$instagram_url"
  ],
  "taxID": "$tax_id",
  "vatID": "$vat_id"
}"""),
            
            "localBusiness": Template("""{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "$business_name",
  "image": "$image_url",
  "priceRange": "$price_range",
  "@id": "$business_id",
  "url": "$website_url",
  "telephone": "$phone",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "$street_address",
    "addressLocality": "$city",
    "addressRegion": "$region",
    "postalCode": "$postal_code",
    "addressCountry": "$country"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": $latitude,
    "longitude": $longitude
  },
  "openingHoursSpecification": [{
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    "opens": "09:00",
    "closes": "18:00"
  }],
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "$rating_value",
    "reviewCount": "$review_count"
  }
}"""),
            
            "product": Template("""{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "$product_name",
  "image": ["$image1", "$image2", "$image3"],
  "description": "$product_description",
  "sku": "$sku",
  "mpn": "$mpn",
  "brand": {
    "@type": "Brand",
    "name": "$brand_name"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "$rating",
    "reviewCount": "$review_count"
  },
  "offers": {
    "@type": "Offer",
    "url": "$product_url",
    "priceCurrency": "$currency",
    "price": "$price",
    "priceValidUntil": "$price_valid_until",
    "availability": "https://schema.org/InStock",
    "seller": {
      "@type": "Organization",
      "name": "$seller_name"
    },
    "shippingDetails": {
      "@type": "OfferShippingDetails",
      "shippingRate": {
        "@type": "MonetaryAmount",
        "value": "$shipping_cost",
        "currency": "$currency"
      },
      "deliveryTime": {
        "@type": "ShippingDeliveryTime",
        "businessDays": {
          "@type": "QuantitativeValue",
          "minValue": 1,
          "maxValue": 3
        }
      }
    }
  }
}"""),
            
            "faq": Template("""{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [$faq_items]
}"""),
            
            "howto": Template("""{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "$howto_title",
  "description": "$howto_description",
  "image": "$howto_image",
  "totalTime": "PT$total_time",
  "estimatedCost": {
    "@type": "MonetaryAmount",
    "currency": "$currency",
    "value": "$cost"
  },
  "supply": [$supplies],
  "tool": [$tools],
  "step": [$steps]
}"""),
            
            "article": Template("""{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "$headline",
  "alternativeHeadline": "$alt_headline",
  "image": "$article_image",
  "author": {
    "@type": "Person",
    "name": "$author_name",
    "url": "$author_url"
  },
  "publisher": {
    "@type": "Organization",
    "name": "$publisher_name",
    "logo": {
      "@type": "ImageObject",
      "url": "$publisher_logo"
    }
  },
  "datePublished": "$publish_date",
  "dateModified": "$modified_date",
  "description": "$article_description",
  "articleBody": "$article_body",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "$article_url"
  },
  "keywords": "$keywords",
  "articleSection": "$section",
  "wordCount": $word_count
}"""),
            
            "event": Template("""{
  "@context": "https://schema.org",
  "@type": "Event",
  "name": "$event_name",
  "startDate": "$start_date",
  "endDate": "$end_date",
  "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
  "eventStatus": "https://schema.org/EventScheduled",
  "location": {
    "@type": "Place",
    "name": "$location_name",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "$street_address",
      "addressLocality": "$city",
      "addressRegion": "$region",
      "postalCode": "$postal_code",
      "addressCountry": "$country"
    }
  },
  "image": "$event_image",
  "description": "$event_description",
  "offers": {
    "@type": "Offer",
    "url": "$ticket_url",
    "price": "$price",
    "priceCurrency": "$currency",
    "availability": "https://schema.org/InStock",
    "validFrom": "$valid_from"
  },
  "performer": {
    "@type": "Person",
    "name": "$performer_name"
  },
  "organizer": {
    "@type": "Organization",
    "name": "$organizer_name",
    "url": "$organizer_url"
  }
}"""),
            
            "recipe": Template("""{
  "@context": "https://schema.org",
  "@type": "Recipe",
  "name": "$recipe_name",
  "image": ["$image1", "$image2"],
  "author": {
    "@type": "Person",
    "name": "$author_name"
  },
  "datePublished": "$publish_date",
  "description": "$recipe_description",
  "prepTime": "PT$prep_time",
  "cookTime": "PT$cook_time",
  "totalTime": "PT$total_time",
  "keywords": "$keywords",
  "recipeYield": "$servings",
  "recipeCategory": "$category",
  "recipeCuisine": "$cuisine",
  "nutrition": {
    "@type": "NutritionInformation",
    "calories": "$calories calories"
  },
  "recipeIngredient": [$ingredients],
  "recipeInstructions": [$instructions],
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "$rating",
    "ratingCount": "$rating_count"
  }
}"""),
            
            "course": Template("""{
  "@context": "https://schema.org",
  "@type": "Course",
  "name": "$course_name",
  "description": "$course_description",
  "provider": {
    "@type": "Organization",
    "name": "$provider_name",
    "sameAs": "$provider_url"
  },
  "educationalCredentialAwarded": "$credential",
  "hasCourseInstance": {
    "@type": "CourseInstance",
    "courseMode": "online",
    "duration": "$duration",
    "startDate": "$start_date",
    "endDate": "$end_date",
    "offers": {
      "@type": "Offer",
      "price": "$price",
      "priceCurrency": "$currency",
      "availability": "https://schema.org/InStock"
    }
  }
}"""),
            
            "softwareApplication": Template("""{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "$app_name",
  "operatingSystem": "$os",
  "applicationCategory": "$category",
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "$rating",
    "ratingCount": "$rating_count"
  },
  "offers": {
    "@type": "Offer",
    "price": "$price",
    "priceCurrency": "$currency"
  },
  "screenshot": "$screenshot_url",
  "featureList": "$features",
  "softwareVersion": "$version",
  "fileSize": "$file_size",
  "softwareRequirements": "$requirements"
}"""),
            
            "breadcrumb": Template("""{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [{
    "@type": "ListItem",
    "position": 1,
    "name": "Főoldal",
    "item": "$homepage_url"
  },{
    "@type": "ListItem",
    "position": 2,
    "name": "$category_name",
    "item": "$category_url"
  },{
    "@type": "ListItem",
    "position": 3,
    "name": "$page_name",
    "item": "$page_url"
  }]
}"""),
            
            "searchAction": Template("""{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "url": "$website_url",
  "potentialAction": {
    "@type": "SearchAction",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": "$search_url?q={search_term_string}"
    },
    "query-input": "required name=search_term_string"
  }
}""")
        }
    
    def _initialize_platform_requirements(self) -> Dict:
        """Platform-specifikus követelmények részletes meghatározása"""
        return {
            "chatgpt": {
                "must_have": [
                    "Számozott lépések vagy útmutatók",
                    "Világos Q&A formátum",
                    "Gyakorlati példák kóddal",
                    "Összefoglaló szakaszok",
                    "Tiszta heading hierarchia"
                ],
                "nice_to_have": [
                    "Összehasonlító táblázatok",
                    "Pro/kontra listák",
                    "TL;DR szakaszok",
                    "Definíciók és magyarázatok",
                    "Kapcsolódó témák linkjei"
                ],
                "avoid": [
                    "Túl hosszú bekezdések",
                    "Strukturálatlan szövegfalak",
                    "Kontextus nélküli információk"
                ]
            },
            "claude": {
                "must_have": [
                    "Részletes kontextus és háttér",
                    "Tudományos hivatkozások",
                    "Hosszú, átfogó tartalom",
                    "Szakmai terminológia magyarázattal",
                    "Etikai szempontok említése"
                ],
                "nice_to_have": [
                    "Történelmi kontextus",
                    "Különböző nézőpontok",
                    "Mélyreható elemzések",
                    "Esettanulmányok",
                    "Filozófiai megközelítések"
                ],
                "avoid": [
                    "Felületes kezelés",
                    "Egyoldalú megközelítés",
                    "Kontextus hiánya"
                ]
            },
            "gemini": {
                "must_have": [
                    "Friss, aktuális információk",
                    "Rich media integráció",
                    "Strukturált adatok (schema)",
                    "Mobile-optimalizált tartalom",
                    "Google szolgáltatások integrációja"
                ],
                "nice_to_have": [
                    "YouTube videó beágyazások",
                    "Google Maps integráció",
                    "Interaktív elemek",
                    "AMP kompatibilitás",
                    "Voice search optimalizáció"
                ],
                "avoid": [
                    "Elavult információk",
                    "Desktop-only tartalom",
                    "Lassú betöltési idő"
                ]
            },
            "bing_chat": {
                "must_have": [
                    "Külső forrásokra hivatkozások",
                    "Friss hírek és események",
                    "Microsoft termék integráció",
                    "Faktaellenőrzés jelzései",
                    "Helyi információk"
                ],
                "nice_to_have": [
                    "LinkedIn integráció",
                    "GitHub kapcsolatok",
                    "Academic források",
                    "Hivatalos dokumentumok",
                    "Iparági jelentések"
                ],
                "avoid": [
                    "Ellenőrizetlen állítások",
                    "Forrás nélküli adatok",
                    "Spekulatív tartalom"
                ]
            }
        }
    
    def _initialize_keywords_database(self) -> Dict:
        """Kulcsszó adatbázis különböző iparágakhoz"""
        return {
            "ecommerce": {
                "hu": ["vásárlás", "webshop", "kedvezmény", "akció", "ingyenes szállítás", 
                       "garancia", "minőség", "eredeti", "raktáron", "expressz", "visszaküldés"],
                "en": ["buy", "shop", "discount", "sale", "free shipping", "warranty", 
                       "quality", "original", "in stock", "express", "returns"]
            },
            "service": {
                "hu": ["szolgáltatás", "szakértő", "tanácsadás", "árajánlat", "garancia",
                       "tapasztalat", "minősített", "gyors", "megbízható", "professzionális"],
                "en": ["service", "expert", "consulting", "quote", "guarantee",
                       "experience", "certified", "fast", "reliable", "professional"]
            },
            "blog": {
                "hu": ["útmutató", "hogyan", "tippek", "trükkök", "oktatóanyag",
                       "lépésről lépésre", "kezdőknek", "haladóknak", "példa", "sablon"],
                "en": ["guide", "how to", "tips", "tricks", "tutorial",
                       "step by step", "beginners", "advanced", "example", "template"]
            },
            "corporate": {
                "hu": ["vállalat", "cég", "innováció", "megoldás", "partner",
                       "vezető", "szakmai", "üzleti", "stratégia", "fejlesztés"],
                "en": ["company", "corporation", "innovation", "solution", "partner",
                       "leading", "professional", "business", "strategy", "development"]
            }
        }
    
    def generate_all_fixes(self, analysis_result: Dict, url: str) -> Dict:
        """Enhanced összes automatikus javítás generálása"""
        
        if not analysis_result or not isinstance(analysis_result, dict):
            return self._get_empty_fixes_structure()
        
        try:
            # URL és tartalom elemzés
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            path = parsed_url.path.lower()
            
            # Oldal típus felismerése
            page_type = self._detect_page_type(url, path, analysis_result)
            industry = self._detect_industry(domain, analysis_result)
            
            # Enhanced javítások generálása
            fixes = {
                "critical_fixes": self._generate_critical_fixes(analysis_result, url, page_type, industry),
                "seo_improvements": self._generate_seo_improvements(analysis_result, url, page_type, industry),
                "schema_suggestions": self._generate_schema_fixes(analysis_result, url, page_type, industry),
                "content_optimizations": self._generate_content_fixes(analysis_result, page_type, industry),
                "technical_fixes": self._generate_technical_fixes(analysis_result, url),
                "ai_readiness_fixes": self._generate_ai_fixes(analysis_result, page_type, industry),
                "implementation_guide": self._create_implementation_guide(analysis_result),
                "quick_wins": self._identify_quick_wins(analysis_result, url, page_type)
            }
            
            # ROI-alapú prioritizálás
            fixes["prioritized_actions"] = self._prioritize_fixes_by_roi(fixes)
            
            # Platform kombinációk kezelése
            fixes["platform_bundles"] = self._create_platform_bundles(analysis_result)
            
            return fixes
            
        except Exception as e:
            return self._get_empty_fixes_structure(str(e))
    
    def _detect_page_type(self, url: str, path: str, analysis: Dict) -> str:
        """Intelligens oldaltípus felismerés"""
        
        # URL path alapú detektálás
        if any(x in path for x in ['product', 'termek', 'p/', 'item']):
            return 'product'
        elif any(x in path for x in ['category', 'kategoria', 'c/', 'shop']):
            return 'category'
        elif any(x in path for x in ['blog', 'article', 'cikk', 'post', 'hirek', 'news']):
            return 'blog'
        elif any(x in path for x in ['about', 'rolunk', 'about-us', 'company']):
            return 'about'
        elif any(x in path for x in ['contact', 'kapcsolat', 'elerhetoseg']):
            return 'contact'
        elif any(x in path for x in ['service', 'szolgaltatas', 'services']):
            return 'service'
        elif path == '/' or path == '':
            return 'homepage'
        
        # Tartalom alapú detektálás
        content_quality = analysis.get('content_quality', {})
        word_count = content_quality.get('readability', {}).get('word_count', 0)
        
        if word_count > 1500:
            return 'blog'
        elif word_count < 300:
            return 'landing'
        
        # Schema alapú detektálás
        schema_data = analysis.get('schema', {})
        schema_count = schema_data.get('count', {})
        
        if schema_count.get('Product', 0) > 0:
            return 'product'
        elif schema_count.get('Article', 0) > 0:
            return 'blog'
        elif schema_count.get('LocalBusiness', 0) > 0:
            return 'local'
        
        return 'general'
    
    def _detect_industry(self, domain: str, analysis: Dict) -> str:
        """Iparág felismerése domain és tartalom alapján"""
        
        domain_lower = domain.lower()
        
        # Domain alapú felismerés
        ecommerce_indicators = ['shop', 'bolt', 'store', 'webshop', 'vasarlas', 'rendeles']
        if any(ind in domain_lower for ind in ecommerce_indicators):
            return 'ecommerce'
        
        blog_indicators = ['blog', 'news', 'hirek', 'magazine', 'journal']
        if any(ind in domain_lower for ind in blog_indicators):
            return 'blog'
        
        # Tartalom alapú felismerés
        content = analysis.get('content_quality', {})
        keywords = content.get('keyword_analysis', {}).get('top_keywords', [])
        
        if keywords:
            keyword_text = ' '.join([k[0] if isinstance(k, list) else str(k) for k in keywords[:20]])
            
            if any(word in keyword_text.lower() for word in ['termék', 'vásárlás', 'kosár', 'rendel']):
                return 'ecommerce'
            elif any(word in keyword_text.lower() for word in ['szolgáltatás', 'ajánlat', 'konzultáció']):
                return 'service'
            elif any(word in keyword_text.lower() for word in ['cikk', 'útmutató', 'hogyan', 'tipp']):
                return 'blog'
        
        return 'corporate'
    
    def _generate_critical_fixes(self, analysis: Dict, url: str, page_type: str, industry: str) -> List[Dict]:
        """Enhanced kritikus hibák javítása"""
        critical_fixes = []
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        meta_data = analysis.get("meta_and_headings", {})
        
        # Enhanced Title javítás
        title = meta_data.get("title")
        if not title:
            suggested_title = self._generate_intelligent_title(domain, page_type, industry, analysis)
            
            critical_fixes.append({
                "issue": "Hiányzó title tag",
                "severity": "critical",
                "impact": "90% forgalomvesztés potenciál - AI platformok nem tudják azonosítani az oldalt",
                "fix_code": f'<title>{suggested_title}</title>',
                "explanation": "A title a legfontosabb SEO és AI elem. Közvetlenül befolyásolja a CTR-t és az AI megértést.",
                "estimated_time": "2 perc",
                "implementation": "A <head> szekcióban, lehetőleg az első meta elem legyen",
                "expected_improvement": "+15-25% organic traffic 30 napon belül",
                "testing_method": "Google Search Console és AI platform tesztek"
            })
        elif len(title) < 30 or len(title) > 60:
            optimized_title = self._optimize_existing_title(title, page_type, industry)
            
            critical_fixes.append({
                "issue": f"Nem optimális title hossz ({len(title)} karakter)",
                "severity": "high",
                "impact": "Csökkent CTR és AI relevancia",
                "current_title": title,
                "optimized_title": optimized_title,
                "fix_code": f'<title>{optimized_title}</title>',
                "explanation": f"Jelenlegi: {len(title)} kar. Optimális: 30-60 kar. AI platformok preferálják a tömör, kulcsszódús címeket.",
                "estimated_time": "5 perc",
                "implementation": "Cseréld le a jelenlegi title tag-et",
                "expected_improvement": "+5-10% CTR javulás"
            })
        
        # Enhanced Description javítás
        description = meta_data.get("description")
        if not description:
            suggested_desc = self._generate_intelligent_description(domain, page_type, industry, analysis, title)
            
            critical_fixes.append({
                "issue": "Hiányzó meta description",
                "severity": "critical",
                "impact": "50% alacsonyabb CTR, AI platformok nem tudják összefoglalni az oldalt",
                "fix_code": f'<meta name="description" content="{suggested_desc}">',
                "explanation": "A description befolyásolja a CTR-t és az AI snippet generálást. Call-to-action szükséges.",
                "estimated_time": "3 perc",
                "implementation": "Head szekcióban, title után helyezd el",
                "expected_improvement": "+10-15% CTR a SERP-ben",
                "character_count": len(suggested_desc),
                "includes_cta": True
            })
        
        # Enhanced H1 elemzés
        h1_count = meta_data.get("h1_count", 0)
        h1_texts = meta_data.get("h1_texts", [])
        
        if h1_count == 0:
            suggested_h1 = self._generate_h1_from_context(title, page_type, industry)
            
            critical_fixes.append({
                "issue": "Hiányzó H1 elem",
                "severity": "critical",
                "impact": "AI platformok nem tudják azonosítani a fő témát, -30% semantic relevance",
                "fix_code": f'<h1>{suggested_h1}</h1>',
                "explanation": "H1 az oldal fő témáját jelöli. AI rendszerek ezt használják tartalom megértéshez.",
                "estimated_time": "1 perc",
                "implementation": "A main content első eleme legyen, vizuálisan prominens",
                "seo_best_practice": "Tartalmazza a fő kulcsszót, de ne legyen azonos a title-lel",
                "ai_recommendation": "Használj természetes, kérdés-alapú megfogalmazást"
            })
        elif h1_count > 1:
            critical_fixes.append({
                "issue": f"Túl sok H1 elem ({h1_count} db)",
                "severity": "high",
                "impact": "Zavaró struktúra AI és keresőmotorok számára, -15% topical authority",
                "current_h1s": h1_texts[:3],
                "fix_code": self._generate_heading_hierarchy_fix(h1_texts),
                "explanation": "Csak 1 H1 legyen oldalanként. A többi legyen H2-H6 logikus hierarchiában.",
                "estimated_time": "10 perc",
                "implementation": "Első H1 megtartása, többi átalakítása H2-vé vagy H3-má",
                "hierarchy_suggestion": self._suggest_heading_hierarchy(h1_texts)
            })
        
        # Robots.txt kritikus hiba
        if not analysis.get('robots_txt', {}).get('can_fetch'):
            critical_fixes.append({
                "issue": "Robots.txt blokkolja az oldalt",
                "severity": "critical",
                "impact": "Az oldal láthatatlan keresőmotorok és AI számára",
                "fix_code": self._generate_robots_txt_fix(url),
                "explanation": "A robots.txt jelenleg tiltja az indexelést. Sürgős javítás szükséges!",
                "estimated_time": "5 perc",
                "implementation": "Módosítsd a robots.txt fájlt a gyökérkönyvtárban",
                "warning": "⚠️ Ez akadályozza az összes AI platform elérést!"
            })
        
        return critical_fixes
    
    def _generate_seo_improvements(self, analysis: Dict, url: str, page_type: str, industry: str) -> List[Dict]:
        """Enhanced SEO fejlesztések kontextus-alapú javaslatokkal"""
        seo_fixes = []
        
        meta_data = analysis.get("meta_and_headings", {})
        
        # Keyword optimalizáció
        content_quality = analysis.get('content_quality', {})
        keyword_data = content_quality.get('keyword_analysis', {})
        
        if keyword_data:
            keyword_optimization = self._analyze_keyword_optimization(keyword_data, industry, page_type)
            if keyword_optimization['needs_improvement']:
                seo_fixes.append({
                    "issue": "Kulcsszó optimalizáció szükséges",
                    "current_density": keyword_optimization['current_density'],
                    "optimal_density": keyword_optimization['optimal_density'],
                    "missing_keywords": keyword_optimization['missing_keywords'],
                    "suggestion": keyword_optimization['suggestion'],
                    "fix_code": keyword_optimization['implementation_example'],
                    "impact": "Jobb tematikus relevancia AI platformok számára",
                    "estimated_improvement": "+20% topical authority score"
                })
        
        # Rich Snippets optimalizáció
        if not meta_data.get("has_og_tags"):
            og_tags = self._generate_comprehensive_og_tags(url, meta_data, page_type, industry)
            
            seo_fixes.append({
                "issue": "Hiányzó Open Graph és social media meta tagek",
                "impact": "Gyenge social media megjelenés, AI platformok nem tudják preview-zni",
                "fix_code": og_tags['code'],
                "implementation": "Teljes social media tag készlet a head szekcióban",
                "includes": og_tags['includes'],
                "platforms_benefiting": ["Facebook", "Twitter", "LinkedIn", "Slack", "Discord"],
                "expected_improvement": "3x jobb social engagement"
            })
        
        # Semantic HTML5 struktúra
        semantic_analysis = self._analyze_semantic_structure(analysis)
        if semantic_analysis['needs_improvement']:
            seo_fixes.append({
                "issue": "Hiányos szemantikus HTML5 struktúra",
                "missing_elements": semantic_analysis['missing_elements'],
                "suggestion": "Használj szemantikus HTML5 elemeket a jobb AI megértéshez",
                "fix_code": semantic_analysis['example_structure'],
                "impact": "AI platformok jobban értelmezik a tartalom struktúrát",
                "implementation_guide": semantic_analysis['guide']
            })
        
        # Internal linking optimalizáció
        internal_linking = self._analyze_internal_linking(analysis, page_type)
        if internal_linking['needs_improvement']:
            seo_fixes.append({
                "issue": "Belső linkelés optimalizálása szükséges",
                "current_internal_links": internal_linking['current_count'],
                "recommended_links": internal_linking['recommended_count'],
                "suggestion": internal_linking['strategy'],
                "fix_code": internal_linking['example_code'],
                "impact": "Jobb crawlability és topical authority",
                "ai_benefit": "AI platformok jobban megértik az oldal kontextusát"
            })
        
        # Canonical és hreflang tagek
        if page_type != 'homepage':
            canonical_suggestion = self._generate_canonical_suggestion(url, analysis)
            if canonical_suggestion:
                seo_fixes.append(canonical_suggestion)
        
        return seo_fixes
    
    def _generate_schema_fixes(self, analysis: Dict, url: str, page_type: str, industry: str) -> List[Dict]:
        """Intelligens schema.org javaslatok oldaltípus alapján"""
        schema_fixes = []
        
        schema_data = analysis.get("schema", {})
        existing_schemas = schema_data.get("count", {})
        total_schemas = sum(existing_schemas.values())
        
        # Automatikus schema típus ajánlás
        recommended_schemas = self._recommend_schemas_by_page_type(page_type, industry)
        
        for schema_rec in recommended_schemas:
            schema_type = schema_rec['type']
            priority = schema_rec['priority']
            
            # Ha még nincs ilyen típusú schema
            if existing_schemas.get(schema_type, 0) == 0:
                # Kontextus-alapú schema generálás
                schema_code = self._generate_contextual_schema(
                    schema_type, url, analysis, page_type, industry
                )
                
                schema_fixes.append({
                    "type": f"{schema_type} Schema",
                    "priority": priority,
                    "benefit": schema_rec['benefit'],
                    "ai_impact": schema_rec['ai_impact'],
                    "code": schema_code,
                    "implementation": "JSON-LD formátumban a head vagy body végén",
                    "testing_tool": "https://search.google.com/test/rich-results",
                    "expected_features": schema_rec['rich_results'],
                    "platforms_using": schema_rec['platforms'],
                    "setup_time": schema_rec['setup_time']
                })
        
        # Speciális schema kombinációk
        if page_type == 'product' and industry == 'ecommerce':
            combo_schema = self._generate_product_combo_schema(analysis, url)
            schema_fixes.append({
                "type": "E-commerce Combo Schema Pack",
                "priority": "critical",
                "benefit": "Teljes e-commerce rich results csomag",
                "includes": ["Product", "Offer", "AggregateRating", "Review", "BreadcrumbList"],
                "code": combo_schema,
                "ai_impact": "AI platformok teljes termék kontextust kapnak",
                "implementation": "Egyetlen script tag-ben az összes kapcsolódó schema"
            })
        
        # Schema validáció és optimalizáció
        if total_schemas > 0:
            validation_result = self._validate_existing_schemas(schema_data)
            if validation_result['has_issues']:
                schema_fixes.append({
                    "type": "Schema Validation Fixes",
                    "priority": "high",
                    "issues_found": validation_result['issues'],
                    "fixes": validation_result['fixes'],
                    "benefit": "Javított schema érvényesség és hatékonyság"
                })
        
        return schema_fixes
    
    def _generate_content_fixes(self, analysis: Dict, page_type: str, industry: str) -> List[Dict]:
        """Tartalom optimalizálás AI platformokra"""
        content_fixes = []
        
        ai_metrics = analysis.get("ai_metrics", {})
        content_quality = analysis.get("content_quality", {})
        platform_analysis = analysis.get("platform_analysis", {})
        
        # Platform-specifikus tartalom javaslatok
        for platform_name, requirements in self.platform_requirements.items():
            platform_data = platform_analysis.get(platform_name, {})
            platform_score = platform_data.get('compatibility_score', 0)
            
            if platform_score < 70:
                missing_elements = self._identify_missing_platform_elements(
                    platform_name, requirements, ai_metrics, content_quality
                )
                
                if missing_elements:
                    content_fixes.append({
                        "issue": f"{platform_name.upper()} tartalom optimalizáció",
                        "current_score": platform_score,
                        "target_score": 85,
                        "missing_elements": missing_elements['must_have'],
                        "quick_improvements": missing_elements['quick_wins'],
                        "example_implementation": self._generate_platform_content_example(
                            platform_name, page_type, industry
                        ),
                        "benefit": f"Várható javulás: +{missing_elements['expected_improvement']} pont",
                        "implementation_time": missing_elements['time_estimate'],
                        "priority_actions": missing_elements['priority_actions']
                    })
        
        # Strukturált tartalom hiányosságok
        content_structure = ai_metrics.get("content_structure", {})
        if content_structure:
            structure_improvements = self._analyze_content_structure_gaps(content_structure, page_type)
            
            if structure_improvements['needs_improvement']:
                content_fixes.append({
                    "issue": "Strukturált tartalom fejlesztése szükséges",
                    "benefit": "AI platformok könnyebben feldolgozzák és priorizálják",
                    "missing_structures": structure_improvements['missing'],
                    "suggestion": structure_improvements['suggestion'],
                    "example_code": structure_improvements['example'],
                    "ai_platforms": ["ChatGPT", "Claude", "Gemini"],
                    "implementation_guide": structure_improvements['guide']
                })
        
        # FAQ és Q&A optimalizáció
        qa_format = ai_metrics.get("qa_format", {})
        if qa_format.get("qa_score", 0) < 50:
            faq_suggestions = self._generate_faq_suggestions(page_type, industry, content_quality)
            
            content_fixes.append({
                "issue": "FAQ/Q&A szekció hiányzik vagy gyenge",
                "benefit": "AI platformok preferálják a Q&A formátumot",
                "suggested_questions": faq_suggestions['questions'],
                "implementation_example": faq_suggestions['html_structure'],
                "schema_code": faq_suggestions['faq_schema'],
                "ai_impact": "Közvetlenül megjelenhet AI válaszokban",
                "platforms_benefiting": ["ChatGPT", "Gemini", "Bing Chat"]
            })
        
        # Multimédia és vizuális tartalom
        multimedia_suggestions = self._analyze_multimedia_needs(analysis, page_type)
        if multimedia_suggestions['needs_improvement']:
            content_fixes.append({
                "issue": "Multimédia tartalom optimalizáció",
                "current_images": multimedia_suggestions['current_count'],
                "recommended_images": multimedia_suggestions['recommended_count'],
                "missing_elements": multimedia_suggestions['missing'],
                "suggestions": multimedia_suggestions['suggestions'],
                "alt_text_template": multimedia_suggestions['alt_text_guide'],
                "image_schema": multimedia_suggestions['image_schema'],
                "ai_benefit": "Gemini és Bing Chat preferálja a vizuális tartalmat"
            })
        
        return content_fixes
    
    def _generate_technical_fixes(self, analysis: Dict, url: str) -> List[Dict]:
        """Enhanced technikai javítások"""
        technical_fixes = []
        
        # Core Web Vitals optimalizáció
        psi = analysis.get("pagespeed_insights", {})
        if psi:
            cwv_fixes = self._analyze_core_web_vitals(psi)
            if cwv_fixes:
                technical_fixes.extend(cwv_fixes)
        
        # Mobile optimalizáció
        mobile = analysis.get("mobile_friendly", {})
        if not mobile.get("has_viewport"):
            technical_fixes.append({
                "issue": "Hiányzó vagy hibás viewport meta tag",
                "severity": "high",
                "impact": "Rossz mobil élmény, AI mobile-first indexing probléma",
                "fix_code": '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">',
                "implementation": "Head szekció elején",
                "additional_mobile_fixes": self._generate_mobile_optimization_pack()
            })
        
        # Robots.txt optimalizáció
        robots = analysis.get("robots_txt", {})
        if robots.get("can_fetch") and not self._is_robots_optimized(robots, url):
            technical_fixes.append({
                "issue": "Robots.txt optimalizáció szükséges",
                "severity": "medium",
                "current_status": "Alapszintű engedélyezés",
                "optimized_robots": self._generate_optimized_robots(url),
                "includes": ["AI bot engedélyek", "Crawl-delay", "Sitemap referencia"],
                "ai_bots_included": ["GPTBot", "Claude-Web", "Bingbot", "Googlebot"],
                "implementation": "robots.txt fájl frissítése a gyökérkönyvtárban"
            })
        
        # Sitemap fejlesztések
        sitemap = analysis.get("sitemap", {})
        if not sitemap.get("exists"):
            technical_fixes.append({
                "issue": "Hiányzó XML sitemap",
                "severity": "high",
                "impact": "Lassabb indexelés, AI platformok nem találják meg az összes oldalt",
                "solution": "XML sitemap generálása és robots.txt-ben hivatkozás",
                "example_structure": self._generate_sitemap_example(url),
                "tools": {
                    "WordPress": "Yoast SEO vagy RankMath",
                    "Static": "sitemap-generator.org",
                    "Dynamic": "Programozott generálás"
                },
                "best_practices": [
                    "Max 50,000 URL per sitemap",
                    "Prioritás és changefreq megadása",
                    "Képek és videók külön sitemap"
                ]
            })
        
        # HTTPS és biztonság
        if not url.startswith('https://'):
            technical_fixes.append({
                "issue": "HTTPS hiányzik",
                "severity": "critical",
                "impact": "Biztonsági figyelmeztetések, alacsonyabb ranking",
                "solution": "SSL tanúsítvány telepítése",
                "providers": ["Let's Encrypt (ingyenes)", "Cloudflare", "SSL.com"],
                "implementation_steps": [
                    "SSL tanúsítvány beszerzése",
                    "Telepítés a szerveren",
                    "HTTP->HTTPS átirányítás beállítása",
                    "Mixed content hibák javítása"
                ]
            })
        
        # Nemzetköziesítés (i18n)
        lang_optimization = self._analyze_language_setup(analysis)
        if lang_optimization['needs_improvement']:
            technical_fixes.append(lang_optimization['fix'])
        
        return technical_fixes
    
    def _generate_ai_fixes(self, analysis: Dict, page_type: str, industry: str) -> List[Dict]:
        """AI-specifikus optimalizálások részletes útmutatóval"""
        ai_fixes = []
        
        platforms = analysis.get("platform_analysis", {})
        ai_readiness = analysis.get("ai_readiness_score", 0)
        
        # Platform bundle optimalizáció
        platform_scores = {name: data.get('compatibility_score', 0) 
                          for name, data in platforms.items() 
                          if name != 'summary'}
        
        # Azonosítjuk a gyenge platformokat
        weak_platforms = {name: score for name, score in platform_scores.items() if score < 70}
        
        if weak_platforms:
            # Csoportosított javítások hasonló platformokhoz
            platform_groups = self._group_platforms_by_requirements(weak_platforms)
            
            for group_name, group_data in platform_groups.items():
                platforms_in_group = group_data['platforms']
                common_fixes = group_data['common_fixes']
                
                ai_fixes.append({
                    "type": f"{group_name}_optimization",
                    "platforms": platforms_in_group,
                    "current_avg_score": group_data['avg_score'],
                    "target_score": 85,
                    "common_improvements": common_fixes,
                    "implementation_priority": group_data['priority_actions'],
                    "quick_wins": group_data['quick_wins'],
                    "estimated_improvement": f"+{group_data['improvement_potential']} pont",
                    "time_investment": group_data['time_estimate'],
                    "roi_score": group_data['roi_score']
                })
        
        # AI-first content stratégia
        if ai_readiness < 70:
            content_strategy = self._generate_ai_content_strategy(
                analysis, page_type, industry, ai_readiness
            )
            
            ai_fixes.append({
                "type": "ai_first_content_strategy",
                "current_score": ai_readiness,
                "improvement_roadmap": content_strategy['roadmap'],
                "quick_implementations": content_strategy['quick_wins'],
                "long_term_projects": content_strategy['long_term'],
                "content_templates": content_strategy['templates'],
                "measurement_plan": content_strategy['kpis']
            })
        
        # Voice search optimalizáció
        voice_optimization = self._analyze_voice_search_readiness(analysis)
        if voice_optimization['needs_improvement']:
            ai_fixes.append({
                "type": "voice_search_optimization",
                "current_readiness": voice_optimization['score'],
                "improvements": voice_optimization['fixes'],
                "conversational_keywords": voice_optimization['keywords'],
                "snippet_optimization": voice_optimization['snippet_strategy'],
                "platforms_affected": ["Google Assistant", "Alexa", "Siri", "Cortana"]
            })
        
        # Featured snippet optimalizáció
        snippet_optimization = self._analyze_featured_snippet_potential(analysis, page_type)
        if snippet_optimization['has_potential']:
            ai_fixes.append({
                "type": "featured_snippet_optimization",
                "snippet_types": snippet_optimization['suitable_types'],
                "content_formatting": snippet_optimization['formatting_guide'],
                "example_structure": snippet_optimization['examples'],
                "keywords_targeting": snippet_optimization['target_keywords'],
                "success_probability": snippet_optimization['success_rate']
            })
        
        return ai_fixes
    
    def _identify_quick_wins(self, analysis: Dict, url: str, page_type: str) -> List[Dict]:
        """Gyors nyereségek azonosítása (< 1 óra befektetés, nagy hatás)"""
        quick_wins = []
        
        # Title optimalizáció (ha van, de nem optimális)
        meta_data = analysis.get("meta_and_headings", {})
        title = meta_data.get("title")
        if title and (len(title) < 30 or len(title) > 60):
            quick_wins.append({
                "task": "Title hossz optimalizálása",
                "current": f"{len(title)} karakter",
                "action": "Módosítsd 30-60 karakter közé",
                "time": "2 perc",
                "impact": "High",
                "expected_result": "+5-10% CTR"
            })
        
        # Meta description (ha hiányzik)
        if not meta_data.get("description"):
            quick_wins.append({
                "task": "Meta description hozzáadása",
                "action": "Írj 120-160 karakteres leírást CTA-val",
                "time": "5 perc",
                "impact": "High",
                "expected_result": "+10% CTR"
            })
        
        # H1 (ha hiányzik)
        if meta_data.get("h1_count", 0) == 0:
            quick_wins.append({
                "task": "H1 elem hozzáadása",
                "action": "Adj hozzá egy tiszta, kulcsszódús H1-et",
                "time": "2 perc",
                "impact": "Critical",
                "expected_result": "Jobb AI tartalom megértés"
            })
        
        # Alt text képekhez
        content = analysis.get("content_quality", {})
        if content:
            quick_wins.append({
                "task": "Alt text hozzáadása képekhez",
                "action": "Minden képhez írj leíró alt text-et",
                "time": "15 perc",
                "impact": "Medium",
                "expected_result": "Jobb accessibility és SEO"
            })
        
        # Viewport meta tag
        if not analysis.get("mobile_friendly", {}).get("has_viewport"):
            quick_wins.append({
                "task": "Viewport meta tag hozzáadása",
                "action": "Add hozzá a viewport meta tag-et",
                "time": "1 perc",
                "impact": "Critical",
                "expected_result": "Mobil kompatibilitás"
            })
        
        return quick_wins
    
    def _create_platform_bundles(self, analysis: Dict) -> Dict:
        """Platform bundle-ök létrehozása szinergikus optimalizációhoz"""
        bundles = {
            "search_bundle": {
                "platforms": ["ChatGPT", "Gemini", "Bing Chat"],
                "common_optimizations": [
                    "Strukturált Q&A tartalom",
                    "Gazdag schema markup",
                    "Tematikus mélység növelése"
                ],
                "synergy_score": 0
            },
            "ai_assistant_bundle": {
                "platforms": ["ChatGPT", "Claude"],
                "common_optimizations": [
                    "Hosszú formátumú tartalom",
                    "Lépésenkénti útmutatók",
                    "Részletes magyarázatok"
                ],
                "synergy_score": 0
            },
            "visual_bundle": {
                "platforms": ["Gemini", "Bing Chat"],
                "common_optimizations": [
                    "Multimédia integráció",
                    "Infografikák",
                    "Video tartalom"
                ],
                "synergy_score": 0
            }
        }
        
        # Szinergia pontszámok számítása
        platform_analysis = analysis.get("platform_analysis", {})
        for bundle_name, bundle_data in bundles.items():
            scores = [platform_analysis.get(p, {}).get('compatibility_score', 0) 
                     for p in bundle_data['platforms']]
            if scores:
                bundle_data['synergy_score'] = sum(scores) / len(scores)
                bundle_data['improvement_potential'] = max(0, 85 - bundle_data['synergy_score'])
        
        return bundles
    
    def _prioritize_fixes_by_roi(self, fixes: Dict) -> List[Dict]:
        """ROI-alapú prioritizálás (impact/effort)"""
        all_fixes = []
        
        # Kritikus javítások - legmagasabb ROI
        for fix in fixes.get("critical_fixes", []):
            roi_score = self._calculate_roi_score(fix, "critical")
            all_fixes.append({
                **fix,
                "category": "critical",
                "roi_score": roi_score,
                "priority_rank": 1
            })
        
        # Quick wins - magas ROI
        for fix in fixes.get("quick_wins", []):
            roi_score = self._calculate_roi_score(fix, "quick_win")
            all_fixes.append({
                **fix,
                "category": "quick_win",
                "roi_score": roi_score,
                "priority_rank": 2
            })
        
        # Technikai javítások
        for fix in fixes.get("technical_fixes", []):
            severity = fix.get("severity", "medium")
            roi_score = self._calculate_roi_score(fix, severity)
            all_fixes.append({
                **fix,
                "category": "technical",
                "roi_score": roi_score,
                "priority_rank": 3 if severity == "high" else 4
            })
        
        # SEO fejlesztések
        for fix in fixes.get("seo_improvements", []):
            roi_score = self._calculate_roi_score(fix, "medium")
            all_fixes.append({
                **fix,
                "category": "seo",
                "roi_score": roi_score,
                "priority_rank": 5
            })
        
        # Schema javítások
        for fix in fixes.get("schema_suggestions", []):
            priority = fix.get("priority", "medium")
            roi_score = self._calculate_roi_score(fix, priority)
            all_fixes.append({
                **fix,
                "category": "schema",
                "roi_score": roi_score,
                "priority_rank": 4 if priority == "high" else 6
            })
        
        # Rendezés: először priority_rank, majd ROI score szerint
        return sorted(all_fixes, key=lambda x: (x.get("priority_rank", 10), -x.get("roi_score", 0)))
    
    def _calculate_roi_score(self, fix: Dict, severity: str) -> float:
        """ROI score számítása egy javításhoz"""
        base_scores = {
            "critical": 100,
            "high": 80,
            "medium": 50,
            "low": 20,
            "quick_win": 90
        }
        
        base_score = base_scores.get(severity, 50)
        
        # Időigény alapú módosító
        time_str = fix.get("estimated_time", "")
        if "perc" in time_str.lower() or "minute" in time_str.lower():
            try:
                minutes = int(re.search(r'\d+', time_str).group())
                if minutes <= 5:
                    base_score *= 1.5
                elif minutes <= 15:
                    base_score *= 1.2
            except:
                pass
        
        # Expected improvement módosító
        improvement = fix.get("expected_improvement", "")
        if "%" in improvement:
            try:
                percent = int(re.search(r'\d+', improvement).group())
                base_score *= (1 + percent/100)
            except:
                pass
        
        return round(base_score, 2)
    
    def _create_implementation_guide(self, analysis: Dict) -> Dict:
        """Részletes implementációs útmutató időbecslésekkel"""
        
        # Elemzés alapján testreszabott útmutató
        ai_score = analysis.get("ai_readiness_score", 0)
        has_schema = sum(analysis.get("schema", {}).get("count", {}).values()) > 0
        has_mobile = analysis.get("mobile_friendly", {}).get("has_viewport", False)
        
        if ai_score < 40:
            phase = "emergency"
        elif ai_score < 60:
            phase = "improvement"
        else:
            phase = "optimization"
        
        guides = {
            "emergency": {
                "priority_order": [
                    "1. 🚨 Kritikus SEO hibák javítása (title, description, H1) - 30 perc",
                    "2. 🤖 Robots.txt és sitemap létrehozása - 1 óra",
                    "3. 📱 Mobile viewport és alapvető reszponzivitás - 2 óra",
                    "4. 🏗️ Alapvető schema.org markup (Organization/LocalBusiness) - 2 óra",
                    "5. 📝 Tartalom struktúra javítása (headings, bekezdések) - 3 óra",
                    "6. 🎯 Platform-specifikus quick wins - 2 óra"
                ],
                "estimated_timeline": {
                    "kritikus_javítások": "30 perc - 1 óra",
                    "technikai_alapok": "2-3 óra",
                    "schema_alapok": "2-4 óra",
                    "tartalom_struktúra": "3-5 óra",
                    "platform_optimalizáció": "1-2 nap",
                    "teljes_implementáció": "2-3 nap"
                },
                "focus": "Alapvető problémák sürgős javítása"
            },
            "improvement": {
                "priority_order": [
                    "1. ⚡ Quick wins implementálása - 1 óra",
                    "2. 🏗️ Schema.org bővítése (FAQ, HowTo, Article) - 3 óra",
                    "3. 📊 Tartalom mélység növelése - 1 nap",
                    "4. 🎯 Top 2 AI platform optimalizáció - 1 nap",
                    "5. 🔍 Kulcsszó és szemantikai optimalizáció - 4 óra",
                    "6. 📈 Teljesítmény optimalizáció - 4 óra"
                ],
                "estimated_timeline": {
                    "quick_wins": "1-2 óra",
                    "schema_bővítés": "3-4 óra",
                    "tartalom_fejlesztés": "1-2 nap",
                    "platform_specifikus": "1-2 nap",
                    "finomhangolás": "1 nap",
                    "teljes_implementáció": "4-5 nap"
                },
                "focus": "Jelentős javulás elérése minden területen"
            },
            "optimization": {
                "priority_order": [
                    "1. 🚀 Advanced schema implementáció - 4 óra",
                    "2. 🎯 Minden AI platform finomhangolása - 2 nap",
                    "3. 💎 Premium tartalom funkciók - 2 nap",
                    "4. 🔊 Voice search optimalizáció - 1 nap",
                    "5. 🌍 Nemzetközi SEO setup - 1 nap",
                    "6. ⚡ Core Web Vitals maximalizálás - 1 nap"
                ],
                "estimated_timeline": {
                    "advanced_schema": "4-6 óra",
                    "platform_excellence": "2-3 nap",
                    "premium_features": "2-3 nap",
                    "voice_és_i18n": "2 nap",
                    "teljesítmény_max": "1-2 nap",
                    "teljes_implementáció": "7-10 nap"
                },
                "focus": "Versenyelőny és kiválóság elérése"
            }
        }
        
        guide = guides[phase]
        
        # Testing checklist
        guide["testing_checklist"] = [
            "✅ Google Search Console - nincs hiba, coverage OK",
            "✅ Schema Testing Tool - minden schema valid",
            "✅ Mobile-Friendly Test - passed",
            "✅ PageSpeed Insights - 70+ mobil score",
            "✅ AI platform tesztek (ChatGPT, Claude, Gemini)",
            "✅ Rich Results Test - eligibility confirmed",
            "✅ Core Web Vitals - zöld minden metrika"
        ]
        
        # Monitoring terv
        guide["monitoring"] = [
            "📊 Napi: Search Console hibaellenőrzés",
            "📈 Heti: Ranking és forgalom változások",
            "🤖 Heti: AI platform megjelenések tesztelése",
            "📝 Havi: Tartalom frissítés és bővítés",
            "🎯 Havi: Konkurencia elemzés",
            "🚀 Negyedéves: Teljes AI-readiness audit"
        ]
        
        # ROI becslés
        guide["expected_roi"] = {
            "30_nap": "+15-25% organic traffic",
            "60_nap": "+25-40% AI visibility",
            "90_nap": "+30-50% overall engagement",
            "conversion_impact": "+10-20% conversion rate"
        }
        
        return guide
    
    # ============= Helper metódusok =============
    
    def _generate_intelligent_title(self, domain: str, page_type: str, 
                                   industry: str, analysis: Dict) -> str:
        """Intelligens title generálás kontextus alapján"""
        
        clean_domain = domain.replace('www.', '').split('.')[0].title()
        current_year = datetime.now().year
        
        # Kulcsszavak kinyerése a tartalomból
        keywords = self._extract_top_keywords(analysis, 3)
        keyword_string = " ".join(keywords) if keywords else ""
        
        # Industry és page type specifikus template választás
        templates = self.meta_templates["title"]["industry_patterns"].get(industry, [])
        
        if page_type == "homepage":
            if industry == "ecommerce":
                return f"{clean_domain} - Online Vásárlás | Ingyenes Szállítás 15.000 Ft felett"
            elif industry == "service":
                return f"{clean_domain} - Professzionális {keyword_string} Szolgáltatások | Garancia"
            elif industry == "blog":
                return f"{clean_domain} Blog - Szakértői Tartalmak és Útmutatók {current_year}"
            else:
                return f"{clean_domain} - {keyword_string} | Megbízható Partner {current_year} Óta"
        
        elif page_type == "product":
            price_indicator = "Legjobb Ár" if industry == "ecommerce" else "Prémium"
            return f"{keyword_string} - {clean_domain} | {price_indicator} Garancia"
        
        elif page_type == "blog":
            return f"{keyword_string}: Teljes Útmutató [{current_year}] - {clean_domain}"
        
        elif page_type == "service":
            location = "Budapest" if ".hu" in domain else "Magyarország"
            return f"{keyword_string} {location} - {clean_domain} | Azonnali Árajánlat"
        
        elif page_type == "contact":
            return f"Kapcsolat - {clean_domain} | Kérjen Személyes Ajánlatot"
        
        elif page_type == "about":
            return f"Rólunk - {clean_domain} | {current_year - 5}+ Év Tapasztalat"
        
        # Fallback
        return f"{clean_domain} - {keyword_string or 'Professzionális Megoldások'} | {current_year}"
    
    def _generate_intelligent_description(self, domain: str, page_type: str, 
                                         industry: str, analysis: Dict, title: str) -> str:
        """Intelligens meta description generálás"""
        
        clean_domain = domain.replace('www.', '').split('.')[0].title()
        keywords = self._extract_top_keywords(analysis, 5)
        
        # Industry templates
        templates = self.meta_templates["description"]["industry_patterns"].get(industry, [])
        
        if page_type == "homepage":
            if industry == "ecommerce":
                return f"⭐ {clean_domain} webáruház - Több mint 10.000 termék raktárról. ✓ Ingyenes szállítás ✓ 30 napos visszaküldés ✓ Biztonságos fizetés. Vásárolj most!"
            elif industry == "service":
                return f"Professzionális {' és '.join(keywords[:2]) if keywords else 'szolgáltatások'}. ✓ 10+ év tapasztalat ✓ Ingyenes felmérés ✓ Garancia. {clean_domain} - Kérj árajánlatot!"
            elif industry == "blog":
                return f"Olvass szakértői cikkeket {' és '.join(keywords[:2]) if keywords else 'számos'} témában. Gyakorlati útmutatók, tippek, legfrissebb trendek. Csatlakozz {clean_domain} közösségéhez!"
            else:
                return f"{clean_domain} - Vezető vállalat {' és '.join(keywords[:2]) if keywords else 'az iparágban'}. Innovatív megoldások, szakértő csapat, garantált minőség. Ismerj meg minket!"
        
        elif page_type == "product":
            return f"{'⭐ ' + keywords[0] if keywords else 'Termék'} kedvező áron a {clean_domain} kínálatában. Részletes leírás, vásárlói vélemények, gyors szállítás. Rendeld meg most!"
        
        elif page_type == "blog":
            return f"Részletes útmutató: {title[:50] if title else 'szakmai tartalom'}. Lépésről-lépésre, példákkal, szakértői tippekkel. Olvasd el a {clean_domain} blogon!"
        
        elif page_type == "service":
            return f"{keywords[0] if keywords else 'Szolgáltatás'} szakértők Budapesten és környékén. Ingyenes felmérés, versenyképes árak, garancia. Hívjon: +36-XX-XXX-XXXX"
        
        # Fallback with CTA
        base_desc = f"{clean_domain} - Minőségi {' és '.join(keywords[:2]) if keywords else 'szolgáltatások és termékek'}."
        cta = "Fedezd fel kínálatunkat és kérj ajánlatot még ma!"
        return f"{base_desc} {cta}"[:160]
    
    def _optimize_existing_title(self, title: str, page_type: str, industry: str) -> str:
        """Meglévő title optimalizálása"""
        
        title_length = len(title)
        
        # Ha túl rövid
        if title_length < 30:
            # Industry-specifikus bővítések
            extensions = {
                "ecommerce": " | Ingyenes Szállítás",
                "service": " | Szakértő Csapat",
                "blog": f" | Frissítve {datetime.now().year}",
                "corporate": " | Megbízható Partner"
            }
            extension = extensions.get(industry, " | Professzionális Megoldások")
            
            if len(title + extension) <= 60:
                return title + extension
            else:
                return title + " | Minőség"
        
        # Ha túl hosszú
        elif title_length > 60:
            # Intelligens rövidítés - megtartjuk a fontos részeket
            if " - " in title:
                parts = title.split(" - ")
                return parts[0][:57] + "..."
            elif " | " in title:
                parts = title.split(" | ")
                return parts[0][:57] + "..."
            else:
                # Szó határon vágjuk
                words = title.split()
                result = ""
                for word in words:
                    if len(result + word) < 57:
                        result += word + " "
                    else:
                        break
                return result.strip() + "..."
        
        return title
    
    def _generate_h1_from_context(self, title: str, page_type: str, industry: str) -> str:
        """Kontextus-alapú H1 generálás"""
        
        if page_type == "homepage":
            if industry == "ecommerce":
                return "Fedezd Fel Webáruházunk Kínálatát"
            elif industry == "service":
                return "Professzionális Szolgáltatások Az Ön Sikeréért"
            elif industry == "blog":
                return "Szakértői Tudás és Útmutatók Egy Helyen"
            else:
                return "Innovatív Megoldások Üzleti Partnereinknek"
        
        elif page_type == "product":
            return title.split("-")[0].strip() if title and "-" in title else "Prémium Termék Részletek"
        
        elif page_type == "blog":
            # Kérdés formátum AI platformoknak
            if title:
                clean_title = title.split("|")[0].split("-")[0].strip()
                if not clean_title.endswith("?"):
                    return f"Hogyan {clean_title}?"
                return clean_title
            return "Amit Erről Tudni Érdemes"
        
        elif page_type == "service":
            return "Szolgáltatásaink Részletesen"
        
        elif page_type == "contact":
            return "Vegye Fel Velünk A Kapcsolatot"
        
        elif page_type == "about":
            return "Történetünk és Küldetésünk"
        
        # Fallback
        return title.split("|")[0].strip() if title else "Üdvözöljük Oldalunkon"
    
    def _generate_heading_hierarchy_fix(self, h1_texts: List[str]) -> str:
        """Heading hierarchia javítási kód generálása"""
        
        if not h1_texts:
            return "<!-- Nincs H1 elem az oldalon -->"
        
        code = "<!-- Heading hierarchia javítás -->\n"
        code += f"<h1>{h1_texts[0]}</h1> <!-- Ezt tartsd meg H1-ként -->\n\n"
        
        for i, heading in enumerate(h1_texts[1:], 1):
            code += f"<!-- Régi H1 #{i+1} -> H2 -->\n"
            code += f"<h2>{heading}</h2>\n"
        
        code += "\n<!-- Használj H3, H4 elemeket az al-szekciókhoz -->"
        
        return code
    
    def _suggest_heading_hierarchy(self, h1_texts: List[str]) -> str:
        """Heading hierarchia javaslat"""
        
        hierarchy = "Javasolt hierarchia:\n"
        hierarchy += "└─ H1: Fő téma (1 db)\n"
        hierarchy += "   ├─ H2: Fő szekciók (3-5 db)\n"
        hierarchy += "   │  ├─ H3: Al-szekciók\n"
        hierarchy += "   │  └─ H4: Részletek\n"
        hierarchy += "   └─ H2: Következő fő szekció"
        
        return hierarchy
    
    def _extract_top_keywords(self, analysis: Dict, count: int = 5) -> List[str]:
        """Top kulcsszavak kinyerése az elemzésből"""
        
        keywords = []
        
        # Tartalom elemzésből
        content = analysis.get('content_quality', {})
        keyword_analysis = content.get('keyword_analysis', {})
        top_keywords = keyword_analysis.get('top_keywords', [])
        
        for kw in top_keywords[:count]:
            if isinstance(kw, list) and len(kw) > 0:
                keywords.append(kw[0])
            elif isinstance(kw, str):
                keywords.append(kw)
        
        # Ha nincs elég, title-ből és description-ből
        if len(keywords) < count:
            meta = analysis.get('meta_and_headings', {})
            title = meta.get('title', '')
            desc = meta.get('description', '')
            
            # Egyszerű tokenizálás
            text = f"{title} {desc}".lower()
            words = re.findall(r'\b[a-záéíóöőúüű]+\b', text)
            
            # Stop words kiszűrése
            stop_words = {'a', 'az', 'és', 'vagy', 'de', 'hogy', 'ez', 'az', 'itt', 'ott'}
            words = [w for w in words if w not in stop_words and len(w) > 3]
            
            # Gyakoriság alapján
            from collections import Counter
            word_freq = Counter(words)
            
            for word, _ in word_freq.most_common(count - len(keywords)):
                if word not in keywords:
                    keywords.append(word)
        
        return keywords[:count]
    
    def _analyze_keyword_optimization(self, keyword_data: Dict, industry: str, page_type: str) -> Dict:
        """Kulcsszó optimalizáció elemzése"""
        
        result = {
            'needs_improvement': False,
            'current_density': 0,
            'optimal_density': 2.5,
            'missing_keywords': [],
            'suggestion': '',
            'implementation_example': ''
        }
        
        # Industry-specifikus kulcsszavak
        industry_keywords = self.keywords_db.get(industry, {}).get('hu', [])
        
        # Jelenlegi kulcsszavak
        current_keywords = [kw[0].lower() if isinstance(kw, list) else str(kw).lower() 
                           for kw in keyword_data.get('top_keywords', [])]
        
        # Hiányzó fontos kulcsszavak
        missing = [kw for kw in industry_keywords[:5] if not any(kw in ck for ck in current_keywords)]
        
        if missing:
            result['needs_improvement'] = True
            result['missing_keywords'] = missing
            result['suggestion'] = f"Adj hozzá ezeket a kulcsszavakat: {', '.join(missing[:3])}"
            
            # Példa implementáció
            result['implementation_example'] = f"""
<!-- Kulcsszó optimalizált bekezdés példa -->
<p>A {missing[0]} területén szerzett tapasztalatunk garantálja, hogy 
{missing[1] if len(missing) > 1 else 'szolgáltatásaink'} a legmagasabb 
minőséget képviselik. Ügyfeleink számára {missing[2] if len(missing) > 2 else 'megoldásaink'}
biztosítják a várt eredményeket.</p>
"""
        
        return result
    
    def _generate_comprehensive_og_tags(self, url: str, meta_data: Dict, 
                                       page_type: str, industry: str) -> Dict:
        """Teljes Open Graph és social media tag készlet"""
        
        title = meta_data.get('title', 'Weboldal')
        description = meta_data.get('description', 'Professzionális szolgáltatások és megoldások')
        
        code = f"""<!-- Open Graph / Facebook -->
<meta property="og:type" content="{'product' if page_type == 'product' else 'website'}">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{url}/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="hu_HU">
<meta property="og:site_name" content="{urlparse(url).netloc}">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:url" content="{url}">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{url}/twitter-image.jpg">

<!-- LinkedIn -->
<meta property="og:image:alt" content="{title}">

<!-- WhatsApp és más chat alkalmazások -->
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:secure_url" content="{url}/og-image.jpg">"""
        
        # Product-specifikus tagek
        if page_type == 'product' and industry == 'ecommerce':
            code += """

<!-- Product specific -->
<meta property="product:price:amount" content="0">
<meta property="product:price:currency" content="HUF">
<meta property="product:availability" content="in stock">
<meta property="product:condition" content="new">"""
        
        return {
            'code': code,
            'includes': [
                'Facebook Open Graph',
                'Twitter Cards',
                'LinkedIn Preview',
                'WhatsApp Preview',
                'Discord Embed'
            ]
        }
    
    def _analyze_semantic_structure(self, analysis: Dict) -> Dict:
        """Szemantikus HTML5 struktúra elemzése"""
        
        # Ezt egy valós implementációban a HTML parse-olásával kellene
        # Most simplified változat
        
        result = {
            'needs_improvement': True,  # Alapértelmezetten mindig van mit javítani
            'missing_elements': [],
            'example_structure': '',
            'guide': ''
        }
        
        # Tipikus hiányzó elemek
        result['missing_elements'] = [
            '<header> - Fejléc szakasz',
            '<nav> - Navigációs menü',
            '<main> - Fő tartalom',
            '<article> - Cikk/bejegyzés',
            '<section> - Tartalmi szakaszok',
            '<aside> - Oldalsáv',
            '<footer> - Lábléc'
        ]
        
        result['example_structure'] = """<!DOCTYPE html>
<html lang="hu">
<head>
    <!-- Meta tags -->
</head>
<body>
    <header>
        <nav aria-label="Fő navigáció">
            <ul>
                <li><a href="/">Főoldal</a></li>
                <li><a href="/szolgaltatasok">Szolgáltatások</a></li>
            </ul>
        </nav>
    </header>
    
    <main>
        <article>
            <header>
                <h1>Cím</h1>
                <time datetime="2024-01-01">2024. január 1.</time>
            </header>
            <section>
                <h2>Szakasz címe</h2>
                <p>Tartalom...</p>
            </section>
        </article>
        
        <aside>
            <h3>Kapcsolódó tartalmak</h3>
        </aside>
    </main>
    
    <footer>
        <p>&copy; 2024 Vállalat</p>
    </footer>
</body>
</html>"""
        
        result['guide'] = "Használj szemantikus HTML5 elemeket a jobb SEO és AI megértés érdekében"
        
        return result
    
    def _generate_robots_txt_fix(self, url: str) -> str:
        """Robots.txt javítási kód"""
        
        domain = urlparse(url).netloc
        
        return f"""# Robots.txt - Optimalizált AI botok számára
# Generálva: {datetime.now().strftime('%Y-%m-%d')}

# Keresőmotorok
User-agent: *
Allow: /
Crawl-delay: 1

# Google
User-agent: Googlebot
Allow: /
Crawl-delay: 0

# Bing
User-agent: Bingbot
Allow: /
Crawl-delay: 1

# AI Botok engedélyezése
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: CCBot
Allow: /

# Tiltások
Disallow: /admin/
Disallow: /private/
Disallow: *.pdf$
Disallow: /temp/

# Sitemaps
Sitemap: https://{domain}/sitemap.xml
Sitemap: https://{domain}/sitemap-images.xml
Sitemap: https://{domain}/sitemap-videos.xml"""
    
    def _generate_optimized_robots(self, url: str) -> str:
        """Optimalizált robots.txt generálása"""
        return self._generate_robots_txt_fix(url)
    
    def _get_empty_fixes_structure(self, error_msg: str = "") -> Dict:
        """Üres fix struktúra visszaadása hiba esetén"""
        
        base_structure = {
            "critical_fixes": [],
            "seo_improvements": [],
            "schema_suggestions": [],
            "content_optimizations": [],
            "technical_fixes": [],
            "ai_readiness_fixes": [],
            "implementation_guide": self._create_implementation_guide({}),
            "quick_wins": [],
            "prioritized_actions": [],
            "platform_bundles": {}
        }
        
        if error_msg:
            base_structure["error"] = error_msg
        
        return base_structure
    
    def _recommend_schemas_by_page_type(self, page_type: str, industry: str) -> List[Dict]:
        """Schema ajánlások oldaltípus alapján"""
        
        recommendations = {
            "homepage": [
                {"type": "Organization", "priority": "critical", "benefit": "Cég információk megjelenítése",
                 "ai_impact": "AI platformok azonosítják a szervezetet", "rich_results": ["Knowledge panel"],
                 "platforms": ["Google", "Bing", "ChatGPT"], "setup_time": "30 perc"},
                {"type": "WebSite", "priority": "high", "benefit": "Sitelinks search box",
                 "ai_impact": "Keresés funkció AI-ban", "rich_results": ["Search box"],
                 "platforms": ["Google"], "setup_time": "15 perc"},
                {"type": "BreadcrumbList", "priority": "medium", "benefit": "Navigációs útvonal",
                 "ai_impact": "Jobb site struktúra megértés", "rich_results": ["Breadcrumbs"],
                 "platforms": ["Google", "Bing"], "setup_time": "20 perc"}
            ],
            "product": [
                {"type": "Product", "priority": "critical", "benefit": "Termék információk, ár, értékelés",
                 "ai_impact": "AI shopping asszisztensek", "rich_results": ["Product snippet", "Price", "Rating"],
                 "platforms": ["Google Shopping", "Bing Shopping"], "setup_time": "45 perc"},
                {"type": "AggregateRating", "priority": "high", "benefit": "Értékelések megjelenítése",
                 "ai_impact": "Bizalom építés AI-ban", "rich_results": ["Star rating"],
                 "platforms": ["All"], "setup_time": "20 perc"},
                {"type": "Offer", "priority": "high", "benefit": "Ár és elérhetőség",
                 "ai_impact": "Valós idejű ár info", "rich_results": ["Price", "Availability"],
                 "platforms": ["Shopping platforms"], "setup_time": "25 perc"}
            ],
            "blog": [
                {"type": "Article", "priority": "critical", "benefit": "Cikk részletek, szerző, dátum",
                 "ai_impact": "AI tartalom forrásként használja", "rich_results": ["Article rich results"],
                 "platforms": ["Google", "Bing", "ChatGPT"], "setup_time": "30 perc"},
                {"type": "HowTo", "priority": "high", "benefit": "Lépésenkénti útmutatók",
                 "ai_impact": "AI útmutató generálás", "rich_results": ["How-to snippet"],
                 "platforms": ["Google", "ChatGPT"], "setup_time": "40 perc"},
                {"type": "FAQPage", "priority": "high", "benefit": "GYIK megjelenítés",
                 "ai_impact": "Közvetlen válaszok AI-ban", "rich_results": ["FAQ snippet"],
                 "platforms": ["All AI platforms"], "setup_time": "35 perc"}
            ],
            "service": [
                {"type": "LocalBusiness", "priority": "critical", "benefit": "Helyi üzleti információk",
                 "ai_impact": "Helyi keresési relevancia", "rich_results": ["Local pack", "Knowledge panel"],
                 "platforms": ["Google Maps", "Bing Places"], "setup_time": "40 perc"},
                {"type": "Service", "priority": "high", "benefit": "Szolgáltatás részletek",
                 "ai_impact": "Szolgáltatás összehasonlítás", "rich_results": ["Service details"],
                 "platforms": ["Google", "Bing"], "setup_time": "30 perc"},
                {"type": "AggregateRating", "priority": "medium", "benefit": "Ügyfél értékelések",
                 "ai_impact": "Bizalmi faktor", "rich_results": ["Stars"],
                 "platforms": ["All"], "setup_time": "20 perc"}
            ]
        }
        
        # Default recommendations
        default = [
            {"type": "Organization", "priority": "high", "benefit": "Alapvető cég info",
             "ai_impact": "Szervezet azonosítás", "rich_results": ["Brand info"],
             "platforms": ["All"], "setup_time": "30 perc"}
        ]
        
        return recommendations.get(page_type, default)
    
    def _generate_contextual_schema(self, schema_type: str, url: str, 
                                   analysis: Dict, page_type: str, industry: str) -> str:
        """Kontextus-alapú schema generálás"""
        
        domain = urlparse(url).netloc
        clean_domain = domain.replace('www.', '').split('.')[0].title()
        
        # Alapértelmezett értékek
        defaults = {
            "company_name": clean_domain,
            "company_alt_name": clean_domain,
            "website_url": f"https://{domain}",
            "logo_url": f"https://{domain}/logo.png",
            "company_description": f"{clean_domain} - Professzionális szolgáltatások",
            "founding_date": "2015-01-01",
            "founder_name": "Alapító Neve",
            "street_address": "Példa utca 1.",
            "city": "Budapest",
            "region": "Budapest",
            "postal_code": "1111",
            "country": "HU",
            "phone": "+36-1-234-5678",
            "area_served": "HU",
            "facebook_url": f"https://facebook.com/{clean_domain.lower()}",
            "linkedin_url": f"https://linkedin.com/company/{clean_domain.lower()}",
            "twitter_url": f"https://twitter.com/{clean_domain.lower()}",
            "instagram_url": f"https://instagram.com/{clean_domain.lower()}",
            "tax_id": "12345678-2-42",
            "vat_id": "HU12345678",
            "business_name": clean_domain,
            "image_url": f"https://{domain}/hero-image.jpg",
            "price_range": "$",
            "business_id": f"https://{domain}/#organization",
            "latitude": 47.4979,
            "longitude": 19.0402,
            "rating_value": "4.8",
            "review_count": "127",
            "product_name": "Termék neve",
            "product_description": "Részletes termékleírás",
            "sku": "SKU123",
            "mpn": "MPN123",
            "brand_name": clean_domain,
            "rating": "4.5",
            "product_url": url,
            "currency": "HUF",
            "price": "9990",
            "price_valid_until": "2024-12-31",
            "seller_name": clean_domain,
            "shipping_cost": "990",
            "headline": analysis.get('meta_and_headings', {}).get('title', 'Cikk címe'),
            "alt_headline": "Alternatív cím",
            "article_image": f"https://{domain}/article-image.jpg",
            "author_name": "Szerző Neve",
            "author_url": f"https://{domain}/author",
            "publisher_name": clean_domain,
            "publisher_logo": f"https://{domain}/logo.png",
            "publish_date": datetime.now().strftime("%Y-%m-%d"),
            "modified_date": datetime.now().strftime("%Y-%m-%d"),
            "article_description": analysis.get('meta_and_headings', {}).get('description', 'Cikk leírása'),
            "article_body": "Cikk teljes szövege...",
            "article_url": url,
            "keywords": ", ".join(self._extract_top_keywords(analysis, 5)),
            "section": "Technológia",
            "word_count": str(analysis.get('content_quality', {}).get('readability', {}).get('word_count', 500))
        }
        
        # Schema template kiválasztása
        if schema_type in self.schema_templates:
            template = self.schema_templates[schema_type]
            
            # Speciális esetek kezelése
            if schema_type == "FAQPage":
                # FAQ items generálása
                faq_items = self._generate_faq_items(page_type, industry)
                defaults["faq_items"] = faq_items
                
            elif schema_type == "HowTo":
                # HowTo steps generálása
                howto_data = self._generate_howto_data(page_type, industry)
                defaults.update(howto_data)
                
            elif schema_type == "Recipe":
                # Recipe adatok
                recipe_data = self._generate_recipe_data()
                defaults.update(recipe_data)
            
            # Template kitöltése
            try:
                return template.safe_substitute(**defaults)
            except:
                return template.substitute(**defaults)
        
        # Ha nincs template, alapértelmezett Organization
        return self.schema_templates["organization"].substitute(**defaults)
    
    def _generate_faq_items(self, page_type: str, industry: str) -> str:
        """FAQ items generálása JSON formátumban"""
        
        faq_templates = {
            "ecommerce": [
                {"q": "Mennyi a szállítási idő?", "a": "Általában 1-3 munkanap, expressz szállítás esetén másnap."},
                {"q": "Van lehetőség visszaküldésre?", "a": "Igen, 30 napos visszaküldési garanciát biztosítunk."},
                {"q": "Milyen fizetési módok érhetők el?", "a": "Bankkártya, PayPal, átutalás és utánvét."}
            ],
            "service": [
                {"q": "Mennyibe kerül a szolgáltatás?", "a": "Áraink egyedi ajánlat alapján alakulnak, kérjen ingyenes árajánlatot."},
                {"q": "Milyen garanciát vállalnak?", "a": "Minden munkánkra 2 év garanciát vállalunk."},
                {"q": "Mennyi idő alatt végeznek?", "a": "A projekt méretétől függően 1-4 hét."}
            ],
            "blog": [
                {"q": "Milyen gyakran jelennek meg új cikkek?", "a": "Hetente 2-3 új tartalmat publikálunk."},
                {"q": "Lehet vendégcikket írni?", "a": "Igen, szívesen fogadunk minőségi vendégcikkeket."},
                {"q": "Hogyan iratkozhatok fel a hírlevélre?", "a": "Az oldal alján található feliratkozás gombbal."}
            ]
        }
        
        faqs = faq_templates.get(industry, faq_templates["service"])
        
        faq_json = []
        for item in faqs:
            faq_json.append(f'''{{
      "@type": "Question",
      "name": "{item['q']}",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "{item['a']}"
      }}
    }}''')
        
        return ",".join(faq_json)
    
    def _generate_howto_data(self, page_type: str, industry: str) -> Dict:
        """HowTo schema adatok generálása"""
        
        howto_data = {
            "howto_title": "Hogyan válasszunk megfelelő szolgáltatót",
            "howto_description": "Részletes útmutató a legjobb szolgáltató kiválasztásához",
            "howto_image": "https://example.com/howto-image.jpg",
            "total_time": "30M",
            "currency": "HUF",
            "cost": "0",
            "supplies": '''[
      {
        "@type": "HowToSupply",
        "name": "Követelmény lista"
      },
      {
        "@type": "HowToSupply",
        "name": "Összehasonlító táblázat"
      }
    ]''',
            "tools": '''[
      {
        "@type": "HowToTool",
        "name": "Online kalkulátor"
      }
    ]''',
            "steps": '''[
      {
        "@type": "HowToStep",
        "text": "Határozza meg az igényeit",
        "image": "https://example.com/step1.jpg",
        "name": "Igényfelmérés",
        "url": "https://example.com/step1"
      },
      {
        "@type": "HowToStep",
        "text": "Kérjen több árajánlatot",
        "image": "https://example.com/step2.jpg",
        "name": "Árajánlat kérés",
        "url": "https://example.com/step2"
      },
      {
        "@type": "HowToStep",
        "text": "Hasonlítsa össze az ajánlatokat",
        "image": "https://example.com/step3.jpg",
        "name": "Összehasonlítás",
        "url": "https://example.com/step3"
      }
    ]'''
        }
        
        return howto_data
    
    def _generate_recipe_data(self) -> Dict:
        """Recipe schema adatok generálása"""
        
        return {
            "recipe_name": "Klasszikus Recept",
            "image1": "https://example.com/recipe1.jpg",
            "image2": "https://example.com/recipe2.jpg",
            "author_name": "Séf Neve",
            "publish_date": datetime.now().strftime("%Y-%m-%d"),
            "recipe_description": "Ínycsiklandó recept részletes leírása",
            "prep_time": "20M",
            "cook_time": "30M",
            "total_time": "50M",
            "keywords": "recept, főzés, gasztronómia",
            "servings": "4 adag",
            "category": "Főétel",
            "cuisine": "Magyar",
            "calories": "350",
            "ingredients": '''[
      "500g alapanyag",
      "2 db zöldség",
      "1 evőkanál fűszer"
    ]''',
            "instructions": '''[
      {
        "@type": "HowToStep",
        "text": "Készítse elő az alapanyagokat"
      },
      {
        "@type": "HowToStep",
        "text": "Főzze meg az alapanyagot"
      },
      {
        "@type": "HowToStep",
        "text": "Tálaljon és díszítsen"
      }
    ]''',
            "rating": "4.7",
            "rating_count": "89"
        }
    
    def _generate_product_combo_schema(self, analysis: Dict, url: str) -> str:
        """E-commerce combo schema pack generálása"""
        
        domain = urlparse(url).netloc
        
        return f'''<script type="application/ld+json">
[
  {{
    "@context": "https://schema.org",
    "@type": "Product",
    "@id": "{url}#product",
    "name": "Termék neve",
    "image": [
      "{url}/product1.jpg",
      "{url}/product2.jpg",
      "{url}/product3.jpg"
    ],
    "description": "Részletes termékleírás SEO optimalizálva",
    "sku": "SKU123",
    "brand": {{
      "@type": "Brand",
      "name": "Márka neve"
    }},
    "offers": {{
      "@type": "Offer",
      "url": "{url}",
      "priceCurrency": "HUF",
      "price": "29990",
      "priceValidUntil": "2024-12-31",
      "availability": "https://schema.org/InStock",
      "seller": {{
        "@type": "Organization",
        "name": "{domain}"
      }}
    }},
    "aggregateRating": {{
      "@type": "AggregateRating",
      "ratingValue": "4.8",
      "reviewCount": "247"
    }},
    "review": [
      {{
        "@type": "Review",
        "reviewRating": {{
          "@type": "Rating",
          "ratingValue": "5"
        }},
        "author": {{
          "@type": "Person",
          "name": "Vásárló Neve"
        }},
        "reviewBody": "Kiváló termék, ajánlom!"
      }}
    ]
  }},
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{
        "@type": "ListItem",
        "position": 1,
        "name": "Főoldal",
        "item": "https://{domain}"
      }},
      {{
        "@type": "ListItem",
        "position": 2,
        "name": "Kategória",
        "item": "https://{domain}/kategoria"
      }},
      {{
        "@type": "ListItem",
        "position": 3,
        "name": "Termék",
        "item": "{url}"
      }}
    ]
  }}
]
</script>'''
    
    def _validate_existing_schemas(self, schema_data: Dict) -> Dict:
        """Meglévő schema-k validálása"""
        
        result = {
            'has_issues': False,
            'issues': [],
            'fixes': []
        }
        
        # Alapvető validációs szabályok
        if schema_data.get('count', {}).get('Organization', 0) > 1:
            result['has_issues'] = True
            result['issues'].append('Több Organization schema (csak 1 kell)')
            result['fixes'].append('Egyesítsd az Organization schema-kat')
        
        if not schema_data.get('has_breadcrumbs') and schema_data.get('count', {}).get('Article', 0) > 0:
            result['has_issues'] = True
            result['issues'].append('Article schema breadcrumb nélkül')
            result['fixes'].append('Adj hozzá BreadcrumbList schema-t')
        
        return result
    
    def _identify_missing_platform_elements(self, platform: str, requirements: Dict,
                                           ai_metrics: Dict, content_quality: Dict) -> Dict:
        """Hiányzó platform elemek azonosítása"""
        
        result = {
            'must_have': [],
            'quick_wins': [],
            'expected_improvement': 15,
            'time_estimate': '2-4 óra',
            'priority_actions': []
        }
        
        # Must have elemek ellenőrzése
        for requirement in requirements.get('must_have', []):
            # Egyszerűsített ellenőrzés
            if "számozott" in requirement.lower() and ai_metrics.get('content_structure', {}).get('lists', {}).get('ordered', 0) < 2:
                result['must_have'].append(requirement)
                result['quick_wins'].append('Adj hozzá számozott listákat')
                result['priority_actions'].append('Számozott útmutatók létrehozása')
            
            elif "q&a" in requirement.lower() and ai_metrics.get('qa_format', {}).get('qa_score', 0) < 50:
                result['must_have'].append(requirement)
                result['quick_wins'].append('Hozz létre FAQ szekciót')
                result['priority_actions'].append('Q&A formátum implementálása')
        
        # Improvement potenciál számítása
        missing_count = len(result['must_have'])
        result['expected_improvement'] = min(30, missing_count * 10)
        
        return result
    
    def _generate_platform_content_example(self, platform: str, page_type: str, industry: str) -> str:
        """Platform-specifikus tartalom példa generálása"""
        
        examples = {
            "chatgpt": {
                "default": """<section class="chatgpt-optimized">
  <h2>Hogyan működik? - Lépésről lépésre</h2>
  <ol>
    <li><strong>Első lépés:</strong> Regisztráció és bejelentkezés</li>
    <li><strong>Második lépés:</strong> Szolgáltatás kiválasztása</li>
    <li><strong>Harmadik lépés:</strong> Beállítások testreszabása</li>
    <li><strong>Negyedik lépés:</strong> Indítás és használat</li>
  </ol>
  
  <h3>Gyakori kérdések</h3>
  <dl>
    <dt>Mennyi időt vesz igénybe?</dt>
    <dd>Általában 15-30 perc a teljes folyamat.</dd>
    <dt>Szükséges előzetes tudás?</dt>
    <dd>Nem, kezdők számára is alkalmas.</dd>
  </dl>
</section>"""
            },
            "claude": {
                "default": """<article class="claude-optimized">
  <section class="context">
    <h2>Háttér és kontextus</h2>
    <p>A téma megértéséhez fontos ismerni a történelmi előzményeket és a jelenlegi 
    piaci környezetet. Az elmúlt években jelentős változások történtek...</p>
    
    <h3>Tudományos alapok</h3>
    <p>Kutatások szerint <cite>(Smith et al., 2023)</cite> a módszer hatékonysága
    92%-os javulást mutat a hagyományos megközelítésekhez képest.</p>
  </section>
  
  <section class="detailed-analysis">
    <h2>Részletes elemzés</h2>
    <p>A probléma több szinten is megközelíthető. Filozófiai szempontból...</p>
  </section>
</article>"""
            },
            "gemini": {
                "default": """<div class="gemini-optimized">
  <h2>Vizuális útmutató</h2>
  <figure>
    <img src="infographic.jpg" alt="Folyamat infografika" loading="lazy">
    <figcaption>A teljes folyamat vizuális ábrázolása</figcaption>
  </figure>
  
  <div class="video-embed">
    <iframe src="https://youtube.com/embed/xxx" title="Bemutató videó"></iframe>
  </div>
  
  <div class="structured-data">
    <script type="application/ld+json">
      {/* Strukturált adatok */}
    </script>
  </div>
</div>"""
            },
            "bing_chat": {
                "default": """<section class="bing-optimized">
  <h2>Források és hivatkozások</h2>
  <p>A legfrissebb információk szerint <a href="https://source1.com" rel="nofollow">[1]</a>
  a trend 2024-ben jelentős növekedést mutat.</p>
  
  <h3>Hivatalos dokumentumok</h3>
  <ul>
    <li><a href="gov-source.pdf">Kormányzati jelentés 2024</a></li>
    <li><a href="industry-report.pdf">Iparági elemzés Q3 2024</a></li>
  </ul>
  
  <div class="fact-check">
    <p>✓ Ellenőrzött tény: Az adatok 2024. október 15-én frissültek.</p>
  </div>
</section>"""
            }
        }
        
        return examples.get(platform, {}).get("default", "<!-- Platform-specifikus tartalom -->")
    
    def _analyze_content_structure_gaps(self, content_structure: Dict, page_type: str) -> Dict:
        """Tartalom struktúra hiányosságok elemzése"""
        
        result = {
            'needs_improvement': False,
            'missing': [],
            'suggestion': '',
            'example': '',
            'guide': ''
        }
        
        # Listák ellenőrzése
        lists = content_structure.get('lists', {})
        if lists.get('ordered', 0) < 2:
            result['needs_improvement'] = True
            result['missing'].append('Számozott listák')
        
        if lists.get('unordered', 0) < 3:
            result['needs_improvement'] = True
            result['missing'].append('Pontozott listák')
        
        # Táblázatok
        if content_structure.get('tables', 0) == 0 and page_type in ['service', 'product']:
            result['needs_improvement'] = True
            result['missing'].append('Összehasonlító táblázatok')
        
        if result['needs_improvement']:
            result['suggestion'] = 'Strukturáld a tartalmat listákkal és táblázatokkal'
            result['example'] = '''<h2>Szolgáltatásaink összehasonlítása</h2>
<table>
  <thead>
    <tr>
      <th>Csomag</th>
      <th>Ár</th>
      <th>Funkciók</th>
      <th>Támogatás</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Alap</td>
      <td>9.990 Ft</td>
      <td>5 funkció</td>
      <td>Email</td>
    </tr>
    <tr>
      <td>Prémium</td>
      <td>19.990 Ft</td>
      <td>Minden funkció</td>
      <td>24/7 telefon</td>
    </tr>
  </tbody>
</table>'''
            result['guide'] = 'AI platformok preferálják a strukturált tartalmat'
        
        return result
    
    def _generate_faq_suggestions(self, page_type: str, industry: str, content_quality: Dict) -> Dict:
        """FAQ javaslatok generálása"""
        
        # Industry és page type alapú kérdések
        questions_db = {
            "ecommerce": {
                "product": [
                    "Milyen méretben kapható a termék?",
                    "Van-e garancia a termékre?",
                    "Hogyan történik a szállítás?",
                    "Lehet-e személyesen átvenni?",
                    "Milyen fizetési módok érhetők el?"
                ],
                "category": [
                    "Melyik terméket válasszam?",
                    "Mi a különbség az egyes modellek között?",
                    "Van-e készleten a termék?",
                    "Mikor érkezik új készlet?"
                ]
            },
            "service": {
                "service": [
                    "Mennyi időt vesz igénybe a szolgáltatás?",
                    "Milyen garanciát vállalnak?",
                    "Kell-e előleget fizetni?",
                    "Hogyan történik az árajánlat kérés?",
                    "Működnek-e hétvégén is?"
                ],
                "homepage": [
                    "Miért minket válasszon?",
                    "Milyen referenciáik vannak?",
                    "Hol dolgoznak?",
                    "Mennyi a kiszállási díj?"
                ]
            },
            "blog": {
                "blog": [
                    "Honnan származnak az információk?",
                    "Lehet-e vendégcikket írni?",
                    "Hogyan idézhetek a cikkből?",
                    "Van-e newsletter?",
                    "Hogyan kereshetek a cikkek között?"
                ]
            }
        }
        
        # Megfelelő kérdések kiválasztása
        industry_questions = questions_db.get(industry, questions_db["service"])
        questions = industry_questions.get(page_type, industry_questions.get("homepage", []))
        
        # HTML struktúra
        html_structure = '''<section id="faq" class="faq-section">
  <h2>Gyakran ismételt kérdések</h2>
  <div class="faq-container" itemscope itemtype="https://schema.org/FAQPage">'''
        
        for q in questions:
            html_structure += f'''
    <div class="faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
      <h3 itemprop="name">{q}</h3>
      <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
        <p itemprop="text">Részletes válasz a kérdésre...</p>
      </div>
    </div>'''
        
        html_structure += '''
  </div>
</section>'''
        
        # FAQ Schema
        faq_schema_items = []
        for q in questions:
            faq_schema_items.append(f'''{{
      "@type": "Question",
      "name": "{q}",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "Részletes válasz..."
      }}
    }}''')
        
        faq_schema = f'''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{",".join(faq_schema_items)}]
}}
</script>'''
        
        return {
            'questions': questions,
            'html_structure': html_structure,
            'faq_schema': faq_schema
        }
    
    def _analyze_multimedia_needs(self, analysis: Dict, page_type: str) -> Dict:
        """Multimédia tartalom szükségletek elemzése"""
        
        result = {
            'needs_improvement': True,
            'current_count': 0,
            'recommended_count': 5,
            'missing': [],
            'suggestions': [],
            'alt_text_guide': '',
            'image_schema': ''
        }
        
        # Page type alapú ajánlások
        recommendations = {
            'homepage': {'images': 5, 'videos': 1, 'infographics': 1},
            'product': {'images': 8, 'videos': 2, 'infographics': 0},
            'blog': {'images': 3, 'videos': 1, 'infographics': 2},
            'service': {'images': 4, 'videos': 1, 'infographics': 1}
        }
        
        rec = recommendations.get(page_type, {'images': 3, 'videos': 0, 'infographics': 0})
        
        result['recommended_count'] = rec['images']
        result['missing'] = ['Hero image', 'Galéria képek', 'Infografika']
        
        result['suggestions'] = [
            'Adj hozzá hero image-t a főoldalhoz',
            'Készíts termék galéria',
            'Használj infografikákat az adatok bemutatására',
            'Optimalizáld a képeket WebP formátumra'
        ]
        
        result['alt_text_guide'] = '''<!-- Alt text példák -->
<img src="product.jpg" alt="Piros bőr kézitáska 30cm, cipzáras, hosszú vállpánttal">
<img src="team.jpg" alt="5 fős szakértői csapatunk egy meeting során az irodában">
<img src="process.jpg" alt="3 lépéses folyamatábra: tervezés, kivitelezés, átadás">'''
        
        result['image_schema'] = '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "ImageObject",
  "contentUrl": "https://example.com/image.jpg",
  "license": "https://example.com/license",
  "acquireLicensePage": "https://example.com/buy-license",
  "creditText": "Fotós neve",
  "creator": {
    "@type": "Person",
    "name": "Fotós neve"
  },
  "copyrightNotice": "© 2024 Company"
}
</script>'''
        
        return result
    
    def _analyze_core_web_vitals(self, psi: Dict) -> List[Dict]:
        """Core Web Vitals elemzése és javítási javaslatok"""
        
        fixes = []
        
        mobile_data = psi.get('mobile', {})
        cwv = mobile_data.get('core_web_vitals', {})
        
        if cwv:
            # LCP elemzés
            lcp = cwv.get('lcp', '')
            if 's' in str(lcp):
                try:
                    lcp_value = float(str(lcp).replace('s', '').strip())
                    if lcp_value > 2.5:
                        fixes.append({
                            "issue": f"Lassú LCP ({lcp})",
                            "severity": "high" if lcp_value > 4 else "medium",
                            "impact": "Rossz első benyomás, magas bounce rate",
                            "solutions": [
                                "Optimalizáld a hero image-t (WebP, lazy load)",
                                "Használj CDN-t a statikus tartalmakhoz",
                                "Preload kritikus fontosságú források",
                                "Csökkentsd a render-blocking CSS/JS méretét"
                            ],
                            "fix_code": '''<!-- Preload hero image -->
<link rel="preload" as="image" href="hero.webp">

<!-- Lazy loading -->
<img src="placeholder.jpg" data-src="actual-image.jpg" loading="lazy">''',
                            "expected_improvement": "LCP < 2.5s"
                        })
                except:
                    pass
            
            # CLS elemzés
            cls = cwv.get('cls', '')
            if cls and float(str(cls)) > 0.1:
                fixes.append({
                    "issue": f"Magas CLS ({cls})",
                    "severity": "medium",
                    "impact": "Zavaró felhasználói élmény",
                    "solutions": [
                        "Adj meg explicit méreteket képeknek és videóknak",
                        "Kerüld a dinamikusan injektált tartalmat",
                        "Használj CSS transform animációkat position helyett"
                    ],
                    "fix_code": '''<!-- Explicit méretek -->
<img src="image.jpg" width="800" height="600" alt="...">

<!-- Placeholder a dinamikus tartalomhoz -->
<div class="ad-placeholder" style="min-height: 250px;">
  <!-- Ad loads here -->
</div>''',
                    "expected_improvement": "CLS < 0.1"
                })
        
        return fixes
    
    def _generate_mobile_optimization_pack(self) -> str:
        """Mobil optimalizációs csomag"""
        
        return '''<!-- Teljes mobil optimalizációs csomag -->

<!-- Viewport -->
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">

<!-- Touch icons -->
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">

<!-- Theme color -->
<meta name="theme-color" content="#4285f4">

<!-- Apple specific -->
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">

<!-- CSS media queries -->
<style>
  @media (max-width: 768px) {
    .container { padding: 15px; }
    .text-large { font-size: 16px; }
    .button { padding: 12px 24px; min-height: 44px; }
  }
</style>'''
    
    def _is_robots_optimized(self, robots: Dict, url: str) -> bool:
        """Robots.txt optimalizáltság ellenőrzése"""
        # Simplified check
        return False  # Mindig javasoljon optimalizálást
    
    def _generate_sitemap_example(self, url: str) -> str:
        """Sitemap példa generálása"""
        
        domain = urlparse(url).netloc
        
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
  <url>
    <loc>https://{domain}/</loc>
    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://{domain}/szolgaltatasok</loc>
    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
    <image:image>
      <image:loc>https://{domain}/szolgaltatasok-hero.jpg</image:loc>
      <image:title>Szolgáltatásaink</image:title>
    </image:image>
  </url>
  <url>
    <loc>https://{domain}/kapcsolat</loc>
    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
</urlset>'''
    
    def _analyze_language_setup(self, analysis: Dict) -> Dict:
        """Nyelvi beállítások elemzése"""
        
        result = {
            'needs_improvement': True,
            'fix': {}
        }
        
        result['fix'] = {
            "issue": "Hiányzó nyelvi és nemzetközi SEO beállítások",
            "severity": "medium",
            "impact": "Helyi keresési hátrány, rossz nemzetközi láthatóság",
            "solution": "Implementálj hreflang tageket és nyelvi meta adatokat",
            "fix_code": '''<!-- Nyelvi beállítások -->
<html lang="hu">
<head>
  <!-- Hreflang -->
  <link rel="alternate" hreflang="hu" href="https://example.hu/">
  <link rel="alternate" hreflang="en" href="https://example.com/">
  <link rel="alternate" hreflang="x-default" href="https://example.com/">
  
  <!-- Nyelvi meta -->
  <meta name="language" content="Hungarian">
  <meta http-equiv="content-language" content="hu">
</head>''',
            "implementation_steps": [
                "Határozd meg a célnyelv(ek)et",
                "Implementáld a hreflang tageket",
                "Állítsd be a helyes lang attribútumot",
                "Használj lokalizált URL struktúrát"
            ]
        }
        
        return result
    
    def _analyze_internal_linking(self, analysis: Dict, page_type: str) -> Dict:
        """Belső linkelés elemzése"""
        
        result = {
            'needs_improvement': True,
            'current_count': 0,
            'recommended_count': 10,
            'strategy': '',
            'example_code': ''
        }
        
        # Page type alapú ajánlások
        recommendations = {
            'homepage': 15,
            'blog': 8,
            'product': 10,
            'service': 12,
            'category': 20
        }
        
        result['recommended_count'] = recommendations.get(page_type, 10)
        
        result['strategy'] = '''Belső linkelési stratégia:
1. Minden oldal linkeljen legalább 3 releváns oldalra
2. Használj leíró anchor text-et
3. Építs topic cluster struktúrát
4. Kerüld a túlzott linkelést
5. Priorizáld a fontos oldalakat'''
        
        result['example_code'] = '''<!-- Kontextuális belső linkek -->
<p>Fedezd fel <a href="/szolgaltatasok/webfejlesztes">webfejlesztési szolgáltatásainkat</a>, 
amelyek segítenek online jelenlétod növelésében. Ha többet szeretnél tudni, 
olvasd el <a href="/blog/weboldal-keszites-lepesrol-lepesre">részletes útmutatónkat</a> 
a weboldalak készítéséről.</p>

<!-- Kapcsolódó tartalmak szekció -->
<aside class="related-content">
  <h3>Kapcsolódó tartalmak</h3>
  <ul>
    <li><a href="/blog/seo-alapok">SEO alapok kezdőknek</a></li>
    <li><a href="/szolgaltatasok/seo-optimalizalas">SEO szolgáltatásaink</a></li>
    <li><a href="/esettanulmanyok/seo-sikertortenet">Sikeres SEO projekt</a></li>
  </ul>
</aside>'''
        
        return result
    
    def _generate_canonical_suggestion(self, url: str, analysis: Dict) -> Optional[Dict]:
        """Canonical tag javaslat"""
        
        return {
            "issue": "Hiányzó canonical tag",
            "impact": "Duplikált tartalom problémák",
            "fix_code": f'<link rel="canonical" href="{url}">',
            "implementation": "Head szekcióban helyezd el",
            "additional_tags": '''<!-- Pagination -->
<link rel="prev" href="/page/1">
<link rel="next" href="/page/3">'''
        }
    
    def _group_platforms_by_requirements(self, weak_platforms: Dict) -> Dict:
        """Platformok csoportosítása hasonló követelmények alapján"""
        
        groups = {
            "content_depth_group": {
                "platforms": [],
                "common_fixes": [],
                "avg_score": 0,
                "priority_actions": [],
                "quick_wins": [],
                "improvement_potential": 0,
                "time_estimate": "1-2 nap",
                "roi_score": 0
            },
            "structure_group": {
                "platforms": [],
                "common_fixes": [],
                "avg_score": 0,
                "priority_actions": [],
                "quick_wins": [],
                "improvement_potential": 0,
                "time_estimate": "4-6 óra",
                "roi_score": 0
            }
        }
        
        # Platform csoportosítás
        for platform, score in weak_platforms.items():
            if platform in ["chatgpt", "claude"]:
                groups["content_depth_group"]["platforms"].append(platform)
                groups["content_depth_group"]["avg_score"] += score
            else:
                groups["structure_group"]["platforms"].append(platform)
                groups["structure_group"]["avg_score"] += score
        
        # Átlag számítás és javítások
        for group_name, group_data in groups.items():
            if group_data["platforms"]:
                platform_count = len(group_data["platforms"])
                group_data["avg_score"] = group_data["avg_score"] / platform_count
                group_data["improvement_potential"] = 85 - group_data["avg_score"]
                group_data["roi_score"] = group_data["improvement_potential"] / 10
                
                if group_name == "content_depth_group":
                    group_data["common_fixes"] = [
                        "Hosszabb, részletesebb tartalom",
                        "Több példa és esettanulmány",
                        "Mélyebb szakmai elemzés"
                    ]
                    group_data["quick_wins"] = [
                        "FAQ szekció hozzáadása",
                        "Tartalom bővítése 500+ szóval"
                    ]
                else:
                    group_data["common_fixes"] = [
                        "Strukturált listák és táblázatok",
                        "Schema markup implementáció",
                        "Multimédia integráció"
                    ]
                    group_data["quick_wins"] = [
                        "Számozott listák hozzáadása",
                        "Képek alt text optimalizálása"
                    ]
        
        return groups
    
    def _generate_ai_content_strategy(self, analysis: Dict, page_type: str, 
                                     industry: str, current_score: int) -> Dict:
        """AI-first tartalom stratégia generálása"""
        
        strategy = {
            "roadmap": [],
            "quick_wins": [],
            "long_term": [],
            "templates": {},
            "kpis": []
        }
        
        # Roadmap a jelenlegi pontszám alapján
        if current_score < 40:
            strategy["roadmap"] = [
                "Hét 1-2: Kritikus SEO hibák javítása",
                "Hét 3-4: Alapvető tartalom struktúra",
                "Hónap 2: Schema implementáció",
                "Hónap 3: Platform optimalizáció"
            ]
        elif current_score < 70:
            strategy["roadmap"] = [
                "Hét 1: Quick wins megvalósítása",
                "Hét 2-3: Tartalom mélység növelése",
                "Hét 4: Platform-specifikus optimalizáció",
                "Hónap 2: Folyamatos finomhangolás"
            ]
        else:
            strategy["roadmap"] = [
                "Hét 1: Versenytárs elemzés",
                "Hét 2: Advanced schema",
                "Hét 3-4: A/B tesztelés",
                "Folyamatos: Monitoring és optimalizáció"
            ]
        
        strategy["quick_wins"] = [
            "Meta tagek optimalizálása",
            "H1 és heading struktúra",
            "FAQ szekció létrehozása",
            "Alt text minden képhez"
        ]
        
        strategy["long_term"] = [
            "Átfogó tartalmi audit",
            "Topic cluster stratégia",
            "Video tartalom integráció",
            "Többnyelvű támogatás"
        ]
        
        strategy["templates"] = {
            "blog_post": "# {Title}\n## Bevezetés\n## Főbb pontok\n### 1. {Point}\n## Összefoglalás\n## GYIK",
            "service_page": "# {Service}\n## Mit kínálunk\n## Hogyan működik (1-2-3)\n## Árak\n## GYIK\n## CTA",
            "product_page": "# {Product}\n## Főbb jellemzők\n## Előnyök\n## Specifikáció\n## Vélemények\n## GYIK"
        }
        
        strategy["kpis"] = [
            "AI readiness score: 70+ (3 hónap)",
            "Organic traffic: +30% (6 hónap)",
            "Featured snippets: 5+ (3 hónap)",
            "Platform visibility: Top 10 (6 hónap)"
        ]
        
        return strategy
    
    def _analyze_voice_search_readiness(self, analysis: Dict) -> Dict:
        """Voice search készültség elemzése"""
        
        result = {
            'needs_improvement': True,
            'score': 40,
            'fixes': [],
            'keywords': [],
            'snippet_strategy': {}
        }
        
        result['fixes'] = [
            "Használj természetes nyelvi kifejezéseket",
            "Optimalizálj hosszú kulcsszavakra",
            "Hozz létre Q&A tartalmat",
            "Használj strukturált adatokat",
            "Optimalizálj helyi keresésekre"
        ]
        
        result['keywords'] = [
            "hogyan lehet...",
            "mi a legjobb módja...",
            "hol találok...",
            "mennyi időbe telik...",
            "miért fontos..."
        ]
        
        result['snippet_strategy'] = {
            'format': 'Kérdés-válasz formátum',
            'length': '40-50 szó a válaszokban',
            'structure': 'Tiszta, egyértelmű válaszok'
        }
        
        return result
    
    def _analyze_featured_snippet_potential(self, analysis: Dict, page_type: str) -> Dict:
        """Featured snippet potenciál elemzése"""
        
        result = {
            'has_potential': True,
            'suitable_types': [],
            'formatting_guide': {},
            'examples': [],
            'target_keywords': [],
            'success_rate': '40%'
        }
        
        if page_type == 'blog':
            result['suitable_types'] = ['Paragraph', 'List', 'Table']
            result['success_rate'] = '60%'
        elif page_type == 'service':
            result['suitable_types'] = ['List', 'Table']
            result['success_rate'] = '45%'
        else:
            result['suitable_types'] = ['Paragraph']
            result['success_rate'] = '30%'
        
        result['formatting_guide'] = {
            'Paragraph': '40-60 szavas bekezdés, amely közvetlenül válaszol a kérdésre',
            'List': 'Számozott vagy pontozott lista 5-8 elemmel',
            'Table': '2-4 oszlopos táblázat összehasonlításhoz'
        }
        
        result['examples'] = [
            '''<p class="snippet-target">
A SEO optimalizálás egy olyan folyamat, amely során a weboldalakat 
úgy alakítjuk át, hogy jobban rangsoroljanak a keresőmotorokban. 
Ez magában foglalja a tartalom, a technikai elemek és a linkek 
optimalizálását.</p>''',
            
            '''<ol class="snippet-target">
  <li>Kulcsszó kutatás</li>
  <li>Tartalom optimalizálás</li>
  <li>Technikai SEO</li>
  <li>Link építés</li>
  <li>Teljesítmény mérés</li>
</ol>'''
        ]
        
        result['target_keywords'] = self._extract_top_keywords(analysis, 10)
        
        return result
    
    def generate_fix_report(self, fixes: Dict, url: str) -> str:
        """Összefoglaló jelentés generálása"""
        
        report = f"""
# 🚀 Enhanced Automatikus Javítási Terv
## Elemzett URL: {url}
## Generálva: {datetime.now().strftime('%Y-%m-%d %H:%M')}

### 📊 Összefoglalás
- Kritikus javítások: {len(fixes.get('critical_fixes', []))}
- SEO fejlesztések: {len(fixes.get('seo_improvements', []))}
- Schema javaslatok: {len(fixes.get('schema_suggestions', []))}
- Quick wins: {len(fixes.get('quick_wins', []))}

### 🚨 Kritikus javítások ({len(fixes.get('critical_fixes', []))})
"""
        
        for i, fix in enumerate(fixes.get('critical_fixes', []), 1):
            report += f"""
#### {i}. {fix.get('issue', 'N/A')}
- **Súlyosság**: {fix.get('severity', 'N/A')}
- **Hatás**: {fix.get('impact', 'N/A')}
- **Megoldás**: 
```html
{fix.get('fix_code', 'N/A')}
```
- **Időigény**: {fix.get('estimated_time', 'N/A')}
- **Várható javulás**: {fix.get('expected_improvement', 'N/A')}
"""
        
        report += f"""
### ⚡ Quick Wins ({len(fixes.get('quick_wins', []))})
"""
        
        for i, win in enumerate(fixes.get('quick_wins', []), 1):
            report += f"""
{i}. **{win.get('task', 'N/A')}**
   - Művelet: {win.get('action', 'N/A')}
   - Idő: {win.get('time', 'N/A')}
   - Hatás: {win.get('impact', 'N/A')}
"""
        
        # Implementációs útmutató
        guide = fixes.get('implementation_guide', {})
        if guide:
            report += f"""
### 📋 Implementációs Útmutató

**Prioritási sorrend:**
"""
            for step in guide.get('priority_order', []):
                report += f"- {step}\n"
            
            report += """
**Becsült időkeret:**
"""
            for task, time in guide.get('estimated_timeline', {}).items():
                report += f"- {task}: {time}\n"
            
            if guide.get('expected_roi'):
                report += f"""
**Várható ROI:**
- 30 nap: {guide['expected_roi'].get('30_nap', 'N/A')}
- 60 nap: {guide['expected_roi'].get('60_nap', 'N/A')}
- 90 nap: {guide['expected_roi'].get('90_nap', 'N/A')}
"""
        
        return report
            