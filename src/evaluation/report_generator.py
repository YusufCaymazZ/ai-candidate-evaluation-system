"""
Report Generator for Candidate Evaluation System

This module provides comprehensive report generation functionality, combining
CV analysis and interview scoring results into professional evaluation reports.
"""

import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
from loguru import logger

from src.models.llm_client import LLMClient
from src.utils.prompt_templates import PromptTemplates
from src.utils.file_utils import FileUtils


class ReportGenerator:
    """
    Comprehensive report generation system for candidate evaluation.
    
    Combines CV analysis and interview scoring results to create
    professional evaluation reports in multiple formats.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize the report generator with LLM client and utilities.
        
        Args:
            config_path: Path to configuration file
        """
        self.llm_client = LLMClient(config_path)
        self.file_utils = FileUtils()
        self.prompt_templates = PromptTemplates()
        
        logger.info("Report Generator initialized successfully")
    
    def generate_comprehensive_report(self, cv_analysis: Dict, interview_scores: Dict, 
                                    candidate_info: Dict = None) -> Dict:
        """
        Generate a comprehensive evaluation report combining CV and interview results.
        
        Args:
            cv_analysis: Results from CV analysis
            interview_scores: Results from interview scoring
            candidate_info: Basic candidate information (optional)
            
        Returns:
            Comprehensive report in multiple formats
        """
        try:
            logger.info("Generating comprehensive evaluation report")
            
            # Prepare candidate information
            if candidate_info is None:
                candidate_info = self._extract_candidate_info(cv_analysis)
            
            # Generate LLM-based report
            llm_report = self._generate_llm_report(cv_analysis, interview_scores, candidate_info)
            
            # Generate structured report
            structured_report = self._generate_structured_report(cv_analysis, interview_scores, candidate_info)
            
            # Generate summary report
            summary_report = self._generate_summary_report(cv_analysis, interview_scores, candidate_info)
            
            # Combine all reports
            comprehensive_report = {
                "candidate_info": candidate_info,
                "cv_analysis": cv_analysis,
                "interview_scores": interview_scores,
                "llm_report": llm_report,
                "structured_report": structured_report,
                "summary_report": summary_report,
                "final_recommendation": self._generate_final_recommendation(cv_analysis, interview_scores),
                "metadata": {
                    "generation_timestamp": self._get_timestamp(),
                    "report_version": "1.0"
                }
            }
            
            return comprehensive_report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            return {"error": str(e)}
    
    def _extract_candidate_info(self, cv_analysis: Dict) -> Dict:
        """
        Extract basic candidate information from CV analysis.
        
        Args:
            cv_analysis: CV analysis results
            
        Returns:
            Basic candidate information
        """
        candidate_info = {
            "name": "Unknown",
            "email": "Unknown",
            "phone": "Unknown",
            "experience_level": "Unknown",
            "years_experience": "Unknown",
            "key_skills": [],
            "education": "Unknown"
        }
        
        try:
            # Extract from CV skills if available
            if "cv_skills" in cv_analysis:
                cv_skills = cv_analysis["cv_skills"]
                if "experience_level" in cv_skills:
                    candidate_info["experience_level"] = cv_skills["experience_level"]
                if "years_experience" in cv_skills:
                    candidate_info["years_experience"] = cv_skills["years_experience"]
                
                # Extract key skills
                if "technical_skills" in cv_skills:
                    tech_skills = cv_skills["technical_skills"]
                    for category, skills in tech_skills.items():
                        if isinstance(skills, list):
                            candidate_info["key_skills"].extend(skills[:3])  # Top 3 per category
            
            # Extract from LLM analysis if available
            if "llm_analysis" in cv_analysis:
                llm_analysis = cv_analysis["llm_analysis"]
                if "experience_assessment" in llm_analysis:
                    exp_assessment = llm_analysis["experience_assessment"]
                    if "years_experience" in exp_assessment:
                        candidate_info["years_experience"] = exp_assessment["years_experience"]
                    if "experience_quality" in exp_assessment:
                        candidate_info["experience_level"] = exp_assessment["experience_quality"]
            
        except Exception as e:
            logger.error(f"Error extracting candidate info: {e}")
        
        return candidate_info
    
    def _generate_llm_report(self, cv_analysis: Dict, interview_scores: Dict, 
                           candidate_info: Dict) -> str:
        """
        Generate LLM-based comprehensive report.
        
        Args:
            cv_analysis: CV analysis results
            interview_scores: Interview scoring results
            candidate_info: Candidate information
            
        Returns:
            LLM-generated report text
        """
        try:
            prompt = self.prompt_templates.report_generation_prompt(cv_analysis, interview_scores, candidate_info)
            report = self.llm_client.generate_response(prompt)
            return report
            
        except Exception as e:
            logger.error(f"Error generating LLM report: {e}")
            return f"Error generating LLM report: {str(e)}"
    
    def _generate_structured_report(self, cv_analysis: Dict, interview_scores: Dict, 
                                  candidate_info: Dict) -> Dict:
        """
        Generate structured report with organized data.
        
        Args:
            cv_analysis: CV analysis results
            interview_scores: Interview scoring results
            candidate_info: Candidate information
            
        Returns:
            Structured report dictionary
        """
        structured_report = {
            "executive_summary": {},
            "technical_assessment": {},
            "interview_performance": {},
            "risk_assessment": {},
            "recommendations": {},
            "next_steps": {}
        }
        
        try:
            # Executive Summary
            structured_report["executive_summary"] = self._generate_executive_summary(
                cv_analysis, interview_scores, candidate_info
            )
            
            # Technical Assessment
            structured_report["technical_assessment"] = self._generate_technical_assessment(cv_analysis)
            
            # Interview Performance
            structured_report["interview_performance"] = self._generate_interview_performance(interview_scores)
            
            # Risk Assessment
            structured_report["risk_assessment"] = self._generate_risk_assessment(cv_analysis, interview_scores)
            
            # Recommendations
            structured_report["recommendations"] = self._generate_recommendations(cv_analysis, interview_scores)
            
            # Next Steps
            structured_report["next_steps"] = self._generate_next_steps(cv_analysis, interview_scores)
            
        except Exception as e:
            logger.error(f"Error generating structured report: {e}")
        
        return structured_report
    
    def _generate_executive_summary(self, cv_analysis: Dict, interview_scores: Dict, 
                                  candidate_info: Dict) -> Dict:
        """
        Generate executive summary section.
        
        Args:
            cv_analysis: CV analysis results
            interview_scores: Interview scoring results
            candidate_info: Candidate information
            
        Returns:
            Executive summary dictionary
        """
        summary = {
            "candidate_overview": {},
            "overall_assessment": {},
            "key_findings": [],
            "final_recommendation": ""
        }
        
        try:
            # Candidate overview
            summary["candidate_overview"] = {
                "name": candidate_info.get("name", "Unknown"),
                "experience_level": candidate_info.get("experience_level", "Unknown"),
                "years_experience": candidate_info.get("years_experience", "Unknown"),
                "key_skills": candidate_info.get("key_skills", [])[:5]  # Top 5 skills
            }
            
            # Overall assessment
            cv_score = cv_analysis.get("overall_assessment", {}).get("overall_score", 0)
            interview_score = interview_scores.get("overall_assessment", {}).get("overall_score", 0)
            
            # Calculate weighted overall score (CV: 40%, Interview: 60%)
            overall_score = (cv_score * 0.4) + (interview_score * 0.6)
            
            summary["overall_assessment"] = {
                "cv_score": round(cv_score, 1),
                "interview_score": round(interview_score, 1),
                "overall_score": round(overall_score, 1),
                "performance_level": self._get_performance_level(overall_score)
            }
            
            # Key findings
            key_findings = []
            
            # CV findings
            if "overall_assessment" in cv_analysis:
                cv_overall = cv_analysis["overall_assessment"]
                if cv_overall.get("strengths"):
                    key_findings.append(f"CV Strengths: {', '.join(cv_overall['strengths'][:2])}")
                if cv_overall.get("weaknesses"):
                    key_findings.append(f"CV Areas of Concern: {', '.join(cv_overall['weaknesses'][:2])}")
            
            # Interview findings
            if "overall_assessment" in interview_scores:
                interview_overall = interview_scores["overall_assessment"]
                if interview_overall.get("top_strengths"):
                    key_findings.append(f"Interview Strengths: {', '.join(interview_overall['top_strengths'][:2])}")
                if interview_overall.get("top_weaknesses"):
                    key_findings.append(f"Interview Areas for Improvement: {', '.join(interview_overall['top_weaknesses'][:2])}")
            
            summary["key_findings"] = key_findings[:5]  # Limit to top 5 findings
            
            # Final recommendation
            summary["final_recommendation"] = self._generate_final_recommendation(cv_analysis, interview_scores)
            
        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")
        
        return summary
    
    def _generate_technical_assessment(self, cv_analysis: Dict) -> Dict:
        """
        Generate technical assessment section.
        
        Args:
            cv_analysis: CV analysis results
            
        Returns:
            Technical assessment dictionary
        """
        assessment = {
            "skill_match": {},
            "experience_evaluation": {},
            "technical_gaps": {},
            "technical_score": 0
        }
        
        try:
            # Skill match analysis
            if "skill_gaps" in cv_analysis:
                skill_gaps = cv_analysis["skill_gaps"]
                assessment["skill_match"] = {
                    "missing_skills": skill_gaps.get("missing_technical_skills", []),
                    "gap_score": skill_gaps.get("gap_score", 0),
                    "skill_match_percentage": 100 - skill_gaps.get("gap_score", 0)
                }
            
            # Experience evaluation
            if "llm_analysis" in cv_analysis and "experience_assessment" in cv_analysis["llm_analysis"]:
                exp_assessment = cv_analysis["llm_analysis"]["experience_assessment"]
                assessment["experience_evaluation"] = {
                    "years_experience": exp_assessment.get("years_experience", "Unknown"),
                    "experience_score": exp_assessment.get("experience_score", 0),
                    "experience_quality": exp_assessment.get("experience_quality", "Unknown")
                }
            
            # Technical gaps
            if "skill_gaps" in cv_analysis:
                assessment["technical_gaps"] = {
                    "missing_technical_skills": cv_analysis["skill_gaps"].get("missing_technical_skills", []),
                    "missing_tools": cv_analysis["skill_gaps"].get("missing_tools", []),
                    "gap_impact": self._assess_gap_impact(cv_analysis["skill_gaps"])
                }
            
            # Technical score
            if "overall_assessment" in cv_analysis:
                assessment["technical_score"] = cv_analysis["overall_assessment"].get("overall_score", 0)
            
        except Exception as e:
            logger.error(f"Error generating technical assessment: {e}")
        
        return assessment
    
    def _generate_interview_performance(self, interview_scores: Dict) -> Dict:
        """
        Generate interview performance section.
        
        Args:
            interview_scores: Interview scoring results
            
        Returns:
            Interview performance dictionary
        """
        performance = {
            "overall_performance": {},
            "criteria_breakdown": {},
            "response_analysis": {},
            "consistency_score": 0
        }
        
        try:
            # Overall performance
            if "overall_assessment" in interview_scores:
                overall = interview_scores["overall_assessment"]
                performance["overall_performance"] = {
                    "overall_score": overall.get("overall_score", 0),
                    "performance_level": overall.get("performance_level", "Unknown"),
                    "total_questions": overall.get("total_questions", 0),
                    "recommendation": overall.get("recommendation", "Unknown")
                }
            
            # Criteria breakdown
            if "summary_statistics" in interview_scores and "criteria_averages" in interview_scores["summary_statistics"]:
                performance["criteria_breakdown"] = interview_scores["summary_statistics"]["criteria_averages"]
            
            # Response analysis
            if "summary_statistics" in interview_scores and "response_quality" in interview_scores["summary_statistics"]:
                performance["response_analysis"] = interview_scores["summary_statistics"]["response_quality"]
            
            # Consistency score
            if "overall_assessment" in interview_scores:
                performance["consistency_score"] = interview_scores["overall_assessment"].get("consistency_score", 0)
            
        except Exception as e:
            logger.error(f"Error generating interview performance: {e}")
        
        return performance
    
    def _generate_risk_assessment(self, cv_analysis: Dict, interview_scores: Dict) -> Dict:
        """
        Generate risk assessment section.
        
        Args:
            cv_analysis: CV analysis results
            interview_scores: Interview scoring results
            
        Returns:
            Risk assessment dictionary
        """
        risk_assessment = {
            "overall_risk_level": "medium",
            "risk_factors": [],
            "mitigation_strategies": [],
            "red_flags": []
        }
        
        try:
            # Determine overall risk level
            cv_risk = cv_analysis.get("overall_assessment", {}).get("risk_level", "medium")
            interview_score = interview_scores.get("overall_assessment", {}).get("overall_score", 5)
            
            # Calculate overall risk
            if cv_risk == "high" or interview_score < 5:
                overall_risk = "high"
            elif cv_risk == "low" and interview_score >= 7:
                overall_risk = "low"
            else:
                overall_risk = "medium"
            
            risk_assessment["overall_risk_level"] = overall_risk
            
            # Identify risk factors
            risk_factors = []
            
            # CV risk factors
            if "skill_gaps" in cv_analysis:
                gap_score = cv_analysis["skill_gaps"].get("gap_score", 0)
                if gap_score > 30:
                    risk_factors.append(f"High skill gap score: {gap_score}%")
            
            # Interview risk factors
            if interview_score < 6:
                risk_factors.append(f"Low interview performance: {interview_score}/10")
            
            if "overall_assessment" in interview_scores:
                consistency = interview_scores["overall_assessment"].get("consistency_score", 100)
                if consistency < 70:
                    risk_factors.append(f"Inconsistent interview performance: {consistency}%")
            
            risk_assessment["risk_factors"] = risk_factors
            
            # Generate mitigation strategies
            mitigation_strategies = []
            if overall_risk == "high":
                mitigation_strategies.extend([
                    "Consider probationary period",
                    "Implement additional training program",
                    "Schedule follow-up assessments",
                    "Assign mentor for onboarding"
                ])
            elif overall_risk == "medium":
                mitigation_strategies.extend([
                    "Provide specific feedback",
                    "Set clear performance expectations",
                    "Monitor progress closely"
                ])
            
            risk_assessment["mitigation_strategies"] = mitigation_strategies
            
            # Identify red flags
            red_flags = []
            if interview_score < 4:
                red_flags.append("Very poor interview performance")
            if gap_score > 50:
                red_flags.append("Significant skill gaps")
            
            risk_assessment["red_flags"] = red_flags
            
        except Exception as e:
            logger.error(f"Error generating risk assessment: {e}")
        
        return risk_assessment
    
    def _generate_recommendations(self, cv_analysis: Dict, interview_scores: Dict) -> Dict:
        """
        Generate recommendations section.
        
        Args:
            cv_analysis: CV analysis results
            interview_scores: Interview scoring results
            
        Returns:
            Recommendations dictionary
        """
        recommendations = {
            "hiring_recommendation": "",
            "development_areas": [],
            "onboarding_suggestions": [],
            "team_fit_considerations": []
        }
        
        try:
            # Hiring recommendation
            recommendations["hiring_recommendation"] = self._generate_final_recommendation(cv_analysis, interview_scores)
            
            # Development areas
            development_areas = []
            
            # From CV analysis
            if "overall_assessment" in cv_analysis and "weaknesses" in cv_analysis["overall_assessment"]:
                development_areas.extend(cv_analysis["overall_assessment"]["weaknesses"])
            
            # From interview scores
            if "overall_assessment" in interview_scores and "top_weaknesses" in interview_scores["overall_assessment"]:
                development_areas.extend(interview_scores["overall_assessment"]["top_weaknesses"])
            
            recommendations["development_areas"] = list(set(development_areas))[:5]  # Remove duplicates, limit to 5
            
            # Onboarding suggestions
            onboarding_suggestions = []
            if recommendations["hiring_recommendation"] in ["hire", "strong_hire"]:
                onboarding_suggestions.extend([
                    "Standard onboarding process",
                    "Technical skills assessment",
                    "Team introduction and shadowing",
                    "Mentor assignment"
                ])
            elif recommendations["hiring_recommendation"] == "consider":
                onboarding_suggestions.extend([
                    "Extended probationary period",
                    "Focused training program",
                    "Regular performance reviews",
                    "Skills development plan"
                ])
            
            recommendations["onboarding_suggestions"] = onboarding_suggestions
            
            # Team fit considerations
            team_fit = []
            if "overall_assessment" in interview_scores:
                interview_overall = interview_scores["overall_assessment"]
                if interview_overall.get("overall_score", 0) >= 7:
                    team_fit.append("Good communication skills")
                    team_fit.append("Positive team dynamics")
                else:
                    team_fit.append("May need communication training")
                    team_fit.append("Monitor team integration")
            
            recommendations["team_fit_considerations"] = team_fit
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
        
        return recommendations
    
    def _generate_next_steps(self, cv_analysis: Dict, interview_scores: Dict) -> Dict:
        """
        Generate next steps section.
        
        Args:
            cv_analysis: CV analysis results
            interview_scores: Interview scoring results
            
        Returns:
            Next steps dictionary
        """
        next_steps = {
            "immediate_actions": [],
            "timeline": {},
            "additional_assessments": [],
            "decision_deadline": ""
        }
        
        try:
            recommendation = self._generate_final_recommendation(cv_analysis, interview_scores)
            
            # Immediate actions
            if recommendation == "strong_hire":
                next_steps["immediate_actions"] = [
                    "Extend offer immediately",
                    "Schedule onboarding meeting",
                    "Prepare employment contract"
                ]
            elif recommendation == "hire":
                next_steps["immediate_actions"] = [
                    "Extend offer",
                    "Schedule follow-up meeting",
                    "Prepare onboarding plan"
                ]
            elif recommendation == "consider":
                next_steps["immediate_actions"] = [
                    "Schedule additional interview",
                    "Request references",
                    "Consider probationary period"
                ]
            else:  # reject
                next_steps["immediate_actions"] = [
                    "Send rejection letter",
                    "Provide constructive feedback",
                    "Keep candidate in database for future opportunities"
                ]
            
            # Timeline
            if recommendation in ["strong_hire", "hire"]:
                next_steps["timeline"] = {
                    "offer_deadline": "Within 1 week",
                    "start_date": "Within 2-4 weeks",
                    "onboarding": "First 2 weeks"
                }
            elif recommendation == "consider":
                next_steps["timeline"] = {
                    "additional_assessment": "Within 1 week",
                    "decision_deadline": "Within 2 weeks",
                    "start_date": "Within 4-6 weeks"
                }
            else:
                next_steps["timeline"] = {
                    "rejection_notice": "Within 1 week",
                    "feedback_provided": "Within 2 weeks"
                }
            
            # Additional assessments
            if recommendation == "consider":
                next_steps["additional_assessments"] = [
                    "Technical coding test",
                    "Reference checks",
                    "Cultural fit interview",
                    "Skills assessment"
                ]
            
            # Decision deadline
            next_steps["decision_deadline"] = self._calculate_decision_deadline(recommendation)
            
        except Exception as e:
            logger.error(f"Error generating next steps: {e}")
        
        return next_steps
    
    def _generate_summary_report(self, cv_analysis: Dict, interview_scores: Dict, 
                               candidate_info: Dict) -> str:
        """
        Generate a concise summary report in markdown format.
        
        Args:
            cv_analysis: CV analysis results
            interview_scores: Interview scoring results
            candidate_info: Candidate information
            
        Returns:
            Markdown formatted summary
        """
        summary = f"""# Candidate Evaluation Summary

## Candidate Information
- **Name**: {candidate_info.get('name', 'Unknown')}
- **Experience Level**: {candidate_info.get('experience_level', 'Unknown')}
- **Years of Experience**: {candidate_info.get('years_experience', 'Unknown')}

## Overall Assessment
"""
        
        try:
            # Overall scores
            cv_score = cv_analysis.get("overall_assessment", {}).get("overall_score", 0)
            interview_score = interview_scores.get("overall_assessment", {}).get("overall_score", 0)
            overall_score = (cv_score * 0.4) + (interview_score * 0.6)
            
            summary += f"- **CV Score**: {cv_score:.1f}/100\n"
            summary += f"- **Interview Score**: {interview_score:.1f}/10\n"
            summary += f"- **Overall Score**: {overall_score:.1f}/100\n"
            summary += f"- **Performance Level**: {self._get_performance_level(overall_score)}\n\n"
            
            # Key findings
            summary += "## Key Findings\n"
            
            # CV findings
            if "overall_assessment" in cv_analysis:
                cv_overall = cv_analysis["overall_assessment"]
                if cv_overall.get("strengths"):
                    summary += f"- **CV Strengths**: {', '.join(cv_overall['strengths'][:3])}\n"
                if cv_overall.get("weaknesses"):
                    summary += f"- **CV Areas of Concern**: {', '.join(cv_overall['weaknesses'][:3])}\n"
            
            # Interview findings
            if "overall_assessment" in interview_scores:
                interview_overall = interview_scores["overall_assessment"]
                if interview_overall.get("top_strengths"):
                    summary += f"- **Interview Strengths**: {', '.join(interview_overall['top_strengths'][:3])}\n"
                if interview_overall.get("top_weaknesses"):
                    summary += f"- **Interview Areas for Improvement**: {', '.join(interview_overall['top_weaknesses'][:3])}\n"
            
            summary += "\n"
            
            # Final recommendation
            final_rec = self._generate_final_recommendation(cv_analysis, interview_scores)
            summary += f"## Final Recommendation\n**{final_rec.replace('_', ' ').title()}**\n\n"
            
            # Next steps
            summary += "## Next Steps\n"
            if final_rec in ["strong_hire", "hire"]:
                summary += "- Extend offer\n- Schedule onboarding\n- Prepare employment contract\n"
            elif final_rec == "consider":
                summary += "- Schedule additional assessment\n- Request references\n- Consider probationary period\n"
            else:
                summary += "- Send rejection notice\n- Provide constructive feedback\n- Keep in database for future opportunities\n"
            
        except Exception as e:
            logger.error(f"Error generating summary report: {e}")
            summary += f"Error generating summary: {str(e)}\n"
        
        return summary
    
    def _generate_final_recommendation(self, cv_analysis: Dict, interview_scores: Dict) -> str:
        """
        Generate final hiring recommendation based on CV and interview results.
        
        Args:
            cv_analysis: CV analysis results
            interview_scores: Interview scoring results
            
        Returns:
            Final recommendation
        """
        try:
            cv_score = cv_analysis.get("overall_assessment", {}).get("overall_score", 0)
            interview_score = interview_scores.get("overall_assessment", {}).get("overall_score", 0)
            
            # Calculate weighted score
            overall_score = (cv_score * 0.4) + (interview_score * 10 * 0.6)  # Convert interview to 0-100 scale
            
            # Determine recommendation
            if overall_score >= 85:
                return "strong_hire"
            elif overall_score >= 70:
                return "hire"
            elif overall_score >= 50:
                return "consider"
            else:
                return "reject"
                
        except Exception as e:
            logger.error(f"Error generating final recommendation: {e}")
            return "consider"
    
    def _get_performance_level(self, score: float) -> str:
        """Get performance level based on score."""
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 50:
            return "Fair"
        else:
            return "Poor"
    
    def _assess_gap_impact(self, skill_gaps: Dict) -> str:
        """Assess the impact of skill gaps."""
        gap_score = skill_gaps.get("gap_score", 0)
        if gap_score > 50:
            return "High"
        elif gap_score > 25:
            return "Medium"
        else:
            return "Low"
    
    def _calculate_decision_deadline(self, recommendation: str) -> str:
        """Calculate decision deadline based on recommendation."""
        if recommendation in ["strong_hire", "hire"]:
            return "Within 1 week"
        elif recommendation == "consider":
            return "Within 2 weeks"
        else:
            return "Within 1 week"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for metadata."""
        return datetime.now().isoformat()
    
    def save_report(self, report: Dict, output_path: str, format: str = "json"):
        """
        Save report to file in specified format.
        
        Args:
            report: Report data
            output_path: Output file path
            format: Output format ("json", "markdown", "html")
        """
        try:
            if format == "json":
                self.file_utils.save_json(report, output_path)
            elif format == "markdown":
                summary = report.get("summary_report", "No summary available")
                self.file_utils.save_markdown(summary, output_path)
            else:
                logger.warning(f"Unsupported format: {format}, saving as JSON")
                self.file_utils.save_json(report, output_path)
            
            logger.info(f"Report saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving report: {e}")
    
    def generate_batch_reports(self, evaluations: List[Dict]) -> Dict:
        """
        Generate reports for multiple candidates.
        
        Args:
            evaluations: List of evaluation dictionaries
            
        Returns:
            Dictionary with reports for each candidate
        """
        batch_reports = {}
        
        for evaluation in evaluations:
            try:
                candidate_name = evaluation.get("candidate_name", "Unknown")
                cv_analysis = evaluation.get("cv_analysis", {})
                interview_scores = evaluation.get("interview_scores", {})
                
                report = self.generate_comprehensive_report(cv_analysis, interview_scores)
                batch_reports[candidate_name] = report
                
            except Exception as e:
                logger.error(f"Error generating report for candidate {candidate_name}: {e}")
                batch_reports[candidate_name] = {"error": str(e)}
        
        return batch_reports
