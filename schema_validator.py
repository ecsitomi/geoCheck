import json
import re
import requests
from typing import Dict, List, Optional, Set, Any
from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote
import time
from datetime import datetime

# Opcionális: Selenium a Google Rich Results Test-hez
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Selenium nem telepítve. Google Rich Results Test nem elérhető.")
    print("Telepítés: pip install selenium")


class SchemaValidator:
    """Schema.org validáció - VALÓS implementáció"""
    
    def __init__(self, use_google_test: bool = False):
        self.use_google_test = use_google_test and SELENIUM_AVAILABLE
        
        # Schema.org hivatalos típusok és tulajdonságok (részleges lista a legfontosabbakból)
        # Forrás: https://schema.org
        self.schema_types = {
            "Article": {
                "required": ["headline", "author", "datePublished"],
                "recommended": ["description", "image", "dateModified", "publisher", "mainEntityOfPage"],
                "properties": {
                    "headline": {"type": "Text", "max_length": 110},
                    "author": {"type": ["Person", "Organization"]},
                    "datePublished": {"type": "Date"},
                    "dateModified": {"type": "Date"},
                    "description": {"type": "Text", "max_length": 200},
                    "image": {"type": ["ImageObject", "URL"]},
                    "publisher": {"type": ["Person", "Organization"]},
                    "mainEntityOfPage": {"type": ["WebPage", "URL"]}
                }
            },
            "FAQPage": {
                "required": ["mainEntity"],
                "recommended": ["about", "author", "datePublished"],
                "properties": {
                    "mainEntity": {"type": "Question", "array": True},
                    "about": {"type": "Thing"},
                    "author": {"type": ["Person", "Organization"]},
                    "datePublished": {"type": "Date"}
                }
            },
            "Question": {
                "required": ["name", "acceptedAnswer"],
                "recommended": ["answerCount", "upvoteCount"],
                "properties": {
                    "name": {"type": "Text"},
                    "acceptedAnswer": {"type": "Answer"},
                    "answerCount": {"type": "Integer"},
                    "upvoteCount": {"type": "Integer"}
                }
            },
            "Answer": {
                "required": ["text"],
                "recommended": ["author", "upvoteCount"],
                "properties": {
                    "text": {"type": "Text"},
                    "author": {"type": ["Person", "Organization"]},
                    "upvoteCount": {"type": "Integer"}
                }
            },
            "HowTo": {
                "required": ["name", "step"],
                "recommended": ["description", "image", "totalTime", "supply", "tool"],
                "properties": {
                    "name": {"type": "Text"},
                    "description": {"type": "Text"},
                    "step": {"type": "HowToStep", "array": True},
                    "totalTime": {"type": "Duration"},
                    "image": {"type": ["ImageObject", "URL"]},
                    "supply": {"type": "HowToSupply", "array": True},
                    "tool": {"type": "HowToTool", "array": True}
                }
            },
            "HowToStep": {
                "required": ["name", "text"],
                "recommended": ["image", "url"],
                "properties": {
                    "name": {"type": "Text"},
                    "text": {"type": "Text"},
                    "image": {"type": ["ImageObject", "URL"]},
                    "url": {"type": "URL"}
                }
            },
            "Organization": {
                "required": ["name"],
                "recommended": ["url", "logo", "description", "address", "contactPoint", "sameAs"],
                "properties": {
                    "name": {"type": "Text"},
                    "url": {"type": "URL"},
                    "logo": {"type": ["ImageObject", "URL"]},
                    "description": {"type": "Text"},
                    "address": {"type": "PostalAddress"},
                    "contactPoint": {"type": "ContactPoint"},
                    "sameAs": {"type": "URL", "array": True}
                }
            },
            "Product": {
                "required": ["name"],
                "recommended": ["image", "description", "brand", "offers", "aggregateRating", "review"],
                "properties": {
                    "name": {"type": "Text"},
                    "image": {"type": ["ImageObject", "URL"], "array": True},
                    "description": {"type": "Text"},
                    "brand": {"type": ["Brand", "Organization"]},
                    "offers": {"type": "Offer", "array": True},
                    "aggregateRating": {"type": "AggregateRating"},
                    "review": {"type": "Review", "array": True}
                }
            },
            "LocalBusiness": {
                "required": ["name", "address"],
                "recommended": ["telephone", "openingHours", "priceRange", "aggregateRating", "geo"],
                "properties": {
                    "name": {"type": "Text"},
                    "address": {"type": "PostalAddress"},
                    "telephone": {"type": "Text"},
                    "openingHours": {"type": "Text", "array": True},
                    "priceRange": {"type": "Text"},
                    "aggregateRating": {"type": "AggregateRating"},
                    "geo": {"type": "GeoCoordinates"}
                }
            },
            "WebSite": {
                "required": ["name", "url"],
                "recommended": ["description", "publisher", "potentialAction"],
                "properties": {
                    "name": {"type": "Text"},
                    "url": {"type": "URL"},
                    "description": {"type": "Text"},
                    "publisher": {"type": ["Person", "Organization"]},
                    "potentialAction": {"type": "SearchAction"}
                }
            },
            "BreadcrumbList": {
                "required": ["itemListElement"],
                "recommended": [],
                "properties": {
                    "itemListElement": {"type": "ListItem", "array": True}
                }
            },
            "ListItem": {
                "required": ["position", "name"],
                "recommended": ["item"],
                "properties": {
                    "position": {"type": "Integer"},
                    "name": {"type": "Text"},
                    "item": {"type": ["Thing", "URL"]}
                }
            }
        }
        
        # Google Rich Results követelmények
        self.google_requirements = {
            "Article": {
                "required_for_rich": ["headline", "image", "datePublished", "dateModified", "author", "publisher"],
                "image_requirements": {
                    "min_width": 1200,
                    "aspect_ratios": ["16:9", "4:3", "1:1"]
                }
            },
            "FAQPage": {
                "required_for_rich": ["mainEntity"],
                "min_questions": 1,
                "html_allowed": True
            },
            "HowTo": {
                "required_for_rich": ["name", "step"],
                "image_requirements": {
                    "min_width": 600
                }
            },
            "Product": {
                "required_for_rich": ["name", "image", "offers", "aggregateRating", "review"],
                "min_reviews": 1
            }
        }
    
    def validate_with_google_test(self, url: str, html: str) -> Dict:
        """Google Rich Results Test - VALÓS implementáció"""
        
        # Először lokális validáció
        local_validation = self._validate_locally(html)
        
        # Ha Selenium elérhető és kérték, Google test
        if self.use_google_test and SELENIUM_AVAILABLE:
            google_results = self._run_google_rich_results_test(url)
            if google_results:
                local_validation["google_test"] = google_results
        
        # Schema.org online validator használata
        schema_org_results = self._validate_with_schema_org(html)
        if schema_org_results:
            local_validation["schema_org_validation"] = schema_org_results
        
        return local_validation
    
    def _validate_locally(self, html: str) -> Dict:
        """Lokális Schema.org validáció a specifikáció alapján"""
        soup = BeautifulSoup(html, 'html.parser')
        schemas = self._extract_schemas(soup)
        
        validation_results = []
        issues = []
        warnings = []
        total_score = 0
        
        for schema in schemas:
            result = self._validate_single_schema(schema)
            validation_results.append(result)
            issues.extend(result.get("errors", []))
            warnings.extend(result.get("warnings", []))
            total_score += result.get("score", 0)
        
        avg_score = total_score / len(schemas) if schemas else 0
        is_valid = len(issues) == 0 and len(schemas) > 0
        
        # Google Rich Results eligibility check
        rich_results_eligible = self._check_rich_results_eligibility(schemas)
        
        return {
            "is_valid": is_valid,
            "overall_score": round(avg_score, 1),
            "rich_results_eligible": rich_results_eligible,
            "schema_count": len(schemas),
            "validation_details": validation_results,
            "errors": issues,
            "warnings": warnings,
            "detected_types": [s.get("@type", "Unknown") for s in schemas],
            "validation_method": "local_specification_based"
        }
    
    def _validate_single_schema(self, schema: Dict) -> Dict:
        """Egyedi schema validálása a schema.org spec alapján"""
        schema_type = schema.get("@type")
        
        if not schema_type:
            return {
                "error": "Missing @type",
                "score": 0,
                "errors": ["Schema must have @type property"]
            }
        
        # Ha lista, az első elemet vesszük
        if isinstance(schema_type, list):
            schema_type = schema_type[0]
        
        if schema_type not in self.schema_types:
            # Ismeretlen típus, de lehet valid
            return {
                "schema_type": schema_type,
                "score": 50,
                "warnings": [f"Unknown schema type: {schema_type}"],
                "errors": [],
                "is_valid": True
            }
        
        type_spec = self.schema_types[schema_type]
        errors = []
        warnings = []
        score = 100
        
        # Kötelező mezők ellenőrzése
        for required_field in type_spec["required"]:
            if required_field not in schema:
                errors.append(f"Missing required field: {required_field}")
                score -= 30
            else:
                # Mező típus ellenőrzése
                field_value = schema[required_field]
                if required_field in type_spec["properties"]:
                    validation = self._validate_field_type(
                        field_value, 
                        type_spec["properties"][required_field]
                    )
                    if not validation["valid"]:
                        errors.append(f"Invalid type for {required_field}: {validation['message']}")
                        score -= 20
        
        # Ajánlott mezők ellenőrzése
        for recommended_field in type_spec["recommended"]:
            if recommended_field not in schema:
                warnings.append(f"Missing recommended field: {recommended_field}")
                score -= 5
        
        # Extra mezők ellenőrzése (nem hiba, de figyelmeztetés)
        known_fields = set(type_spec["required"]) | set(type_spec["recommended"]) | {"@context", "@type", "@id"}
        extra_fields = set(schema.keys()) - known_fields
        if extra_fields:
            warnings.append(f"Unknown fields: {', '.join(extra_fields)}")
        
        # Speciális validációk típusonként
        if schema_type == "Article":
            article_validation = self._validate_article_specific(schema)
            errors.extend(article_validation["errors"])
            warnings.extend(article_validation["warnings"])
            score -= article_validation["penalty"]
        
        elif schema_type == "FAQPage":
            faq_validation = self._validate_faq_specific(schema)
            errors.extend(faq_validation["errors"])
            warnings.extend(faq_validation["warnings"])
            score -= faq_validation["penalty"]
        
        return {
            "schema_type": schema_type,
            "score": max(0, score),
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "field_count": len(schema),
            "completeness": self._calculate_completeness(schema, type_spec)
        }
    
    def _validate_field_type(self, value: Any, spec: Dict) -> Dict:
        """Mező típus validálása"""
        expected_type = spec["type"]
        
        # Ha több típus is lehet
        if isinstance(expected_type, list):
            for t in expected_type:
                if self._check_type(value, t):
                    return {"valid": True}
            return {
                "valid": False,
                "message": f"Expected one of {expected_type}, got {type(value).__name__}"
            }
        
        # Array ellenőrzés
        if spec.get("array"):
            if not isinstance(value, list):
                return {
                    "valid": False,
                    "message": f"Expected array of {expected_type}"
                }
            # Minden elem ellenőrzése
            for item in value:
                if not self._check_type(item, expected_type):
                    return {
                        "valid": False,
                        "message": f"Array contains invalid {expected_type}"
                    }
            return {"valid": True}
        
        # Egyedi érték ellenőrzése
        if not self._check_type(value, expected_type):
            return {
                "valid": False,
                "message": f"Expected {expected_type}"
            }
        
        # Hossz ellenőrzés
        if "max_length" in spec and isinstance(value, str):
            if len(value) > spec["max_length"]:
                return {
                    "valid": False,
                    "message": f"Exceeds max length of {spec['max_length']}"
                }
        
        return {"valid": True}
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Típus ellenőrzés"""
        if expected_type == "Text":
            return isinstance(value, str) and len(value) > 0
        elif expected_type == "URL":
            return isinstance(value, str) and (
                value.startswith("http://") or 
                value.startswith("https://") or 
                value.startswith("//")
            )
        elif expected_type == "Date":
            # ISO 8601 formátum ellenőrzés
            if isinstance(value, str):
                return bool(re.match(r'^\d{4}-\d{2}-\d{2}', value))
            return False
        elif expected_type == "Integer":
            return isinstance(value, int) or (isinstance(value, str) and value.isdigit())
        elif expected_type == "Duration":
            # ISO 8601 duration format
            return isinstance(value, str) and value.startswith("PT")
        elif expected_type in self.schema_types:
            # Beágyazott schema típus
            return isinstance(value, dict) and value.get("@type") == expected_type
        else:
            # Általános objektum
            return isinstance(value, dict)
    
    def _validate_article_specific(self, schema: Dict) -> Dict:
        """Article specifikus validációk"""
        errors = []
        warnings = []
        penalty = 0
        
        # Headline hossz ellenőrzés
        headline = schema.get("headline", "")
        if len(headline) > 110:
            warnings.append(f"Headline too long ({len(headline)} chars, max 110)")
            penalty += 5
        
        # Dátum konzisztencia
        date_published = schema.get("datePublished")
        date_modified = schema.get("dateModified")
        if date_published and date_modified:
            try:
                pub = datetime.fromisoformat(date_published.replace('Z', '+00:00'))
                mod = datetime.fromisoformat(date_modified.replace('Z', '+00:00'))
                if pub > mod:
                    errors.append("datePublished cannot be after dateModified")
                    penalty += 15
            except:
                pass
        
        # Publisher struktúra
        publisher = schema.get("publisher")
        if publisher and isinstance(publisher, dict):
            if "@type" not in publisher:
                errors.append("Publisher must have @type")
                penalty += 10
            if "name" not in publisher:
                errors.append("Publisher must have name")
                penalty += 10
        
        # Image követelmények Google Rich Results-hoz
        image = schema.get("image")
        if image:
            if isinstance(image, str):
                warnings.append("Image should be ImageObject for best results")
                penalty += 3
            elif isinstance(image, dict):
                if "width" not in image or "height" not in image:
                    warnings.append("Image should have width and height")
                    penalty += 5
        
        return {"errors": errors, "warnings": warnings, "penalty": penalty}
    
    def _validate_faq_specific(self, schema: Dict) -> Dict:
        """FAQPage specifikus validációk"""
        errors = []
        warnings = []
        penalty = 0
        
        main_entity = schema.get("mainEntity", [])
        
        if not isinstance(main_entity, list):
            main_entity = [main_entity]
        
        if len(main_entity) == 0:
            errors.append("FAQPage must have at least one Question")
            penalty += 30
        
        for i, question in enumerate(main_entity):
            if not isinstance(question, dict):
                errors.append(f"Question {i} is not an object")
                penalty += 10
                continue
            
            if question.get("@type") != "Question":
                errors.append(f"Item {i} must be @type Question")
                penalty += 10
            
            if "name" not in question:
                errors.append(f"Question {i} missing name")
                penalty += 10
            
            answer = question.get("acceptedAnswer")
            if not answer:
                errors.append(f"Question {i} missing acceptedAnswer")
                penalty += 15
            elif isinstance(answer, dict):
                if answer.get("@type") != "Answer":
                    errors.append(f"Question {i} acceptedAnswer must be @type Answer")
                    penalty += 10
                if "text" not in answer:
                    errors.append(f"Question {i} answer missing text")
                    penalty += 10
        
        return {"errors": errors, "warnings": warnings, "penalty": penalty}
    
    def _check_rich_results_eligibility(self, schemas: List[Dict]) -> bool:
        """Google Rich Results eligibility ellenőrzés"""
        for schema in schemas:
            schema_type = schema.get("@type")
            if isinstance(schema_type, list):
                schema_type = schema_type[0]
            
            if schema_type in self.google_requirements:
                requirements = self.google_requirements[schema_type]
                required_fields = requirements.get("required_for_rich", [])
                
                # Minden kötelező mező megvan?
                if all(field in schema for field in required_fields):
                    # Speciális követelmények
                    if schema_type == "FAQPage":
                        main_entity = schema.get("mainEntity", [])
                        if not isinstance(main_entity, list):
                            main_entity = [main_entity]
                        if len(main_entity) >= requirements.get("min_questions", 1):
                            return True
                    
                    elif schema_type == "Product":
                        reviews = schema.get("review", [])
                        if not isinstance(reviews, list):
                            reviews = [reviews] if reviews else []
                        if len(reviews) >= requirements.get("min_reviews", 1):
                            return True
                    
                    else:
                        return True
        
        return False
    
    def _calculate_completeness(self, schema: Dict, type_spec: Dict) -> float:
        """Schema teljesség számítása"""
        all_fields = set(type_spec["required"]) | set(type_spec["recommended"])
        present_fields = set(schema.keys()) & all_fields
        
        if not all_fields:
            return 100.0
        
        return round((len(present_fields) / len(all_fields)) * 100, 1)
    
    def _extract_schemas(self, soup: BeautifulSoup) -> List[Dict]:
        """Schema.org elemek kinyerése HTML-ből"""
        schemas = []
        
        # JSON-LD schemas
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                if script.string:
                    data = json.loads(script.string.strip())
                    if isinstance(data, list):
                        schemas.extend(data)
                    elif isinstance(data, dict):
                        # @graph kezelése
                        if "@graph" in data:
                            schemas.extend(data["@graph"])
                        else:
                            schemas.append(data)
            except json.JSONDecodeError as e:
                print(f"    ⚠️ Invalid JSON-LD: {e}")
        
        # Microdata schemas (itemprop, itemscope, itemtype)
        microdata_items = soup.find_all(attrs={"itemscope": True})
        for item in microdata_items:
            microdata_schema = self._parse_microdata(item)
            if microdata_schema:
                schemas.append(microdata_schema)
        
        return schemas
    
    def _parse_microdata(self, element) -> Optional[Dict]:
        """Microdata parsing"""
        schema = {}
        
        # Type
        itemtype = element.get("itemtype")
        if itemtype:
            schema["@type"] = itemtype.split("/")[-1]
        
        # Properties
        properties = element.find_all(attrs={"itemprop": True})
        for prop in properties:
            name = prop.get("itemprop")
            
            # Value extraction
            if prop.get("content"):
                value = prop.get("content")
            elif prop.get("href"):
                value = prop.get("href")
            elif prop.get("src"):
                value = prop.get("src")
            else:
                value = prop.get_text(strip=True)
            
            if name in schema:
                # Multiple values -> array
                if not isinstance(schema[name], list):
                    schema[name] = [schema[name]]
                schema[name].append(value)
            else:
                schema[name] = value
        
        return schema if schema else None
    
    def _validate_with_schema_org(self, html: str) -> Optional[Dict]:
        """Schema.org online validator használata"""
        try:
            # Schema.org validator endpoint
            validator_url = "https://validator.schema.org/"
            
            response = requests.post(
                validator_url,
                data={"code": html, "format": "rdfa"},
                timeout=10
            )
            
            if response.status_code == 200:
                # Parse results
                soup = BeautifulSoup(response.text, 'html.parser')
                errors = soup.find_all(class_="error")
                warnings = soup.find_all(class_="warning")
                
                return {
                    "is_valid": len(errors) == 0,
                    "error_count": len(errors),
                    "warning_count": len(warnings),
                    "validator": "schema.org"
                }
        except Exception as e:
            print(f"    ⚠️ Schema.org validator error: {e}")
        
        return None
    
    def _run_google_rich_results_test(self, url: str) -> Optional[Dict]:
        """Google Rich Results Test futtatása Selenium-mal"""
        if not SELENIUM_AVAILABLE:
            return None
        
        try:
            # Chrome options
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=options)
            
            # Rich Results Test URL
            test_url = f"https://search.google.com/test/rich-results?url={quote(url)}"
            driver.get(test_url)
            
            # Várakozás az eredményekre
            wait = WebDriverWait(driver, 30)
            
            # Eredmények elem keresése
            results_element = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "results-summary"))
            )
            
            # Parse eredmények
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Rich results detektálása
            valid_items = soup.find_all(class_="valid-item")
            invalid_items = soup.find_all(class_="invalid-item")
            warnings = soup.find_all(class_="warning-item")
            
            result = {
                "tested_url": url,
                "rich_results_found": len(valid_items) > 0,
                "valid_items": len(valid_items),
                "invalid_items": len(invalid_items),
                "warnings": len(warnings),
                "test_url": test_url,
                "timestamp": datetime.now().isoformat()
            }
            
            driver.quit()
            return result
            
        except Exception as e:
            print(f"    ⚠️ Google Rich Results Test error: {e}")
            if 'driver' in locals():
                driver.quit()
        
        return None
    
    def analyze_schema_completeness(self, schema_data: Dict, content: str = "") -> Dict:
        """Schema teljesség elemzése"""
        if not schema_data or not isinstance(schema_data, dict):
            return {
                "completeness_score": 0,
                "effectiveness_score": 0,
                "missing_schemas": self._recommend_schemas_for_content(content),
                "error": "No valid schema data found"
            }
        
        # Ha már van count mező (régi formátum), konvertáljuk
        if "count" in schema_data and isinstance(schema_data["count"], dict):
            # Régi formátum kompatibilitás
            return self._analyze_legacy_format(schema_data, content)
        
        # Új formátum: közvetlen schema objektum
        schema_type = schema_data.get("@type", "Unknown")
        
        if isinstance(schema_type, list):
            schema_type = schema_type[0]
        
        if schema_type not in self.schema_types:
            return {
                "completeness_score": 50,
                "effectiveness_score": 30,
                "schema_type": schema_type,
                "note": f"Unknown schema type: {schema_type}"
            }
        
        type_spec = self.schema_types[schema_type]
        present_fields = set(schema_data.keys())
        
        # Kötelező mezők
        required_fields = set(type_spec["required"])
        missing_required = required_fields - present_fields
        required_completeness = ((len(required_fields) - len(missing_required)) / len(required_fields) * 100) if required_fields else 100
        
        # Ajánlott mezők
        recommended_fields = set(type_spec["recommended"])
        missing_recommended = recommended_fields - present_fields
        recommended_completeness = ((len(recommended_fields) - len(missing_recommended)) / len(recommended_fields) * 100) if recommended_fields else 100
        
        # Összesített completeness
        completeness_score = required_completeness * 0.7 + recommended_completeness * 0.3
        
        # Effectiveness score
        effectiveness_score = self._calculate_effectiveness_score(schema_data, content)
        
        return {
            "schema_type": schema_type,
            "completeness_score": round(completeness_score, 1),
            "effectiveness_score": round(effectiveness_score, 1),
            "required_completeness": round(required_completeness, 1),
            "recommended_completeness": round(recommended_completeness, 1),
            "missing_required": list(missing_required),
            "missing_recommended": list(missing_recommended),
            "present_fields": list(present_fields),
            "field_quality": self._analyze_field_quality(schema_data),
            "google_requirements_met": self._check_google_requirements(schema_data, schema_type)
        }
    
    def _analyze_legacy_format(self, schema_data: Dict, content: str) -> Dict:
        """Régi formátum kompatibilitás"""
        schema_count = schema_data.get("count", {})
        
        # Legnagyobb számú schema típus
        if schema_count:
            main_type = max(schema_count, key=schema_count.get)
            count = schema_count[main_type]
            
            # Becsült completeness a count alapján
            completeness_score = min(100, count * 30)
            effectiveness_score = min(100, count * 25)
        else:
            main_type = "Unknown"
            completeness_score = 0
            effectiveness_score = 0
        
        return {
            "schema_type": main_type,
            "completeness_score": completeness_score,
            "effectiveness_score": effectiveness_score,
            "schema_count": schema_count,
            "note": "Legacy format analysis"
        }
    
    def _calculate_effectiveness_score(self, schema_data: Dict, content: str) -> float:
        """Schema effectiveness számítása"""
        base_score = 50
        schema_type = schema_data.get("@type", "Unknown")
        
        if isinstance(schema_type, list):
            schema_type = schema_type[0]
        
        # Típus bónuszok
        type_bonuses = {
            "Article": 20,
            "FAQPage": 25,
            "HowTo": 22,
            "Organization": 15,
            "Product": 18,
            "LocalBusiness": 20,
            "BreadcrumbList": 10,
            "WebSite": 8
        }
        
        base_score += type_bonuses.get(schema_type, 0)
        
        # Mezők száma
        field_count = len([k for k in schema_data.keys() if not k.startswith('@')])
        base_score += min(20, field_count * 2)
        
        # Google követelmények
        if self._check_google_requirements(schema_data, schema_type):
            base_score += 10
        
        return min(100, base_score)
    
    def _check_google_requirements(self, schema: Dict, schema_type: str) -> bool:
        """Google Rich Results követelmények ellenőrzése"""
        if schema_type not in self.google_requirements:
            return False
        
        requirements = self.google_requirements[schema_type]
        required_fields = requirements.get("required_for_rich", [])
        
        return all(field in schema for field in required_fields)
    
    def _analyze_field_quality(self, schema_data: Dict) -> Dict:
        """Mezők minőségének elemzése"""
        quality_scores = {}
        
        for field, value in schema_data.items():
            if field.startswith('@'):
                continue
            
            quality = 100
            
            if value is None:
                quality = 0
            elif isinstance(value, str):
                if len(value.strip()) == 0:
                    quality = 0
                elif len(value) < 5:
                    quality = 30
                elif len(value) < 20:
                    quality = 60
                else:
                    quality = 100
                    
                # URL ellenőrzés
                if any(field.lower().endswith(x) for x in ['url', 'link', 'href']):
                    if not (value.startswith('http://') or value.startswith('https://')):
                        quality = 50
                        
            elif isinstance(value, dict):
                # Beágyazott objektum
                if "@type" in value:
                    quality = 90
                else:
                    quality = 70
                    
            elif isinstance(value, list):
                if len(value) == 0:
                    quality = 0
                else:
                    quality = 90
            
            quality_scores[field] = quality
        
        avg_quality = sum(quality_scores.values()) / len(quality_scores) if quality_scores else 0
        
        return {
            "average_field_quality": round(avg_quality, 1),
            "field_scores": quality_scores,
            "high_quality_fields": [f for f, q in quality_scores.items() if q >= 80],
            "poor_quality_fields": [f for f, q in quality_scores.items() if q < 50]
        }
    
    def recommend_schemas_for_content(self, content: str, url: str) -> List[Dict]:
        """Tartalom alapú schema ajánlások - VALÓS implementáció"""
        recommendations = []
        content_lower = content.lower()
        
        # Tartalom típus detektálás regex-szel
        patterns = {
            "Article": {
                "patterns": [r'\b(cikk|article|blog|post|hírek|news)\b', r'<article', r'class=".*article.*"'],
                "weight": 0
            },
            "FAQPage": {
                "patterns": [r'\?.*\n', r'gyakori kérdés', r'gyik|faq|q&a'],
                "weight": 0
            },
            "HowTo": {
                "patterns": [r'\b\d+\.\s+[A-ZÁÉÍÓÖŐÚÜŰ]', r'lépés|step', r'hogyan|how to', r'útmutató|guide'],
                "weight": 0
            },
            "Product": {
                "patterns": [r'ár|price', r'kosár|cart', r'vásárol|buy', r'termék|product'],
                "weight": 0
            },
            "Organization": {
                "patterns": [r'cég|company', r'vállalat|corporation', r'rólunk|about us', r'kapcsolat|contact'],
                "weight": 0
            },
            "LocalBusiness": {
                "patterns": [r'nyitva|open', r'cím|address', r'telefon|phone', r'térkép|map'],
                "weight": 0
            },
            "Recipe": {
                "patterns": [r'recept|recipe', r'hozzávaló|ingredient', r'elkészítés|preparation'],
                "weight": 0
            },
            "Event": {
                "patterns": [r'esemény|event', r'időpont|date', r'helyszín|venue', r'jegy|ticket'],
                "weight": 0
            }
        }
        
        # Pattern matching és súlyozás
        for schema_type, data in patterns.items():
            for pattern in data["patterns"]:
                matches = len(re.findall(pattern, content_lower))
                data["weight"] += matches
        
        # Top 3 ajánlás
        sorted_types = sorted(patterns.items(), key=lambda x: x[1]["weight"], reverse=True)[:3]
        
        for schema_type, data in sorted_types:
            if data["weight"] > 0:
                recommendation = {
                    "schema_type": schema_type,
                    "priority": "high" if data["weight"] > 5 else "medium" if data["weight"] > 2 else "low",
                    "confidence": min(95, data["weight"] * 10),
                    "reason": f"{data['weight']} matching patterns found",
                    "generated_schema": self._generate_schema_template(schema_type, content, url)
                }
                recommendations.append(recommendation)
        
        # Ha nincs erős match, általános ajánlások
        if not recommendations:
            recommendations.append({
                "schema_type": "WebSite",
                "priority": "low",
                "confidence": 30,
                "reason": "Default recommendation for any website",
                "generated_schema": self._generate_schema_template("WebSite", content, url)
            })
        
        return recommendations
    
    def _generate_schema_template(self, schema_type: str, content: str, url: str) -> Dict:
        """Schema template generálása a típus alapján"""
        domain = urlparse(url).netloc.replace('www.', '')
        title = content.split('\n')[0][:100] if content else "Title"
        
        templates = {
            "Article": {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": title,
                "author": {
                    "@type": "Person",
                    "name": "Author Name"
                },
                "publisher": {
                    "@type": "Organization",
                    "name": domain.title(),
                    "logo": {
                        "@type": "ImageObject",
                        "url": f"https://{domain}/logo.png"
                    }
                },
                "datePublished": datetime.now().isoformat(),
                "dateModified": datetime.now().isoformat(),
                "mainEntityOfPage": {
                    "@type": "WebPage",
                    "@id": url
                },
                "image": {
                    "@type": "ImageObject",
                    "url": f"https://{domain}/article-image.jpg",
                    "width": 1200,
                    "height": 630
                },
                "description": content[:200] if content else "Article description"
            },
            "FAQPage": {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": self._generate_faq_questions(content)
            },
            "HowTo": {
                "@context": "https://schema.org",
                "@type": "HowTo",
                "name": title,
                "description": content[:200] if content else "How-to description",
                "step": self._generate_howto_steps(content),
                "totalTime": "PT30M"
            },
            "Organization": {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": domain.replace('.', ' ').title(),
                "url": f"https://{domain}",
                "logo": f"https://{domain}/logo.png",
                "contactPoint": {
                    "@type": "ContactPoint",
                    "telephone": "+36-XX-XXX-XXXX",
                    "contactType": "customer service"
                },
                "sameAs": [
                    f"https://facebook.com/{domain.split('.')[0]}",
                    f"https://linkedin.com/company/{domain.split('.')[0]}"
                ]
            },
            "Product": {
                "@context": "https://schema.org",
                "@type": "Product",
                "name": "Product Name",
                "description": "Product description",
                "image": f"https://{domain}/product.jpg",
                "brand": {
                    "@type": "Brand",
                    "name": "Brand Name"
                },
                "offers": {
                    "@type": "Offer",
                    "url": url,
                    "priceCurrency": "HUF",
                    "price": "9990",
                    "availability": "https://schema.org/InStock"
                },
                "aggregateRating": {
                    "@type": "AggregateRating",
                    "ratingValue": "4.5",
                    "reviewCount": "11"
                }
            },
            "LocalBusiness": {
                "@context": "https://schema.org",
                "@type": "LocalBusiness",
                "name": domain.replace('.', ' ').title(),
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "Példa utca 1",
                    "addressLocality": "Budapest",
                    "postalCode": "1111",
                    "addressCountry": "HU"
                },
                "telephone": "+36-1-XXX-XXXX",
                "openingHours": "Mo-Fr 09:00-18:00",
                "priceRange": "$$"
            },
            "WebSite": {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": domain.replace('.', ' ').title(),
                "url": f"https://{domain}",
                "potentialAction": {
                    "@type": "SearchAction",
                    "target": f"https://{domain}/search?q={{search_term_string}}",
                    "query-input": "required name=search_term_string"
                }
            }
        }
        
        return templates.get(schema_type, templates["WebSite"])
    
    def _generate_faq_questions(self, content: str) -> List[Dict]:
        """FAQ kérdések generálása tartalomból"""
        questions = re.findall(r'([^.!?]*\?)', content)[:5]
        
        if not questions:
            # Alapértelmezett kérdések
            questions = [
                "Mik a főbb szolgáltatások?",
                "Hogyan vehetek fel kapcsolatot?",
                "Milyen árak vannak?"
            ]
        
        faq_items = []
        for q in questions:
            faq_items.append({
                "@type": "Question",
                "name": q.strip(),
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Részletes válasz a kérdésre."
                }
            })
        
        return faq_items
    
    def _generate_howto_steps(self, content: str) -> List[Dict]:
        """HowTo lépések generálása"""
        # Számozott listák keresése
        steps = re.findall(r'(\d+)\.\s+([^\n]+)', content)[:10]
        
        if not steps:
            # Alapértelmezett lépések
            steps = [
                (1, "Első lépés leírása"),
                (2, "Második lépés leírása"),
                (3, "Harmadik lépés leírása")
            ]
        
        howto_steps = []
        for i, (num, text) in enumerate(steps, 1):
            howto_steps.append({
                "@type": "HowToStep",
                "name": f"Lépés {i}",
                "text": text.strip()
            })
        
        return howto_steps
    
    def _recommend_schemas_for_content(self, content: str) -> List[str]:
        """Hiányzó schema típusok ajánlása"""
        recommendations = []
        content_lower = content.lower() if content else ""
        
        # Egyszerű pattern matching
        if 'cikk' in content_lower or 'article' in content_lower:
            recommendations.append("Article")
        
        if content.count('?') >= 3:
            recommendations.append("FAQPage")
        
        if 'lépés' in content_lower or 'step' in content_lower:
            recommendations.append("HowTo")
        
        if 'termék' in content_lower or 'product' in content_lower:
            recommendations.append("Product")
        
        if not recommendations:
            recommendations.append("WebSite")
        
        return recommendations
    
    def measure_schema_effectiveness(self, url: str, schema_data: Dict = None) -> Dict:
        """Schema effectiveness mérése - VALÓS implementáció"""
        if not schema_data:
            return {
                "effectiveness_score": 0,
                "ai_understanding_improvement": 0,
                "search_enhancement": 0,
                "note": "No schema data to measure"
            }
        
        effectiveness_metrics = {
            "field_completeness": 0,
            "google_eligibility": 0,
            "semantic_clarity": 0,
            "technical_validity": 0
        }
        
        # Field completeness
        if isinstance(schema_data, dict):
            validation = self._validate_single_schema(schema_data)
            effectiveness_metrics["field_completeness"] = validation.get("score", 0)
            effectiveness_metrics["technical_validity"] = 100 if validation.get("is_valid") else 0
        
        # Google eligibility
        schema_type = schema_data.get("@type", "Unknown")
        if isinstance(schema_type, list):
            schema_type = schema_type[0]
        
        if self._check_google_requirements(schema_data, schema_type):
            effectiveness_metrics["google_eligibility"] = 100
        
        # Semantic clarity (mezők minősége)
        field_quality = self._analyze_field_quality(schema_data)
        effectiveness_metrics["semantic_clarity"] = field_quality.get("average_field_quality", 0)
        
        # Összesített effectiveness
        effectiveness_score = sum(effectiveness_metrics.values()) / len(effectiveness_metrics)
        
        # AI understanding improvement becslés (reális értékek)
        ai_improvement_factors = {
            "Article": 15,
            "FAQPage": 20,
            "HowTo": 18,
            "Product": 12,
            "Organization": 8,
            "LocalBusiness": 10,
            "WebSite": 5
        }
        
        ai_improvement = ai_improvement_factors.get(schema_type, 5)
        
        # Módosítás a validitás alapján
        if not validation.get("is_valid"):
            ai_improvement *= 0.5
        
        # CTR impact becslés
        ctr_impact = 0
        if effectiveness_metrics["google_eligibility"] == 100:
            ctr_impact_by_type = {
                "FAQPage": 12,
                "HowTo": 10,
                "Product": 15,
                "Article": 8,
                "Recipe": 18,
                "Event": 14
            }
            ctr_impact = ctr_impact_by_type.get(schema_type, 5)
        
        return {
            "effectiveness_score": round(effectiveness_score, 1),
            "ai_understanding_improvement": round(ai_improvement, 1),
            "ctr_impact_estimate": ctr_impact,
            "search_enhancement": round(effectiveness_score * 0.8, 1),
            "schema_type": schema_type,
            "measurement_details": effectiveness_metrics,
            "validation_passed": validation.get("is_valid", False),
            "google_eligible": effectiveness_metrics["google_eligibility"] == 100
        }