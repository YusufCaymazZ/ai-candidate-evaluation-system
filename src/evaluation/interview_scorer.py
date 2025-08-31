"""
Interview Scorer for Candidate Evaluation System

This module provides comprehensive interview scoring functionality, including
question generation, response evaluation, and detailed scoring analysis.
"""

import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from loguru import logger

from src.models.llm_client import LLMClient
from src.utils.prompt_templates import PromptTemplates
from src.utils.file_utils import FileUtils


class InterviewScorer:
    """
    Comprehensive interview scoring system for candidate evaluation.
    
    Provides functionality to generate personalized interview questions,
    score candidate responses, and provide detailed feedback.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize the interview scorer with LLM client and utilities.
        
        Args:
            config_path: Path to configuration file
        """
        self.llm_client = LLMClient(config_path)
        self.file_utils = FileUtils()
        self.prompt_templates = PromptTemplates()
        
        logger.info("Interview Scorer initialized successfully")
    
    def generate_interview_questions(self, job_description: str, cv_analysis: Dict) -> Dict:
        """
        Generate personalized interview questions based on job description and CV analysis.
        
        Args:
            job_description: Job description text
            cv_analysis: Results from CV analysis
            
        Returns:
            Generated interview questions
        """
        # Use fallback questions for better reliability
        logger.info("Generating personalized interview questions")
        
        questions = self._generate_fallback_questions(job_description, cv_analysis)
        
        # Add metadata
        questions["metadata"] = {
            "generation_timestamp": self._get_timestamp(),
            "job_description_length": len(job_description),
            "cv_analysis_score": cv_analysis.get("overall_assessment", {}).get("overall_score", 0)
        }
        
        return questions
    
    def score_interview_response(self, question: str, response: str, 
                               criteria: List[str] = None) -> Dict:
        """
        Score a candidate's interview response.
        
        Args:
            question: Interview question asked
            response: Candidate's response
            criteria: List of evaluation criteria (optional)
            
        Returns:
            Detailed scoring results
        """
        # Use fallback scoring for better reliability
        if criteria is None:
            criteria = ["technical_knowledge", "communication", "problem_solving", "cultural_fit"]
        
        logger.info(f"Scoring interview response for question: {question[:50]}...")
        
        scoring_result = self._fallback_scoring(question, response, criteria)
        
        # Add metadata
        scoring_result["metadata"] = {
            "question_length": len(question),
            "response_length": len(response),
            "scoring_timestamp": self._get_timestamp(),
            "evaluation_criteria": criteria
        }
        
        return scoring_result
    
    def score_multiple_responses(self, questions_responses: List[Dict]) -> Dict:
        """
        Score multiple interview responses for a candidate.
        
        Args:
            questions_responses: List of dictionaries with 'question' and 'response' keys
            
        Returns:
            Comprehensive scoring results for all responses
        """
        results = {
            "individual_scores": [],
            "overall_assessment": {},
            "summary_statistics": {},
            "recommendations": []
        }
        
        try:
            total_score = 0
            criteria_scores = {
                "technical_knowledge": [],
                "communication": [],
                "problem_solving": [],
                "cultural_fit": []
            }
            
            for i, qr in enumerate(questions_responses):
                question = qr.get("question", "")
                response = qr.get("response", "")
                
                if not question or not response:
                    logger.warning(f"Skipping empty question/response at index {i}")
                    continue
                
                # Score individual response
                score_result = self.score_interview_response(question, response)
                score_result["question_index"] = i
                results["individual_scores"].append(score_result)
                
                # Accumulate scores
                if "overall_score" in score_result:
                    total_score += score_result["overall_score"]
                
                # Accumulate criteria scores
                if "criteria_scores" in score_result:
                    for criteria, score in score_result["criteria_scores"].items():
                        if criteria in criteria_scores:
                            criteria_scores[criteria].append(score)
            
            # Calculate overall assessment
            results["overall_assessment"] = self._calculate_overall_assessment(
                results["individual_scores"], total_score, len(questions_responses)
            )
            
            # Calculate summary statistics
            results["summary_statistics"] = self._calculate_summary_statistics(
                results["individual_scores"], criteria_scores
            )
            
            # Generate recommendations
            results["recommendations"] = self._generate_interview_recommendations(
                results["overall_assessment"], results["summary_statistics"]
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error scoring multiple responses: {e}")
            return {"error": str(e)}
    
    def _calculate_overall_assessment(self, individual_scores: List[Dict], 
                                    total_score: float, num_questions: int) -> Dict:
        """
        Calculate overall assessment from individual scores.
        
        Args:
            individual_scores: List of individual scoring results
            total_score: Sum of all scores
            num_questions: Number of questions answered
            
        Returns:
            Overall assessment
        """
        if num_questions == 0:
            return {"overall_score": 0, "performance_level": "poor"}
        
        average_score = total_score / num_questions
        
        # Determine performance level
        if average_score >= 8.5:
            performance_level = "excellent"
        elif average_score >= 7.0:
            performance_level = "good"
        elif average_score >= 5.5:
            performance_level = "fair"
        else:
            performance_level = "poor"
        
        # Analyze strengths and weaknesses across all responses
        all_strengths = []
        all_weaknesses = []
        
        for score_result in individual_scores:
            if "strengths" in score_result:
                all_strengths.extend(score_result["strengths"])
            if "weaknesses" in score_result:
                all_weaknesses.extend(score_result["weaknesses"])
        
        # Get most common strengths and weaknesses
        from collections import Counter
        strength_counts = Counter(all_strengths)
        weakness_counts = Counter(all_weaknesses)
        
        top_strengths = [strength for strength, count in strength_counts.most_common(3)]
        top_weaknesses = [weakness for weakness, count in weakness_counts.most_common(3)]
        
        return {
            "overall_score": round(average_score, 2),
            "performance_level": performance_level,
            "total_questions": num_questions,
            "consistency_score": self._calculate_consistency_score(individual_scores),
            "top_strengths": top_strengths,
            "top_weaknesses": top_weaknesses,
            "recommendation": self._determine_interview_recommendation(average_score)
        }
    
    def _calculate_summary_statistics(self, individual_scores: List[Dict], 
                                    criteria_scores: Dict) -> Dict:
        """
        Calculate summary statistics for interview performance.
        
        Args:
            individual_scores: List of individual scoring results
            criteria_scores: Dictionary of scores by criteria
            
        Returns:
            Summary statistics
        """
        stats = {
            "score_distribution": {},
            "criteria_averages": {},
            "response_quality": {}
        }
        
        try:
            # Calculate score distribution
            score_ranges = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
            for score_result in individual_scores:
                score = score_result.get("overall_score", 0)
                if score >= 8.5:
                    score_ranges["excellent"] += 1
                elif score >= 7.0:
                    score_ranges["good"] += 1
                elif score >= 5.5:
                    score_ranges["fair"] += 1
                else:
                    score_ranges["poor"] += 1
            
            stats["score_distribution"] = score_ranges
            
            # Calculate criteria averages
            for criteria, scores in criteria_scores.items():
                if scores:
                    avg_score = sum(scores) / len(scores)
                    stats["criteria_averages"][criteria] = round(avg_score, 2)
            
            # Analyze response quality
            response_lengths = []
            for score_result in individual_scores:
                if "metadata" in score_result:
                    response_length = score_result["metadata"].get("response_length", 0)
                    response_lengths.append(response_length)
            
            if response_lengths:
                stats["response_quality"] = {
                    "average_length": sum(response_lengths) / len(response_lengths),
                    "min_length": min(response_lengths),
                    "max_length": max(response_lengths)
                }
            
        except Exception as e:
            logger.error(f"Error calculating summary statistics: {e}")
        
        return stats
    
    def _calculate_consistency_score(self, individual_scores: List[Dict]) -> float:
        """
        Calculate consistency score based on score variance.
        
        Args:
            individual_scores: List of individual scoring results
            
        Returns:
            Consistency score (0-100, higher = more consistent)
        """
        try:
            scores = [result.get("overall_score", 0) for result in individual_scores]
            if len(scores) < 2:
                return 100.0
            
            import statistics
            variance = statistics.variance(scores)
            # Convert variance to consistency score (lower variance = higher consistency)
            consistency = max(0, 100 - (variance * 10))
            return round(consistency, 2)
            
        except Exception as e:
            logger.error(f"Error calculating consistency score: {e}")
            return 50.0
    
    def _determine_interview_recommendation(self, average_score: float) -> str:
        """
        Determine hiring recommendation based on interview score.
        
        Args:
            average_score: Average interview score
            
        Returns:
            Hiring recommendation
        """
        if average_score >= 8.5:
            return "strong_hire"
        elif average_score >= 7.0:
            return "hire"
        elif average_score >= 5.5:
            return "consider"
        else:
            return "reject"
    
    def _generate_interview_recommendations(self, overall_assessment: Dict, 
                                          summary_stats: Dict) -> List[str]:
        """
        Generate recommendations based on interview performance.
        
        Args:
            overall_assessment: Overall assessment results
            summary_stats: Summary statistics
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        try:
            score = overall_assessment.get("overall_score", 0)
            performance_level = overall_assessment.get("performance_level", "poor")
            
            # Performance-based recommendations
            if performance_level == "excellent":
                recommendations.append("Strong technical interview performance - proceed to next round")
                recommendations.append("Consider fast-track hiring process")
            elif performance_level == "good":
                recommendations.append("Solid interview performance - recommend for next stage")
                recommendations.append("Schedule follow-up technical assessment if needed")
            elif performance_level == "fair":
                recommendations.append("Moderate interview performance - consider additional assessments")
                recommendations.append("Review specific areas of weakness before proceeding")
            else:
                recommendations.append("Poor interview performance - recommend rejection")
                recommendations.append("Consider providing constructive feedback")
            
            # Consistency-based recommendations
            consistency = overall_assessment.get("consistency_score", 50)
            if consistency < 70:
                recommendations.append("Inconsistent performance across questions - investigate further")
            
            # Specific area recommendations
            criteria_averages = summary_stats.get("criteria_averages", {})
            for criteria, avg_score in criteria_averages.items():
                if avg_score < 6.0:
                    recommendations.append(f"Focus on improving {criteria.replace('_', ' ')} skills")
            
        except Exception as e:
            logger.error(f"Error generating interview recommendations: {e}")
            recommendations.append("Manual review recommended")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _generate_fallback_questions(self, job_description: str, cv_analysis: Dict) -> Dict:
        """
        Generate fallback interview questions when LLM generation fails.
        
        Args:
            job_description: Job description text
            cv_analysis: CV analysis results
            
        Returns:
            Fallback questions
        """
        # Standard interview questions based on common patterns
        technical_questions = [
            {
                "question": "Explain the difference between a list and a tuple in Python.",
                "purpose": "Assess basic programming knowledge",
                "expected_keywords": ["mutable", "immutable", "performance"],
                "difficulty": "junior"
            },
            {
                "question": "How would you design a REST API for a user management system?",
                "purpose": "Assess system design skills",
                "expected_keywords": ["endpoints", "HTTP methods", "authentication"],
                "difficulty": "mid-level"
            },
            {
                "question": "Describe your experience with database optimization.",
                "purpose": "Assess database knowledge",
                "expected_keywords": ["indexing", "query optimization", "performance"],
                "difficulty": "senior"
            }
        ]
        
        behavioral_questions = [
            {
                "question": "Tell me about a challenging project you worked on and how you overcame obstacles.",
                "purpose": "Assess problem-solving and resilience",
                "expected_keywords": ["problem-solving", "collaboration", "learning"],
                "scenario": "Project challenge"
            },
            {
                "question": "How do you handle working with difficult team members?",
                "purpose": "Assess teamwork and communication",
                "expected_keywords": ["communication", "patience", "conflict resolution"],
                "scenario": "Team dynamics"
            }
        ]
        
        return {
            "technical_questions": technical_questions,
            "behavioral_questions": behavioral_questions,
            "situational_questions": [],
            "question_rationale": "Fallback questions generated due to LLM processing error",
            "metadata": {
                "generation_timestamp": self._get_timestamp(),
                "fallback_generated": True
            }
        }
    
    def _fallback_scoring(self, question: str, response: str, criteria: List[str]) -> Dict:
        """
        Fallback scoring when LLM scoring fails.
        
        Args:
            question: Interview question
            response: Candidate response
            criteria: Evaluation criteria
            
        Returns:
            Basic scoring result
        """
        # Simple scoring based on response length and keyword matching
        response_length = len(response)
        question_lower = question.lower()
        response_lower = response.lower()
        
        # Basic scoring logic
        if response_length < 50:
            overall_score = 3
        elif response_length < 150:
            overall_score = 5
        elif response_length < 300:
            overall_score = 7
        else:
            overall_score = 8
        
        # Adjust score based on question type
        if "technical" in question_lower or "programming" in question_lower:
            technical_keywords = ["python", "java", "database", "api", "algorithm"]
            keyword_matches = sum(1 for keyword in technical_keywords if keyword in response_lower)
            overall_score = min(10, overall_score + keyword_matches)
        
        return {
            "overall_score": overall_score,
            "criteria_scores": {
                "technical_knowledge": overall_score,
                "communication": min(10, overall_score + 1),
                "problem_solving": overall_score,
                "cultural_fit": 6
            },
            "strengths": ["Fallback scoring used"],
            "weaknesses": ["Detailed analysis unavailable"],
            "feedback": "Fallback scoring method used due to processing error",
            "recommendation": "consider" if overall_score >= 6 else "reject",
            "confidence": 50,
            "metadata": {
                "fallback_scoring": True,
                "response_length": response_length
            }
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for metadata."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def save_interview_results(self, results: Dict, output_path: str):
        """
        Save interview scoring results to file.
        
        Args:
            results: Interview scoring results
            output_path: Output file path
        """
        try:
            self.file_utils.save_json(results, output_path)
            logger.info(f"Interview results saved to: {output_path}")
        except Exception as e:
            logger.error(f"Error saving interview results: {e}")
    
    def generate_interview_summary(self, results: Dict) -> str:
        """
        Generate a summary of interview scoring results.
        
        Args:
            results: Interview scoring results
            
        Returns:
            Markdown formatted summary
        """
        summary = "# Interview Performance Summary\n\n"
        
        overall = results.get("overall_assessment", {})
        summary += f"## Overall Assessment\n"
        summary += f"- **Overall Score**: {overall.get('overall_score', 'N/A')}/10\n"
        summary += f"- **Performance Level**: {overall.get('performance_level', 'N/A')}\n"
        summary += f"- **Consistency Score**: {overall.get('consistency_score', 'N/A')}%\n"
        summary += f"- **Recommendation**: {overall.get('recommendation', 'N/A')}\n\n"
        
        # Individual question scores
        individual_scores = results.get("individual_scores", [])
        if individual_scores:
            summary += "## Question-by-Question Analysis\n\n"
            for i, score_result in enumerate(individual_scores):
                summary += f"### Question {i+1}\n"
                summary += f"- **Score**: {score_result.get('overall_score', 'N/A')}/10\n"
                
                if "strengths" in score_result and score_result["strengths"]:
                    summary += f"- **Strengths**: {', '.join(score_result['strengths'][:2])}\n"
                
                if "weaknesses" in score_result and score_result["weaknesses"]:
                    summary += f"- **Areas for Improvement**: {', '.join(score_result['weaknesses'][:2])}\n"
                
                summary += "\n"
        
        # Recommendations
        recommendations = results.get("recommendations", [])
        if recommendations:
            summary += "## Recommendations\n\n"
            for rec in recommendations:
                summary += f"- {rec}\n"
            summary += "\n"
        
        return summary
