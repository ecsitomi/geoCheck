import json
import re
from typing import Dict, List, Optional, Set
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse


class SchemaValidator:
    """Schema.org validáció és effectiveness mérés"""
    
    def __init__(self):
        # Schema.org típusok és kötelező mezőik
        self.schema_requirements = {
            "Article": {
                "required": {"headline", "author", "datePublished"},
                "recommended": {"description", "image", "dateModified", "publisher"}
            },
            "FAQPage": {
                "required": {"mainEntity"},
                "recommended": {"about", "author"}
            },
            "HowTo": {
                "required": {"name", "step"},
                "recommended": {"description", "image", "tool", "supply"}
            },
            "Organization": {
                "required": {"name"},
                "recommended": {"url", "logo", "description", "address", "contactPoint"}
            },
            "Product": {
                "required": {"name"},
                "recommended": {"description", "image", "offers", "aggregateRating", "review"}
            },
            "LocalBusiness": {
                "required": {"name", "address"},
                "recommended": {"telephone", "openingHours", "priceRange", "aggregateRating"}
            },
            "WebSite": {
                "required": {"name", "url"},
                "recommended": {"description", "publisher", "potentialAction"}
            },
            "BreadcrumbList": {
                "required": {"itemListElement"},
                "recommended": {}
            }
        }
    
    def validate_with_google_simulation(self, url: str, html: str) -> Dict:
        """Google Rich Results Test szimuláció"""
        soup = BeautifulSoup(html, 'html.parser')
        schemas = self._extract_schemas(soup)
        
        validation_results = []
        total_score = 0
        
        for schema in schemas:
            schema_type = schema.get("@type", "Unknown")
            validation = self._validate_schema_structure(schema, schema_type)
            validation_results.append(validation)
            total_score += validation["score"]
        
        # Google-szerű összesített eredmény
        avg_score = total_score / len(schemas) if schemas else 0
        is_eligible = avg_score >= 70 and len(schemas) > 0
        
        return {
            "is_valid": is_eligible,
            "overall_score": round(avg_score, 1),
            "rich_results_eligible": is_eligible,
            "schema_count": len(schemas),
            "validation_details": validation_results,
            "google_simulation": True,
            "detected_types": [s.get("@type", "Unknown") for s in schemas],
            "issues": self._generate_issues(validation_results),
            "recommendations": self._generate_recommendations(validation_results)
        }
    
    def analyze_schema_completeness(self, schema_data: Dict, content: str) -> Dict:
        """Schema completeness és effectiveness elemzés"""
        if not schema_data or not isinstance(schema_data, dict):
            return {
                "completeness_score": 0,
                "effectiveness_score": 0,
                "missing_schemas": self._recommend_schemas_for_content(content),
                "error": "No valid schema data found"
            }
        
        schema_type = schema_data.get("@type", "Unknown")
        
        if schema_type not in self.schema_requirements:
            return {
                "completeness_score": 50,  # Alappontszám ismeretlen típusért
                "effectiveness_score": 30,
                "schema_type": schema_type,
                "note": f"Unknown schema type: {schema_type}"
            }
        
        requirements = self.schema_requirements[schema_type]
        present_fields = set(schema_data.keys())
        
        # Kötelező mezők ellenőrzése
        required_fields = requirements["required"]
        missing_required = required_fields - present_fields
        required_completeness = (len(required_fields) - len(missing_required)) / len(required_fields) * 100
        
        # Ajánlott mezők ellenőrzése
        recommended_fields = requirements["recommended"]
        missing_recommended = recommended_fields - present_fields
        recommended_completeness = (len(recommended_fields) - len(missing_recommended)) / len(recommended_fields) * 100 if recommended_fields else 100
        
        # Összesített completeness score
        completeness_score = required_completeness * 0.7 + recommended_completeness * 0.3
        
        # Effectiveness score - mennyire hasznos AI platformoknak
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
            "ai_impact_score": self._calculate_ai_impact(schema_data)
        }
    
    def recommend_schemas_for_content(self, content: str, url: str) -> List[Dict]:
        """Tartalom alapú schema ajánlások"""
        recommendations = []
        content_lower = content.lower()
        
        # Article/Blog schema
        if any(indicator in content_lower for indicator in ['cikk', 'article', 'blog', 'post']):
            if not self._has_article_schema(content):
                recommendations.append({
                    "schema_type": "Article",
                    "priority": "high",
                    "reason": "Blog/cikk tartalom detektálva",
                    "estimated_impact": 85,
                    "generated_schema": self._generate_article_schema(content, url)
                })
        
        # FAQ schema
        question_count = content.count('?')
        if question_count >= 3:
            recommendations.append({
                "schema_type": "FAQPage",
                "priority": "high" if question_count >= 5 else "medium",
                "reason": f"{question_count} kérdés találva",
                "estimated_impact": min(90, question_count * 15),
                "generated_schema": self._generate_faq_schema(content)
            })
        
        # HowTo schema
        if self._detect_howto_content(content):
            recommendations.append({
                "schema_type": "HowTo",
                "priority": "high",
                "reason": "Step-by-step útmutató detektálva",
                "estimated_impact": 80,
                "generated_schema": self._generate_howto_schema(content)
            })
        
        # Organization schema
        if self._detect_organization_content(content, url):
            recommendations.append({
                "schema_type": "Organization",
                "priority": "medium",
                "reason": "Vállalati információk detektálva",
                "estimated_impact": 70,
                "generated_schema": self._generate_organization_schema(content, url)
            })
        
        return sorted(recommendations, key=lambda x: x["estimated_impact"], reverse=True)
    
    def measure_schema_effectiveness(self, url: str, schema_data: Dict = None) -> Dict:
        """Schema effectiveness mérése (szimuláció)"""
        if not schema_data:
            return {
                "effectiveness_score": 0,
                "ai_understanding_improvement": 0,
                "search_enhancement": 0,
                "note": "No schema data to measure"
            }
        
        schema_type = schema_data.get("@type", "Unknown")
        
        # AI platform hatás szimulálása
        ai_improvements = {
            "Article": {"chatgpt": 15, "claude": 20, "gemini": 18, "bing": 12},
            "FAQPage": {"chatgpt": 25, "claude": 18, "gemini": 20, "bing": 22},
            "HowTo": {"chatgpt": 30, "claude": 22, "gemini": 25, "bing": 18},
            "Organization": {"chatgpt": 10, "claude": 12, "gemini": 15, "bing": 14},
            "Product": {"chatgpt": 12, "claude": 10, "gemini": 20, "bing": 16}
        }
        
        platform_improvements = ai_improvements.get(schema_type, {})
        avg_improvement = sum(platform_improvements.values()) / len(platform_improvements) if platform_improvements else 0
        
        # CTR hatás becslés
        ctr_impact = self._estimate_ctr_impact(schema_type, schema_data)
        
        # Keresési megjelenés javulás
        search_enhancement = self._estimate_search_enhancement(schema_type, schema_data)
        
        return {
            "effectiveness_score": round(avg_improvement + ctr_impact * 0.5, 1),
            "ai_understanding_improvement": round(avg_improvement, 1),
            "platform_improvements": platform_improvements,
            "ctr_impact_estimate": ctr_impact,
            "search_enhancement": search_enhancement,
            "schema_type": schema_type,
            "measurement_method": "simulation_based"
        }
    
    def _extract_schemas(self, soup: BeautifulSoup) -> List[Dict]:
        """Schema.org elemek kinyerése"""
        schemas = []
        
        # JSON-LD schemas
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                if script.string:
                    data = json.loads(script.string.strip())
                    if isinstance(data, list):
                        schemas.extend(data)
                    else:
                        schemas.append(data)
            except json.JSONDecodeError:
                continue
        
        return schemas
    
    def _validate_schema_structure(self, schema: Dict, schema_type: str) -> Dict:
        """Egyedi schema struktúra validálás"""
        if schema_type not in self.schema_requirements:
            return {
                "schema_type": schema_type,
                "score": 30,
                "is_valid": False,
                "issues": [f"Unknown schema type: {schema_type}"],
                "warnings": []
            }
        
        requirements = self.schema_requirements[schema_type]
        issues = []
        warnings = []
        score = 100
        
        # Kötelező mezők ellenőrzése
        for required_field in requirements["required"]:
            if required_field not in schema:
                issues.append(f"Missing required field: {required_field}")
                score -= 25
        
        # Ajánlott mezők ellenőrzése
        for recommended_field in requirements["recommended"]:
            if recommended_field not in schema:
                warnings.append(f"Missing recommended field: {recommended_field}")
                score -= 5
        
        # Mezők minőségének ellenőrzése
        for field, value in schema.items():
            if field.startswith('@'):
                continue
            
            if not value or (isinstance(value, str) and len(value.strip()) == 0):
                issues.append(f"Empty value for field: {field}")
                score -= 10
            elif isinstance(value, str) and len(value) < 3:
                warnings.append(f"Very short value for field: {field}")
                score -= 2
        
        return {
            "schema_type": schema_type,
            "score": max(0, score),
            "is_valid": score >= 70,
            "issues": issues,
            "warnings": warnings,
            "field_count": len(schema),
            "required_fields_present": len(requirements["required"]) - len([f for f in requirements["required"] if f not in schema])
        }
    
    def _calculate_effectiveness_score(self, schema_data: Dict, content: str) -> float:
        """Schema effectiveness score számítása"""
        base_score = 50
        
        schema_type = schema_data.get("@type", "Unknown")
        
        # Típus-specifikus bónuszok
        type_bonuses = {
            "Article": 20,
            "FAQPage": 25,
            "HowTo": 22,
            "Organization": 15,
            "Product": 18,
            "LocalBusiness": 20
        }
        
        base_score += type_bonuses.get(schema_type, 0)
        
        # Mezők száma és minősége
        field_count = len([k for k in schema_data.keys() if not k.startswith('@')])
        base_score += min(20, field_count * 2)
        
        # Tartalom relevancia
        content_relevance = self._check_content_schema_alignment(schema_data, content)
        base_score += content_relevance * 10
        
        return min(100, base_score)
    
    def _calculate_ai_impact(self, schema_data: Dict) -> float:
        """AI platform hatás becslése"""
        schema_type = schema_data.get("@type", "Unknown")
        
        # AI platform preferenciák
        ai_preferences = {
            "Article": 85,
            "FAQPage": 95,
            "HowTo": 90,
            "Organization": 70,
            "Product": 75,
            "BreadcrumbList": 60
        }
        
        return ai_preferences.get(schema_type, 50)
    
    def _analyze_field_quality(self, schema_data: Dict) -> Dict:
        """Mezők minőségének elemzése"""
        quality_scores = {}
        
        for field, value in schema_data.items():
            if field.startswith('@'):
                continue
            
            quality = 100
            
            if not value:
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
            elif isinstance(value, dict):
                quality = 80  # Strukturált adat jó
            elif isinstance(value, list):
                quality = 90 if value else 0
            
            quality_scores[field] = quality
        
        avg_quality = sum(quality_scores.values()) / len(quality_scores) if quality_scores else 0
        
        return {
            "average_field_quality": round(avg_quality, 1),
            "field_scores": quality_scores,
            "high_quality_fields": [f for f, q in quality_scores.items() if q >= 80],
            "poor_quality_fields": [f for f, q in quality_scores.items() if q < 50]
        }
    
    def _recommend_schemas_for_content(self, content: str) -> List[str]:
        """Hiányzó schema típusok ajánlása"""
        recommendations = []
        content_lower = content.lower()
        
        # Tartalom típus detektálás
        if any(word in content_lower for word in ['cikk', 'article', 'blog', 'post']):
            recommendations.append("Article")
        
        if content.count('?') >= 3:
            recommendations.append("FAQPage")
        
        if any(word in content_lower for word in ['lépés', 'step', 'hogyan', 'how to']):
            recommendations.append("HowTo")
        
        if any(word in content_lower for word in ['cég', 'company', 'vállalat', 'szervezet']):
            recommendations.append("Organization")
        
        return recommendations
    
    def _generate_issues(self, validation_results: List[Dict]) -> List[Dict]:
        """Problémák összegyűjtése"""
        all_issues = []
        
        for result in validation_results:
            for issue in result.get("issues", []):
                all_issues.append({
                    "type": "error",
                    "schema_type": result["schema_type"],
                    "message": issue,
                    "severity": "high"
                })
            
            for warning in result.get("warnings", []):
                all_issues.append({
                    "type": "warning",
                    "schema_type": result["schema_type"],
                    "message": warning,
                    "severity": "medium"
                })
        
        return all_issues
    
    def _generate_recommendations(self, validation_results: List[Dict]) -> List[str]:
        """Javítási javaslatok generálása"""
        recommendations = []
        
        for result in validation_results:
            if result["score"] < 70:
                recommendations.append(f"{result['schema_type']} schema javítása szükséges")
            
            if result.get("issues"):
                recommendations.append(f"Kötelező mezők hozzáadása: {result['schema_type']}")
        
        if not validation_results:
            recommendations.append("Schema.org markup hozzáadása javasolt")
        
        return recommendations
    
    def _has_article_schema(self, content: str) -> bool:
        """Ellenőrzi, hogy van-e már Article schema"""
        # Egyszerű implementáció - valós esetben a meglévő schema-kat ellenőrizné
        return False
    
    def _detect_howto_content(self, content: str) -> bool:
        """HowTo tartalom detektálása"""
        step_indicators = len(re.findall(r'\b(?:lépés|step)\s*\d+|\d+\.\s+[A-ZÁÉÍÓÖŐÚÜŰ]', content, re.I))
        howto_keywords = content.lower().count('hogyan') + content.lower().count('how to')
        
        return step_indicators >= 2 or howto_keywords >= 1
    
    def _detect_organization_content(self, content: str, url: str) -> bool:
        """Szervezeti tartalom detektálása"""
        org_keywords = ['cég', 'company', 'vállalat', 'szervezet', 'about us', 'rólunk']
        return any(keyword in content.lower() for keyword in org_keywords)
    
    def _generate_article_schema(self, content: str, url: str) -> Dict:
        """Article schema generálása"""
        title = content.split('\n')[0][:100] if content else "Generated Article"
        
        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "author": {
                "@type": "Person",
                "name": "Author Name"
            },
            "datePublished": "2024-01-01",
            "dateModified": "2024-01-01",
            "description": content[:200] + "..." if len(content) > 200 else content,
            "url": url
        }
    
    def _generate_faq_schema(self, content: str) -> Dict:
        """FAQ schema generálása"""
        questions = re.findall(r'([^.!?]*\?)', content)[:5]  # Max 5 kérdés
        
        main_entities = []
        for q in questions:
            main_entities.append({
                "@type": "Question",
                "name": q.strip(),
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Generated answer for the question."
                }
            })
        
        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": main_entities
        }
    
    def _generate_howto_schema(self, content: str) -> Dict:
        """HowTo schema generálása"""
        return {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": "How-to Guide",
            "description": "Step by step guide",
            "step": [
                {
                    "@type": "HowToStep",
                    "name": "Step 1",
                    "text": "First step description"
                }
            ]
        }
    
    def _generate_organization_schema(self, content: str, url: str) -> Dict:
        """Organization schema generálása"""
        domain = urlparse(url).netloc.replace('www.', '')
        
        return {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": domain.replace('.', ' ').title(),
            "url": url,
            "description": f"Organization information for {domain}"
        }
    
    def _estimate_ctr_impact(self, schema_type: str, schema_data: Dict) -> float:
        """CTR hatás becslése"""
        ctr_impacts = {
            "Article": 8,
            "FAQPage": 15,
            "HowTo": 12,
            "Product": 20,
            "Organization": 5
        }
        
        return ctr_impacts.get(schema_type, 3)
    
    def _estimate_search_enhancement(self, schema_type: str, schema_data: Dict) -> float:
        """Keresési megjelenés javulás becslése"""
        enhancement_scores = {
            "Article": 70,
            "FAQPage": 85,
            "HowTo": 80,
            "Product": 90,
            "Organization": 60
        }
        
        return enhancement_scores.get(schema_type, 50)
    
    def _check_content_schema_alignment(self, schema_data: Dict, content: str) -> float:
        """Tartalom és schema összehangolásának ellenőrzése"""
        schema_type = schema_data.get("@type", "")
        content_lower = content.lower()
        
        # Egyszerű relevancia számítás
        if schema_type == "Article" and any(word in content_lower for word in ['cikk', 'article']):
            return 1.0
        elif schema_type == "FAQPage" and content.count('?') >= 3:
            return 1.0
        elif schema_type == "HowTo" and any(word in content_lower for word in ['lépés', 'step']):
            return 1.0
        
        return 0.5  # Alapértelmezett közepes relevancia