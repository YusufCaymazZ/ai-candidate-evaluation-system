"""
File Utilities for Candidate Evaluation System

This module provides utilities for reading and processing various file formats
including PDFs, Word documents, and text files for CVs and job descriptions.
"""

import os
import json
import yaml
from typing import Dict, List, Optional, Union
from pathlib import Path
import PyPDF2
from docx import Document
import pandas as pd
from loguru import logger


class FileUtils:
    """
    Utility class for file operations in the candidate evaluation system.
    
    Supports reading CVs and job descriptions from various file formats
    and managing output files for analysis results.
    """
    
    def __init__(self, base_path: str = "."):
        """
        Initialize FileUtils with base path.
        
        Args:
            base_path: Base directory for file operations
        """
        self.base_path = Path(base_path)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            "data/cv_samples",
            "data/job_descriptions", 
            "data/interview_questions",
            "data/sample_responses",
            "outputs/cv_analysis_results",
            "outputs/interview_scores",
            "outputs/final_reports",
            "logs"
        ]
        
        for directory in directories:
            dir_path = self.base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {dir_path}")
    
    def read_text_file(self, file_path: str) -> str:
        """
        Read text content from a text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            File content as string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            return ""
    
    def read_pdf_file(self, file_path: str) -> str:
        """
        Extract text content from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error reading PDF file {file_path}: {e}")
            return ""
    
    def read_word_file(self, file_path: str) -> str:
        """
        Extract text content from a Word document.
        
        Args:
            file_path: Path to the Word document
            
        Returns:
            Extracted text content
        """
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error reading Word file {file_path}: {e}")
            return ""
    
    def read_file(self, file_path: str) -> str:
        """
        Read file content based on file extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content as string
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return ""
        
        extension = file_path.suffix.lower()
        
        if extension == '.txt':
            return self.read_text_file(str(file_path))
        elif extension == '.pdf':
            return self.read_pdf_file(str(file_path))
        elif extension in ['.docx', '.doc']:
            return self.read_word_file(str(file_path))
        else:
            logger.warning(f"Unsupported file extension: {extension}")
            return self.read_text_file(str(file_path))
    
    def save_json(self, data: Dict, file_path: str, indent: int = 2):
        """
        Save data to a JSON file.
        
        Args:
            data: Data to save
            file_path: Output file path
            indent: JSON indentation
        """
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=indent, ensure_ascii=False)
            
            logger.info(f"Saved JSON file: {file_path}")
        except Exception as e:
            logger.error(f"Error saving JSON file {file_path}: {e}")
    
    def load_json(self, file_path: str) -> Dict:
        """
        Load data from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Loaded data dictionary
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            logger.error(f"Error loading JSON file {file_path}: {e}")
            return {}
    
    def save_markdown(self, content: str, file_path: str):
        """
        Save content to a Markdown file.
        
        Args:
            content: Markdown content to save
            file_path: Output file path
        """
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            logger.info(f"Saved Markdown file: {file_path}")
        except Exception as e:
            logger.error(f"Error saving Markdown file {file_path}: {e}")
    
    def list_files(self, directory: str, extensions: Optional[List[str]] = None) -> List[str]:
        """
        List files in a directory with optional extension filtering.
        
        Args:
            directory: Directory to search
            extensions: List of file extensions to include (e.g., ['.pdf', '.txt'])
            
        Returns:
            List of file paths
        """
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                logger.warning(f"Directory not found: {directory}")
                return []
            
            files = []
            for file_path in dir_path.iterdir():
                if file_path.is_file():
                    if extensions is None or file_path.suffix.lower() in extensions:
                        files.append(str(file_path))
            
            return sorted(files)
        except Exception as e:
            logger.error(f"Error listing files in {directory}: {e}")
            return []
    
    def get_cv_samples(self) -> List[str]:
        """
        Get list of CV sample files.
        
        Returns:
            List of CV file paths
        """
        cv_dir = self.base_path / "data" / "cv_samples"
        return self.list_files(str(cv_dir), ['.pdf', '.docx', '.txt'])
    
    def get_job_descriptions(self) -> List[str]:
        """
        Get list of job description files.
        
        Returns:
            List of job description file paths
        """
        jd_dir = self.base_path / "data" / "job_descriptions"
        return self.list_files(str(jd_dir), ['.pdf', '.docx', '.txt'])
    
    def create_sample_data(self):
        """
        Create sample data files for demonstration purposes.
        """
        self._create_sample_cvs()
        self._create_sample_job_descriptions()
        self._create_sample_interview_questions()
        self._create_sample_responses()
    
    def _create_sample_cvs(self):
        """Create sample CV files."""
        cv_samples = {
            "senior_developer.txt": """
JOHN DOE
Senior Software Developer
john.doe@email.com | +1-555-0123 | linkedin.com/in/johndoe

PROFESSIONAL SUMMARY
Experienced software developer with 8+ years in full-stack development, specializing in Python, JavaScript, and cloud technologies. Led multiple successful projects and mentored junior developers.

TECHNICAL SKILLS
Programming Languages: Python, JavaScript, Java, SQL
Frameworks: Django, React, Spring Boot, Node.js
Cloud Platforms: AWS, Azure, Google Cloud
Databases: PostgreSQL, MongoDB, Redis
Tools: Git, Docker, Kubernetes, Jenkins

WORK EXPERIENCE
Senior Developer | TechCorp Inc. | 2020-Present
- Led development of microservices architecture serving 1M+ users
- Mentored 5 junior developers and conducted code reviews
- Implemented CI/CD pipelines reducing deployment time by 60%

Software Developer | StartupXYZ | 2018-2020
- Developed REST APIs and frontend applications
- Collaborated with cross-functional teams on agile projects
- Optimized database queries improving performance by 40%

EDUCATION
Bachelor of Science in Computer Science | University of Technology | 2018
            """,
            
            "junior_developer.txt": """
JANE SMITH
Junior Software Developer
jane.smith@email.com | +1-555-0456 | linkedin.com/in/janesmith

PROFESSIONAL SUMMARY
Recent graduate with 2 years of experience in web development. Passionate about learning new technologies and contributing to innovative projects.

TECHNICAL SKILLS
Programming Languages: Python, JavaScript, HTML/CSS
Frameworks: Flask, React, Bootstrap
Databases: SQLite, MySQL
Tools: Git, VS Code, Postman

WORK EXPERIENCE
Junior Developer | WebSolutions | 2022-Present
- Developed responsive web applications using React and Python
- Collaborated with senior developers on feature implementation
- Participated in code reviews and testing

Intern | TechStartup | 2021-2022
- Assisted in frontend development tasks
- Learned modern development practices and tools
- Contributed to bug fixes and documentation

EDUCATION
Bachelor of Science in Computer Science | State University | 2022
            """
        }
        
        cv_dir = self.base_path / "data" / "cv_samples"
        for filename, content in cv_samples.items():
            file_path = cv_dir / filename
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content.strip())
        
        logger.info("Created sample CV files")
    
    def _create_sample_job_descriptions(self):
        """Create sample job description files."""
        job_descriptions = {
            "senior_python_developer.txt": """
SENIOR PYTHON DEVELOPER

We are seeking an experienced Senior Python Developer to join our growing team. You will be responsible for designing, developing, and maintaining high-quality software solutions.

REQUIREMENTS:
- 5+ years of experience in Python development
- Strong knowledge of Django, Flask, or similar frameworks
- Experience with cloud platforms (AWS, Azure, or GCP)
- Proficiency in SQL and database design
- Experience with microservices architecture
- Knowledge of Docker and Kubernetes
- Strong problem-solving and communication skills
- Bachelor's degree in Computer Science or related field

RESPONSIBILITIES:
- Design and implement scalable software solutions
- Lead technical discussions and code reviews
- Mentor junior developers
- Collaborate with cross-functional teams
- Optimize application performance
- Ensure code quality and best practices

NICE TO HAVE:
- Experience with machine learning libraries
- Knowledge of DevOps practices
- Experience with React or Vue.js
- Agile/Scrum methodology experience
            """,
            
            "junior_developer.txt": """
JUNIOR SOFTWARE DEVELOPER

We are looking for a motivated Junior Developer to join our team and grow their skills in a collaborative environment.

REQUIREMENTS:
- 1-3 years of experience in software development
- Knowledge of Python or JavaScript
- Basic understanding of web development
- Familiarity with Git version control
- Strong learning ability and teamwork skills
- Bachelor's degree in Computer Science or related field

RESPONSIBILITIES:
- Develop and maintain web applications
- Collaborate with senior developers
- Participate in code reviews
- Write clean, maintainable code
- Learn new technologies and frameworks

NICE TO HAVE:
- Experience with React, Django, or Flask
- Knowledge of databases and SQL
- Understanding of REST APIs
- Experience with testing frameworks
            """
        }
        
        jd_dir = self.base_path / "data" / "job_descriptions"
        for filename, content in job_descriptions.items():
            file_path = jd_dir / filename
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content.strip())
        
        logger.info("Created sample job description files")
    
    def _create_sample_interview_questions(self):
        """Create sample interview questions."""
        questions = {
            "technical_questions.json": {
                "questions": [
                    {
                        "id": "tech_1",
                        "category": "technical",
                        "question": "Explain the difference between a list and a tuple in Python.",
                        "expected_keywords": ["mutable", "immutable", "performance", "memory"]
                    },
                    {
                        "id": "tech_2", 
                        "category": "technical",
                        "question": "How would you design a REST API for a user management system?",
                        "expected_keywords": ["endpoints", "HTTP methods", "authentication", "validation"]
                    },
                    {
                        "id": "tech_3",
                        "category": "technical", 
                        "question": "Describe your experience with database optimization.",
                        "expected_keywords": ["indexing", "query optimization", "normalization", "performance"]
                    }
                ]
            },
            "behavioral_questions.json": {
                "questions": [
                    {
                        "id": "behav_1",
                        "category": "behavioral",
                        "question": "Tell me about a challenging project you worked on and how you overcame obstacles.",
                        "expected_keywords": ["problem-solving", "collaboration", "learning", "persistence"]
                    },
                    {
                        "id": "behav_2",
                        "category": "behavioral", 
                        "question": "How do you handle working with difficult team members?",
                        "expected_keywords": ["communication", "patience", "conflict resolution", "teamwork"]
                    }
                ]
            }
        }
        
        questions_dir = self.base_path / "data" / "interview_questions"
        for filename, content in questions.items():
            file_path = questions_dir / filename
            self.save_json(content, str(file_path))
        
        logger.info("Created sample interview questions")
    
    def _create_sample_responses(self):
        """Create sample candidate responses."""
        responses = {
            "senior_candidate_responses.json": {
                "candidate_id": "senior_dev_001",
                "responses": {
                    "tech_1": "Lists and tuples are both sequence types in Python, but lists are mutable while tuples are immutable. Lists use square brackets and can be modified after creation, while tuples use parentheses and cannot be changed. Tuples are generally more memory efficient and slightly faster for iteration.",
                    "tech_2": "I would design RESTful endpoints like /users for user management, /users/{id} for specific users, using GET, POST, PUT, DELETE methods. I'd implement JWT authentication, input validation, and proper HTTP status codes.",
                    "behav_1": "I led a project to migrate a monolithic application to microservices. The main challenge was data consistency across services. I solved this by implementing event sourcing and CQRS patterns, which improved system reliability."
                }
            },
            "junior_candidate_responses.json": {
                "candidate_id": "junior_dev_001", 
                "responses": {
                    "tech_1": "Lists can be changed but tuples cannot. Lists use [] and tuples use (). I think tuples are faster.",
                    "tech_2": "I would create endpoints for users with GET and POST methods. I'm still learning about authentication.",
                    "behav_1": "I worked on a group project in school where we had to build a web app. It was challenging because we had different schedules, but we used Slack to communicate and met regularly."
                }
            }
        }
        
        responses_dir = self.base_path / "data" / "sample_responses"
        for filename, content in responses.items():
            file_path = responses_dir / filename
            self.save_json(content, str(file_path))
        
        logger.info("Created sample candidate responses")
