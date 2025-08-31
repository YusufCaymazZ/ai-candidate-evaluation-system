"""
Prompt Templates for Candidate Evaluation System

This module contains carefully crafted prompts for different evaluation tasks
including CV analysis, interview scoring, and report generation.
"""

from typing import Dict, List, Optional


class PromptTemplates:
    """
    Collection of prompt templates for the candidate evaluation system.
    
    Each template is designed to work with instruction-tuned models like Mistral
    and provides structured output formats for consistent evaluation results.
    """
    
    @staticmethod
    def cv_analysis_prompt(cv_text: str, job_description: str) -> str:
        """
        Generate a prompt for CV analysis against job description.
        
        Args:
            cv_text: Text content of the CV
            job_description: Job description text
            
        Returns:
            Formatted prompt for CV analysis
        """
        # Truncate inputs to avoid token limits
        cv_short = cv_text[:500] + "..." if len(cv_text) > 500 else cv_text
        job_short = job_description[:500] + "..." if len(job_description) > 500 else job_description
        
        return f"""Analyze CV vs Job Description. Return ONLY valid JSON:

CV: {cv_short}
Job: {job_short}

{{
    "overall_score": 75,
    "skill_match": {{
        "required_skills": ["python", "javascript"],
        "missing_skills": ["docker"],
        "skill_match_percentage": 80
    }},
    "experience_assessment": {{
        "years_experience": "3-5 years",
        "experience_score": 85
    }},
    "recommendations": ["Consider additional training", "Schedule technical interview"],
    "confidence": 80
}}"""

    @staticmethod
    def interview_scoring_prompt(question: str, response: str, criteria: List[str]) -> str:
        """
        Generate a prompt for scoring interview responses.
        
        Args:
            question: Interview question asked
            response: Candidate's response
            criteria: List of evaluation criteria
            
        Returns:
            Formatted prompt for interview scoring
        """
        criteria_str = ", ".join(criteria)
        
        return f"""You are an expert interviewer evaluating a candidate's response to an interview question.
Please assess the following response based on the specified criteria.

INTERVIEW QUESTION:
{question}

CANDIDATE RESPONSE:
{response}

EVALUATION CRITERIA:
{criteria_str}

Please provide your scoring in the following JSON format:
{{
    "overall_score": <score from 1-10>,
    "criteria_scores": {{
        "technical_knowledge": <score from 1-10>,
        "communication": <score from 1-10>,
        "problem_solving": <score from 1-10>,
        "cultural_fit": <score from 1-10>,
        "confidence": <score from 1-10>
    }},
    "response_analysis": {{
        "clarity": "<excellent/good/fair/poor>",
        "completeness": "<excellent/good/fair/poor>",
        "relevance": "<excellent/good/fair/poor>",
        "depth": "<excellent/good/fair/poor>"
    }},
    "strengths": [
        "strength1",
        "strength2",
        "strength3"
    ],
    "weaknesses": [
        "weakness1", 
        "weakness2"
    ],
    "specific_feedback": "Detailed feedback about the response quality, technical accuracy, and communication effectiveness.",
    "improvement_suggestions": [
        "suggestion1",
        "suggestion2"
    ],
    "recommendation": "<strong_hire/hire/consider/reject>",
    "confidence": <confidence from 0-100>
}}

Evaluation Guidelines:
1. Technical Knowledge: Assess accuracy and depth of technical understanding
2. Communication: Evaluate clarity, structure, and articulation
3. Problem Solving: Assess analytical thinking and solution approach
4. Cultural Fit: Evaluate alignment with company values and team dynamics
5. Confidence: Assess self-assurance and professional presence

Be fair and objective in your assessment."""

    @staticmethod
    def question_generation_prompt(job_description: str, cv_analysis: Dict) -> str:
        """
        Generate a prompt for creating personalized interview questions.
        
        Args:
            job_description: Job description text
            cv_analysis: Results from CV analysis
            
        Returns:
            Formatted prompt for question generation
        """
        return f"""You are an expert interviewer creating personalized interview questions for a candidate.
Based on the job description and CV analysis, generate relevant interview questions.

JOB DESCRIPTION:
{job_description}

CV ANALYSIS:
{cv_analysis}

Please generate interview questions in the following JSON format:
{{
    "technical_questions": [
        {{
            "question": "Technical question 1",
            "purpose": "Assess specific technical skill",
            "expected_keywords": ["keyword1", "keyword2"],
            "difficulty": "<junior/mid-level/senior>"
        }},
        {{
            "question": "Technical question 2", 
            "purpose": "Evaluate problem-solving approach",
            "expected_keywords": ["keyword3", "keyword4"],
            "difficulty": "<junior/mid-level/senior>"
        }}
    ],
    "behavioral_questions": [
        {{
            "question": "Behavioral question 1",
            "purpose": "Assess teamwork and collaboration",
            "expected_keywords": ["keyword5", "keyword6"],
            "scenario": "Describe a specific situation"
        }},
        {{
            "question": "Behavioral question 2",
            "purpose": "Evaluate leadership and initiative", 
            "expected_keywords": ["keyword7", "keyword8"],
            "scenario": "Describe a challenging project"
        }}
    ],
    "situational_questions": [
        {{
            "question": "Situational question 1",
            "purpose": "Assess decision-making under pressure",
            "scenario": "Describe a specific work situation",
            "expected_approach": "Expected problem-solving approach"
        }}
    ],
    "question_rationale": "Explanation of why these questions were chosen based on the candidate's profile and job requirements"
}}

Focus on:
1. Addressing skill gaps identified in CV analysis
2. Exploring relevant experience mentioned
3. Assessing cultural fit and soft skills
4. Evaluating problem-solving abilities
5. Testing technical knowledge appropriate to the role

Generate 2-3 questions per category that are specific to this candidate's background and the job requirements."""

    @staticmethod
    def report_generation_prompt(cv_analysis: Dict, interview_scores: Dict, candidate_info: Dict) -> str:
        """
        Generate a prompt for creating comprehensive evaluation reports.
        
        Args:
            cv_analysis: Results from CV analysis
            interview_scores: Results from interview scoring
            candidate_info: Basic candidate information
            
        Returns:
            Formatted prompt for report generation
        """
        return f"""You are an expert HR professional creating a comprehensive candidate evaluation report.
Please generate a professional report based on the CV analysis and interview scores.

CANDIDATE INFORMATION:
{candidate_info}

CV ANALYSIS RESULTS:
{cv_analysis}

INTERVIEW SCORING RESULTS:
{interview_scores}

Please create a comprehensive evaluation report in Markdown format with the following structure:

# Candidate Evaluation Report

## Executive Summary
- Overall assessment and recommendation
- Key strengths and areas of concern
- Final hiring recommendation

## Technical Assessment
- Skill match analysis
- Technical competency evaluation
- Experience level assessment
- Technical gaps and recommendations

## Interview Performance
- Overall interview score
- Breakdown by evaluation criteria
- Key strengths demonstrated
- Areas for improvement
- Communication and soft skills assessment

## Detailed Analysis

### CV Analysis
- Skill match percentage and details
- Experience relevance and quality
- Education assessment
- Technical skills evaluation

### Interview Performance
- Question-by-question analysis
- Response quality assessment
- Problem-solving approach evaluation
- Cultural fit assessment

## Recommendations
- Specific recommendations for hiring decision
- Development areas if hired
- Onboarding suggestions
- Team fit considerations

## Next Steps
- Recommended next steps in the hiring process
- Additional assessments if needed
- Timeline for decision

## Risk Assessment
- Potential risks or concerns
- Mitigation strategies
- Red flags to monitor

Format the report professionally with clear sections, bullet points, and actionable insights. 
Be objective and provide evidence-based recommendations."""

    @staticmethod
    def skill_extraction_prompt(cv_text: str) -> str:
        """
        Generate a prompt for extracting skills from CV text.
        
        Args:
            cv_text: Text content of the CV
            
        Returns:
            Formatted prompt for skill extraction
        """

        # Truncate input to avoid token limits
        cv_short = cv_text[:500] + "..." if len(cv_text) > 500 else cv_text
        
        return f"""Extract skills from CV. Return ONLY valid JSON:

CV: {cv_short}

{{
    "technical_skills": {{
        "programming_languages": ["python", "javascript"],
        "frameworks": ["django", "react"],
        "tools": ["git", "docker"]
    }},
    "soft_skills": ["communication", "teamwork"],
    "experience_level": "senior",
    "years_experience": "5-7 years"
}}"""

    @staticmethod
    def job_requirement_extraction_prompt(job_description: str) -> str:
        """
        Generate a prompt for extracting requirements from job descriptions.
        
        Args:
            job_description: Job description text
            
        Returns:
            Formatted prompt for requirement extraction
        """
        # Truncate input to avoid token limits
        job_short = job_description[:500] + "..." if len(job_description) > 500 else job_description
        
        return f"""Extract job requirements. Return ONLY valid JSON:

Job: {job_short}

{{
    "required_skills": {{
        "technical_skills": ["python", "javascript"],
        "soft_skills": ["communication", "teamwork"],
        "tools": ["git"]
    }},
    "experience_requirements": {{
        "years_experience": "1-3 years",
        "experience_level": "junior"
    }},
    "education_requirements": {{
        "degree_level": "bachelor"
    }}
}}"""
