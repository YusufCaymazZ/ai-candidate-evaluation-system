"""
Unit tests for CV Analyzer module.

This module contains comprehensive tests for the CV analysis functionality
including skill extraction, gap analysis, and scoring.
"""

import pytest
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.evaluation.cv_analyzer import CVAnalyzer
from src.utils.file_utils import FileUtils


class TestCVAnalyzer:
    """Test cases for CV Analyzer functionality."""
    
    @pytest.fixture
    def cv_analyzer(self):
        """Create a CV analyzer instance for testing."""
        return CVAnalyzer()
    
    @pytest.fixture
    def file_utils(self):
        """Create a file utils instance for testing."""
        return FileUtils()
    
    @pytest.fixture
    def sample_cv_text(self):
        """Sample CV text for testing."""
        return """
        JOHN DOE
        Senior Software Developer
        john.doe@email.com | +1-555-0123
        
        TECHNICAL SKILLS
        Programming Languages: Python, JavaScript, Java
        Frameworks: Django, React, Spring Boot
        Databases: PostgreSQL, MongoDB
        Tools: Git, Docker, Kubernetes
        
        WORK EXPERIENCE
        Senior Developer | TechCorp Inc. | 2020-Present
        - Led development of microservices architecture
        - Mentored junior developers
        - Implemented CI/CD pipelines
        
        EDUCATION
        Bachelor of Science in Computer Science | University of Technology | 2018
        """
    
    @pytest.fixture
    def sample_job_description(self):
        """Sample job description for testing."""
        return """
        SENIOR PYTHON DEVELOPER
        
        REQUIREMENTS:
        - 5+ years of experience in Python development
        - Strong knowledge of Django, Flask, or similar frameworks
        - Experience with cloud platforms (AWS, Azure, or GCP)
        - Proficiency in SQL and database design
        - Experience with microservices architecture
        - Knowledge of Docker and Kubernetes
        
        RESPONSIBILITIES:
        - Design and implement scalable software solutions
        - Lead technical discussions and code reviews
        - Mentor junior developers
        - Collaborate with cross-functional teams
        """
    
    def test_cv_analyzer_initialization(self, cv_analyzer):
        """Test CV analyzer initialization."""
        assert cv_analyzer is not None
        assert hasattr(cv_analyzer, 'llm_client')
        assert hasattr(cv_analyzer, 'file_utils')
        assert hasattr(cv_analyzer, 'prompt_templates')
    
    def test_fallback_skill_extraction(self, cv_analyzer, sample_cv_text):
        """Test fallback skill extraction functionality."""
        skills = cv_analyzer._fallback_skill_extraction(sample_cv_text)
        
        assert isinstance(skills, dict)
        assert "technical_skills" in skills
        assert "soft_skills" in skills
        assert "experience_level" in skills
        
        # Check if Python was extracted
        python_found = False
        if "programming_languages" in skills["technical_skills"]:
            python_found = "Python" in skills["technical_skills"]["programming_languages"]
        
        assert python_found, "Python should be extracted from the sample CV"
    
    def test_fallback_requirement_extraction(self, cv_analyzer, sample_job_description):
        """Test fallback requirement extraction functionality."""
        requirements = cv_analyzer._fallback_requirement_extraction(sample_job_description)
        
        assert isinstance(requirements, dict)
        assert "required_skills" in requirements
        assert "experience_requirements" in requirements
        assert "education_requirements" in requirements
    
    def test_calculate_skill_gaps(self, cv_analyzer):
        """Test skill gap calculation."""
        cv_skills = {
            "technical_skills": {
                "programming_languages": ["Python", "JavaScript"],
                "frameworks": ["Django", "React"]
            }
        }
        
        job_requirements = {
            "required_skills": {
                "technical_skills": ["Python", "Java", "Docker"],
                "tools": ["Git", "Kubernetes"]
            }
        }
        
        gaps = cv_analyzer._calculate_skill_gaps(cv_skills, job_requirements)
        
        assert isinstance(gaps, dict)
        assert "missing_technical_skills" in gaps
        assert "gap_score" in gaps
        
        # Should identify Java and Docker as missing
        missing_skills = gaps["missing_technical_skills"]
        assert "java" in [skill.lower() for skill in missing_skills]
        assert "docker" in [skill.lower() for skill in missing_skills]
    
    def test_determine_risk_level(self, cv_analyzer):
        """Test risk level determination."""
        assert cv_analyzer._determine_risk_level(85) == "low"
        assert cv_analyzer._determine_risk_level(70) == "medium"
        assert cv_analyzer._determine_risk_level(50) == "high"
    
    def test_determine_hiring_recommendation(self, cv_analyzer):
        """Test hiring recommendation determination."""
        # Test with low gap score
        skill_gaps = {"gap_score": 15}
        assert cv_analyzer._determine_hiring_recommendation(85, skill_gaps) == "strong_hire"
        assert cv_analyzer._determine_hiring_recommendation(75, skill_gaps) == "hire"
        assert cv_analyzer._determine_hiring_recommendation(60, skill_gaps) == "consider"
        assert cv_analyzer._determine_hiring_recommendation(40, skill_gaps) == "reject"
    
    def test_generate_recommendations(self, cv_analyzer):
        """Test recommendation generation."""
        cv_skills = {
            "technical_skills": {
                "programming_languages": ["Python"]
            }
        }
        
        job_requirements = {
            "required_skills": {
                "technical_skills": ["Python", "Java"]
            }
        }
        
        skill_gaps = {
            "missing_technical_skills": ["Java"],
            "gap_score": 30
        }
        
        llm_analysis = {
            "recommendations": ["Consider additional training"],
            "experience_assessment": {"experience_score": 60}
        }
        
        recommendations = cv_analyzer._generate_recommendations(
            cv_skills, job_requirements, skill_gaps, llm_analysis
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Should include recommendation about missing skills
        java_recommendation = any("Java" in rec for rec in recommendations)
        assert java_recommendation, "Should recommend training in missing skills"
    
    def test_generate_overall_assessment(self, cv_analyzer):
        """Test overall assessment generation."""
        cv_skills = {"technical_skills": {"programming_languages": ["Python"]}}
        job_requirements = {"required_skills": {"technical_skills": ["Python"]}}
        skill_gaps = {"gap_score": 20}
        llm_analysis = {
            "overall_score": 80,
            "experience_assessment": {"experience_score": 75},
            "strengths": ["Good technical skills"],
            "weaknesses": ["Limited experience"]
        }
        
        assessment = cv_analyzer._generate_overall_assessment(
            cv_skills, job_requirements, skill_gaps, llm_analysis
        )
        
        assert isinstance(assessment, dict)
        assert "overall_score" in assessment
        assert "strengths" in assessment
        assert "weaknesses" in assessment
        assert "recommendations" in assessment
        assert "risk_level" in assessment
        assert "hiring_recommendation" in assessment
        
        assert assessment["overall_score"] > 0
        assert assessment["risk_level"] in ["low", "medium", "high"]
        assert assessment["hiring_recommendation"] in ["strong_hire", "hire", "consider", "reject"]
    
    def test_get_timestamp(self, cv_analyzer):
        """Test timestamp generation."""
        timestamp = cv_analyzer._get_timestamp()
        assert isinstance(timestamp, str)
        assert len(timestamp) > 0
    
    def test_batch_analyze_cvs(self, cv_analyzer, file_utils, tmp_path):
        """Test batch CV analysis functionality."""
        # Create temporary CV files
        cv1_content = "Python Developer with 5 years experience"
        cv2_content = "Java Developer with 3 years experience"
        
        cv1_file = tmp_path / "cv1.txt"
        cv2_file = tmp_path / "cv2.txt"
        jd_file = tmp_path / "job_description.txt"
        
        cv1_file.write_text(cv1_content)
        cv2_file.write_text(cv2_content)
        jd_file.write_text("Python Developer position")
        
        cv_files = [str(cv1_file), str(cv2_file)]
        
        # Test batch analysis
        results = cv_analyzer.batch_analyze_cvs(cv_files, str(jd_file))
        
        assert isinstance(results, dict)
        assert len(results) == 2
        assert "cv1" in results
        assert "cv2" in results
    
    def test_save_analysis_results(self, cv_analyzer, tmp_path):
        """Test saving analysis results."""
        test_results = {
            "overall_assessment": {
                "overall_score": 75,
                "hiring_recommendation": "hire"
            },
            "skill_gaps": {
                "gap_score": 25
            }
        }
        
        output_file = tmp_path / "test_analysis.json"
        cv_analyzer.save_analysis_results(test_results, str(output_file))
        
        assert output_file.exists()
        
        # Verify content can be loaded
        import json
        with open(output_file, 'r') as f:
            loaded_results = json.load(f)
        
        assert loaded_results["overall_assessment"]["overall_score"] == 75
    
    def test_generate_analysis_summary(self, cv_analyzer):
        """Test analysis summary generation."""
        test_results = {
            "candidate1": {
                "overall_assessment": {
                    "overall_score": 80,
                    "hiring_recommendation": "hire",
                    "risk_level": "low"
                }
            },
            "candidate2": {
                "overall_assessment": {
                    "overall_score": 60,
                    "hiring_recommendation": "consider",
                    "risk_level": "medium"
                }
            }
        }
        
        summary = cv_analyzer.generate_analysis_summary(test_results)
        
        assert isinstance(summary, str)
        assert "candidate1" in summary
        assert "candidate2" in summary
        assert "80.0/100" in summary
        assert "60.0/100" in summary


if __name__ == "__main__":
    pytest.main([__file__])
