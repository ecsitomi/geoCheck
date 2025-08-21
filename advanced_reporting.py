import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import Counter
import statistics


class AdvancedReportGenerator:
    """Fejlett jelentés generátor GEO elemzésekhez"""
    
    def __init__(self):
        self.report_templates = {
            'executive': self._generate_executive_summary,
            'technical': self._generate_technical_audit,
            'competitor': self._generate_competitor_analysis,
            'action_plan': self._generate_action_plan,
            'progress': self._generate_progress_report
        }
    
    def generate_comprehensive_report(self, analysis_results: List[Dict], 
                                    report_type: str = 'executive',
                                    competitor_data: Optional[List[Dict]] = None) -> Dict:
        """Átfogó jelentés generálása"""
        
        if not analysis_results:
            return {"error": "Nincs adat az elemzéshez"}
        
        # Alapstatisztikák
        base_stats = self._calculate_base_statistics(analysis_results)
        
        # Trendek elemzése
        trends = self._analyze_trends(analysis_results)
        
        # Problémák azonosítása
        issues = self._identify_common_issues(analysis_results)
        
        # Lehetőségek feltárása
        opportunities = self._identify_opportunities(analysis_results)
        
        # Specifikus jelentés generálása
        if report_type in self.report_templates:
            specific_report = self.report_templates[report_type](
                analysis_results, base_stats, trends, issues, opportunities, competitor_data
            )
        else:
            specific_report = {"error": f"Ismeretlen jelentés típus: {report_type}"}
        
        return {
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "summary": base_stats,
            "trends": trends,
            "issues": issues,
            "opportunities": opportunities,
            "detailed_report": specific_report,
            "recommendations": self._generate_strategic_recommendations(base_stats, trends, issues)
        }
    
    def _calculate_base_statistics(self, results: List[Dict]) -> Dict:
        """Alapstatisztikák számítása"""
        
        valid_results = [r for r in results if 'ai_readiness_score' in r]
        
        if not valid_results:
            return {"error": "Nincs érvényes AI readiness score"}
        
        scores = [r['ai_readiness_score'] for r in valid_results]
        
        # Platform specifikus pontszámok
        platform_scores = {}
        for result in valid_results:
            platform_data = result.get('platform_analysis', {})
            for platform, data in platform_data.items():
                if platform != 'summary' and isinstance(data, dict):
                    score = data.get('compatibility_score', 0)
                    if platform not in platform_scores:
                        platform_scores[platform] = []
                    platform_scores[platform].append(score)
        
        # Tartalmi metrikák
        content_metrics = self._analyze_content_metrics(valid_results)
        
        # Technikai metrikák
        technical_metrics = self._analyze_technical_metrics(valid_results)
        
        return {
            "total_sites": len(results),
            "analyzed_sites": len(valid_results),
            "ai_readiness": {
                "average": round(statistics.mean(scores), 1),
                "median": round(statistics.median(scores), 1),
                "std_dev": round(statistics.stdev(scores) if len(scores) > 1 else 0, 1),
                "min": min(scores),
                "max": max(scores),
                "distribution": self._score_distribution(scores)
            },
            "platform_performance": {
                platform: {
                    "average": round(statistics.mean(score_list), 1),
                    "best": max(score_list),
                    "worst": min(score_list)
                } for platform, score_list in platform_scores.items()
            },
            "content_quality": content_metrics,
            "technical_health": technical_metrics,
            "performance_categories": self._categorize_performance(scores)
        }
    
    def _analyze_trends(self, results: List[Dict]) -> Dict:
        """Trendek elemzése"""
        
        trends = {
            "schema_adoption": self._analyze_schema_trends(results),
            "mobile_readiness": self._analyze_mobile_trends(results),
            "content_quality_trends": self._analyze_content_trends(results),
            "ai_optimization_maturity": self._analyze_ai_maturity(results)
        }
        
        return trends
    
    def _identify_common_issues(self, results: List[Dict]) -> List[Dict]:
        """Gyakori problémák azonosítása"""
        
        issues = []
        total_sites = len(results)
        
        # Meta adatok problémái
        missing_titles = sum(1 for r in results if not r.get('meta_and_headings', {}).get('title'))
        missing_descriptions = sum(1 for r in results if not r.get('meta_and_headings', {}).get('description'))
        
        if missing_titles > total_sites * 0.2:
            issues.append({
                "type": "critical",
                "category": "Meta adatok",
                "issue": "Hiányzó title tagek",
                "affected_sites": missing_titles,
                "percentage": round((missing_titles / total_sites) * 100, 1),
                "impact": "Kritikus SEO és AI hatás",
                "priority": 1
            })
        
        if missing_descriptions > total_sites * 0.3:
            issues.append({
                "type": "high",
                "category": "Meta adatok", 
                "issue": "Hiányzó meta description",
                "affected_sites": missing_descriptions,
                "percentage": round((missing_descriptions / total_sites) * 100, 1),
                "impact": "Alacsony CTR a keresőkben",
                "priority": 2
            })
        
        # Schema.org problémák
        no_schema = sum(1 for r in results if sum(r.get('schema', {}).get('count', {}).values()) == 0)
        if no_schema > total_sites * 0.5:
            issues.append({
                "type": "high",
                "category": "Strukturált adatok",
                "issue": "Hiányzó Schema.org markup",
                "affected_sites": no_schema,
                "percentage": round((no_schema / total_sites) * 100, 1),
                "impact": "Gyenge AI megértés és keresőmegjelenés",
                "priority": 3
            })
        
        # Mobile-friendly problémák
        no_viewport = sum(1 for r in results if not r.get('mobile_friendly', {}).get('has_viewport'))
        if no_viewport > total_sites * 0.1:
            issues.append({
                "type": "critical",
                "category": "Mobile optimalizálás",
                "issue": "Hiányzó viewport meta tag",
                "affected_sites": no_viewport,
                "percentage": round((no_viewport / total_sites) * 100, 1),
                "impact": "Rossz mobil felhasználói élmény",
                "priority": 1
            })
        
        # H1 problémák
        h1_issues = sum(1 for r in results if r.get('meta_and_headings', {}).get('h1_count', 0) != 1)
        if h1_issues > total_sites * 0.4:
            issues.append({
                "type": "medium",
                "category": "Tartalom struktúra",
                "issue": "Helytelen H1 struktúra",
                "affected_sites": h1_issues,
                "percentage": round((h1_issues / total_sites) * 100, 1),
                "impact": "Zavaró struktúra AI rendszerek számára",
                "priority": 4
            })
        
        return sorted(issues, key=lambda x: x['priority'])
    
    def _identify_opportunities(self, results: List[Dict]) -> List[Dict]:
        """Lehetőségek azonosítása"""
        
        opportunities = []
        
        # AI platform specifikus lehetőségek
        platform_opportunities = self._analyze_platform_opportunities(results)
        opportunities.extend(platform_opportunities)
        
        # Tartalom lehetőségek
        content_opportunities = self._analyze_content_opportunities(results)
        opportunities.extend(content_opportunities)
        
        # Technikai lehetőségek
        technical_opportunities = self._analyze_technical_opportunities(results)
        opportunities.extend(technical_opportunities)
        
        return opportunities
    
    def _generate_executive_summary(self, results: List[Dict], stats: Dict, 
                                  trends: Dict, issues: List[Dict], 
                                  opportunities: List[Dict], competitor_data: Optional[List[Dict]]) -> Dict:
        """Executive összefoglaló jelentés"""
        
        # KPI-k kiemelése
        key_metrics = {
            "ai_readiness_average": stats['ai_readiness']['average'],
            "sites_needing_immediate_action": len([r for r in results if r.get('ai_readiness_score', 0) < 50]),
            "critical_issues_count": len([i for i in issues if i['type'] == 'critical']),
            "high_impact_opportunities": len([o for o in opportunities if o.get('impact_level') == 'high'])
        }
        
        # ROI becslés
        roi_estimation = self._calculate_roi_estimation(results, opportunities)
        
        # Stratégiai ajánlások
        strategic_recommendations = self._generate_executive_recommendations(stats, issues, opportunities)
        
        return {
            "executive_overview": {
                "portfolio_health": self._assess_portfolio_health(stats),
                "key_findings": self._extract_key_findings(stats, issues, opportunities),
                "competitive_position": self._assess_competitive_position(stats, competitor_data) if competitor_data else None,
                "risk_assessment": self._assess_risks(issues)
            },
            "key_metrics": key_metrics,
            "roi_estimation": roi_estimation,
            "strategic_recommendations": strategic_recommendations,
            "next_steps": self._define_next_steps(issues, opportunities),
            "timeline": self._create_implementation_timeline(issues, opportunities)
        }
    
    def _generate_technical_audit(self, results: List[Dict], stats: Dict,
                                trends: Dict, issues: List[Dict],
                                opportunities: List[Dict], competitor_data: Optional[List[Dict]]) -> Dict:
        """Technikai audit jelentés"""
        
        technical_findings = {
            "infrastructure_analysis": self._analyze_infrastructure(results),
            "performance_metrics": self._analyze_performance_metrics(results),
            "schema_implementation": self._detailed_schema_analysis(results),
            "mobile_optimization": self._detailed_mobile_analysis(results),
            "ai_compatibility": self._detailed_ai_compatibility(results)
        }
        
        code_recommendations = self._generate_code_recommendations(results, issues)
        
        return {
            "technical_overview": technical_findings,
            "detailed_issues": self._categorize_technical_issues(issues),
            "code_fixes": code_recommendations,
            "implementation_priorities": self._prioritize_technical_fixes(issues),
            "testing_recommendations": self._generate_testing_plan(results),
            "monitoring_setup": self._recommend_monitoring_tools()
        }
    
    def _generate_competitor_analysis(self, results: List[Dict], stats: Dict,
                                    trends: Dict, issues: List[Dict],
                                    opportunities: List[Dict], competitor_data: Optional[List[Dict]]) -> Dict:
        """Konkurencia elemzés"""
        
        if not competitor_data:
            return {"error": "Nincs competitor adat megadva"}
        
        # Összehasonlítás
        comparison = self._compare_with_competitors(results, competitor_data)
        
        # Gap analysis
        gaps = self._identify_competitive_gaps(results, competitor_data)
        
        # Best practices
        best_practices = self._extract_competitor_best_practices(competitor_data)
        
        return {
            "competitive_landscape": comparison,
            "performance_gaps": gaps,
            "best_practices": best_practices,
            "opportunities_from_gaps": self._convert_gaps_to_opportunities(gaps),
            "competitive_advantages": self._identify_competitive_advantages(results, competitor_data),
            "threat_assessment": self._assess_competitive_threats(comparison)
        }
    
    def _generate_action_plan(self, results: List[Dict], stats: Dict,
                            trends: Dict, issues: List[Dict],
                            opportunities: List[Dict], competitor_data: Optional[List[Dict]]) -> Dict:
        """Cselekvési terv"""
        
        # Prioritized actions
        prioritized_actions = self._prioritize_all_actions(issues, opportunities)
        
        # Resource allocation
        resource_plan = self._plan_resource_allocation(prioritized_actions)
        
        # Timeline
        detailed_timeline = self._create_detailed_timeline(prioritized_actions)
        
        return {
            "immediate_actions": [a for a in prioritized_actions if a['timeline'] == 'immediate'],
            "short_term_plan": [a for a in prioritized_actions if a['timeline'] == 'short_term'],
            "long_term_strategy": [a for a in prioritized_actions if a['timeline'] == 'long_term'],
            "resource_requirements": resource_plan,
            "success_metrics": self._define_success_metrics(prioritized_actions),
            "milestone_tracking": detailed_timeline,
            "risk_mitigation": self._plan_risk_mitigation(issues, prioritized_actions)
        }
    
    def _generate_progress_report(self, results: List[Dict], stats: Dict,
                                trends: Dict, issues: List[Dict],
                                opportunities: List[Dict], competitor_data: Optional[List[Dict]]) -> Dict:
        """Előrehaladási jelentés (ha van előző adat)"""
        
        # Ez csak akkor működik, ha van korábbi elemzés
        return {
            "note": "A progress report funkcióhoz korábbi elemzési adatok szükségesek",
            "current_baseline": stats,
            "monitoring_setup": {
                "recommended_frequency": "Heti",
                "key_metrics_to_track": [
                    "AI readiness score",
                    "Platform compatibility scores", 
                    "Schema.org coverage",
                    "Content quality metrics"
                ],
                "alerting_thresholds": {
                    "critical": "AI readiness score < 40",
                    "warning": "Score decrease > 10 points",
                    "success": "Score increase > 15 points"
                }
            }
        }
    
    # Helper metódusok az elemzésekhez
    def _score_distribution(self, scores: List[int]) -> Dict:
        """Pontszám eloszlás"""
        return {
            "excellent": len([s for s in scores if s >= 80]),
            "good": len([s for s in scores if 60 <= s < 80]),
            "fair": len([s for s in scores if 40 <= s < 60]),
            "poor": len([s for s in scores if s < 40])
        }
    
    def _categorize_performance(self, scores: List[int]) -> Dict:
        """Teljesítmény kategorizálás"""
        total = len(scores)
        return {
            "high_performers": round((len([s for s in scores if s >= 70]) / total) * 100, 1),
            "average_performers": round((len([s for s in scores if 50 <= s < 70]) / total) * 100, 1),
            "underperformers": round((len([s for s in scores if s < 50]) / total) * 100, 1)
        }
    
    def _analyze_content_metrics(self, results: List[Dict]) -> Dict:
        """Tartalom metrikák elemzése"""
        content_scores = []
        
        for result in results:
            content_quality = result.get('content_quality', {})
            if content_quality:
                overall_score = content_quality.get('overall_quality_score', 0)
                content_scores.append(overall_score)
        
        if not content_scores:
            return {"note": "Nincs tartalom minőség adat"}
        
        return {
            "average_content_score": round(statistics.mean(content_scores), 1),
            "content_distribution": self._score_distribution(content_scores),
            "top_content_areas": self._identify_content_strengths(results),
            "content_gaps": self._identify_content_gaps(results)
        }
    
    def _analyze_technical_metrics(self, results: List[Dict]) -> Dict:
        """Technikai metrikák elemzése"""
        
        mobile_ready = sum(1 for r in results if r.get('mobile_friendly', {}).get('has_viewport'))
        has_sitemap = sum(1 for r in results if r.get('sitemap', {}).get('exists'))
        robots_ok = sum(1 for r in results if r.get('robots_txt', {}).get('can_fetch'))
        
        total = len(results)
        
        return {
            "mobile_readiness": round((mobile_ready / total) * 100, 1),
            "sitemap_coverage": round((has_sitemap / total) * 100, 1),
            "robots_compliance": round((robots_ok / total) * 100, 1),
            "technical_health_score": round(((mobile_ready + has_sitemap + robots_ok) / (total * 3)) * 100, 1)
        }
    
    def _assess_portfolio_health(self, stats: Dict) -> str:
        """Portfolio egészség értékelése"""
        avg_score = stats['ai_readiness']['average']
        
        if avg_score >= 75:
            return "Kiváló - A portfolio jól optimalizált AI rendszerekhez"
        elif avg_score >= 60:
            return "Jó - Kisebb fejlesztésekkel tovább javítható"
        elif avg_score >= 45:
            return "Közepes - Jelentős optimalizálás szükséges"
        else:
            return "Gyenge - Sürgős beavatkozás szükséges"
    
    def _calculate_roi_estimation(self, results: List[Dict], opportunities: List[Dict]) -> Dict:
        """ROI becslés"""
        
        # Egyszerű ROI modell
        current_avg = statistics.mean([r.get('ai_readiness_score', 0) for r in results])
        potential_improvement = sum(o.get('potential_score_increase', 0) for o in opportunities)
        
        estimated_new_avg = min(100, current_avg + (potential_improvement / len(results)))
        
        return {
            "current_average_score": round(current_avg, 1),
            "potential_average_score": round(estimated_new_avg, 1),
            "estimated_improvement": round(estimated_new_avg - current_avg, 1),
            "investment_categories": {
                "low_cost": "Technikai javítások, meta tag optimalizálás",
                "medium_cost": "Schema implementation, tartalom bővítés",
                "high_cost": "Teljes UX átdolgozás, professzionális audit"
            },
            "expected_benefits": [
                "Jobb AI platform megjelenés",
                "Magasabb keresőmotoros rangsorolás",
                "Növekvő organikus forgalom",
                "Jobb felhasználói élmény"
            ]
        }
    
    def _generate_strategic_recommendations(self, stats: Dict, trends: Dict, issues: List[Dict]) -> List[Dict]:
        """Stratégiai ajánlások generálása"""
        
        recommendations = []
        
        # Teljesítmény alapú ajánlások
        avg_score = stats['ai_readiness']['average']
        
        if avg_score < 50:
            recommendations.append({
                "type": "strategic",
                "priority": "critical",
                "recommendation": "AI Readiness alapok megerősítése",
                "rationale": f"Átlagos score ({avg_score}) kritikusan alacsony",
                "actions": [
                    "Meta adatok standardizálása",
                    "Alapvető Schema.org implementáció",
                    "Mobile optimalizálás prioritása"
                ],
                "timeline": "1-2 hónap",
                "expected_impact": "20-30 pontos score növekedés"
            })
        
        # Platform specifikus ajánlások
        platform_scores = stats.get('platform_performance', {})
        lowest_platform = min(platform_scores.items(), key=lambda x: x[1]['average']) if platform_scores else None
        
        if lowest_platform and lowest_platform[1]['average'] < 60:
            recommendations.append({
                "type": "platform_optimization",
                "priority": "high",
                "recommendation": f"{lowest_platform[0].title()} platform optimalizálás",
                "rationale": f"Leggyengébb teljesítmény: {lowest_platform[1]['average']} pont",
                "actions": self._get_platform_specific_actions(lowest_platform[0]),
                "timeline": "2-3 hét",
                "expected_impact": "15-25 pontos platform score növekedés"
            })
        
        return recommendations
    
    def _get_platform_specific_actions(self, platform: str) -> List[str]:
        """Platform specifikus akciók"""
        platform_actions = {
            "chatgpt": [
                "Step-by-step útmutatók létrehozása",
                "FAQ szekciók implementálása",
                "Számozott listák használata"
            ],
            "claude": [
                "Részletes, kontextuális tartalom írása",
                "Hivatkozások és források hozzáadása",
                "Árnyalt nyelvezetű szövegek"
            ],
            "gemini": [
                "Multimédia tartalom hozzáadása",
                "Schema.org markup bővítése",
                "Friss tartalom hangsúlyozása"
            ],
            "bing_chat": [
                "Külső hivatkozások növelése",
                "Forrás jelölések használata",
                "Real-time információk kiemelése"
            ]
        }
        
        return platform_actions.get(platform, ["Általános optimalizálás"])
    
    def generate_pdf_report(self, comprehensive_report: Dict) -> str:
        """PDF jelentés generálása (placeholder - HTML-ből PDF konverzió)"""
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>GEO Fejlett Jelentés</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #667eea; color: white; padding: 20px; }}
        .section {{ margin: 20px 0; }}
        .metric {{ background: #f8f9fa; padding: 10px; margin: 5px 0; }}
        .critical {{ border-left: 4px solid #dc3545; }}
        .high {{ border-left: 4px solid #fd7e14; }}
        .medium {{ border-left: 4px solid #ffc107; }}
        .low {{ border-left: 4px solid #28a745; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>GEO AI Readiness Jelentés</h1>
        <p>Generálva: {comprehensive_report.get('generated_at', 'N/A')}</p>
    </div>
    
    <div class="section">
        <h2>Executive Összefoglaló</h2>
        <div class="metric">
            <strong>Átlagos AI Readiness Score:</strong> 
            {comprehensive_report.get('summary', {}).get('ai_readiness', {}).get('average', 'N/A')}
        </div>
    </div>
    
    <div class="section">
        <h2>Kritikus Problémák</h2>
"""
        
        for issue in comprehensive_report.get('issues', []):
            priority_class = issue.get('type', 'medium')
            html_content += f"""
        <div class="metric {priority_class}">
            <strong>{issue.get('issue', 'Ismeretlen')}</strong><br>
            Érintett oldalak: {issue.get('affected_sites', 0)} ({issue.get('percentage', 0)}%)<br>
            Hatás: {issue.get('impact', 'N/A')}
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>
"""
        
        return html_content
    
    def export_to_excel(self, comprehensive_report: Dict) -> Dict:
        """Excel export adatok előkészítése"""
        
        # Ez egy placeholder - valós implementációhoz pandas szükséges
        excel_data = {
            "summary_sheet": {
                "headers": ["Metrika", "Érték", "Kategória"],
                "data": [
                    ["Átlagos AI Score", comprehensive_report.get('summary', {}).get('ai_readiness', {}).get('average', 0), "Teljesítmény"],
                    ["Elemzett oldalak", comprehensive_report.get('summary', {}).get('analyzed_sites', 0), "Méret"],
                    ["Kritikus problémák", len([i for i in comprehensive_report.get('issues', []) if i.get('type') == 'critical']), "Problémák"]
                ]
            },
            "issues_sheet": {
                "headers": ["Probléma", "Típus", "Érintett oldalak", "Százalék", "Prioritás"],
                "data": [
                    [
                        issue.get('issue', ''),
                        issue.get('type', ''),
                        issue.get('affected_sites', 0),
                        issue.get('percentage', 0),
                        issue.get('priority', 0)
                    ] for issue in comprehensive_report.get('issues', [])
                ]
            }
        }
        
        return excel_data