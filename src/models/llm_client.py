"""
LLM Client for Candidate Evaluation System

This module provides a unified interface for interacting with Hugging Face models
for CV analysis, interview scoring, and report generation.
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from typing import Dict, List, Optional, Union
import yaml
import os
from loguru import logger


class LLMClient:
    """
    Client for interacting with Hugging Face language models.
    
    Supports both instruction-tuned models (like Mistral) and conversational models
    (like DialoGPT) for different evaluation tasks.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize the LLM client with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.model = None
        self.tokenizer = None
        self.device = self._setup_device()
        self._load_model()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return default configuration if config file is missing."""
        return {
            'model': {
                'name': 'microsoft/DialoGPT-medium',
                'max_length': 1024,
                'temperature': 0.7,
                'top_p': 0.9,
                'do_sample': True
            },
            'hardware': {
                'use_gpu': False,
                'batch_size': 1
            }
        }
    
    def _setup_device(self) -> str:
        """Setup the device (CPU/GPU) for model inference."""
        if self.config['hardware']['use_gpu'] and torch.cuda.is_available():
            device = "cuda"
            logger.info("Using CUDA for GPU acceleration")
        else:
            device = "cpu"
            logger.info("Using CPU for inference")
        return device
    
    def _load_model(self):
        """Load the specified Hugging Face model and tokenizer."""
        try:
            model_name = self.config['model']['name']
            logger.info(f"Loading model: {model_name}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                low_cpu_mem_usage=True
            )
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            logger.success(f"Model {model_name} loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load primary model: {e}")
            self._load_fallback_model()
    
    def _load_fallback_model(self):
        """Load a smaller fallback model if the primary model fails."""
        try:
            fallback_model = self.config['model'].get('alternative_model', 'microsoft/DialoGPT-medium')
            logger.info(f"Loading fallback model: {fallback_model}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(fallback_model)
            self.model = AutoModelForCausalLM.from_pretrained(fallback_model)
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            logger.success(f"Fallback model {fallback_model} loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load fallback model: {e}")
            raise RuntimeError("No models could be loaded")
    
    def generate_response(self, prompt: str, max_new_tokens: Optional[int] = None) -> str:
        """
        Generate a response using the loaded model.
        
        Args:
            prompt: Input prompt for the model
            max_new_tokens: Maximum number of new tokens to generate
            
        Returns:
            Generated response text
        """
        try:
            # Use config max_new_tokens if not specified
            if max_new_tokens is None:
                max_new_tokens = self.config['model']['max_new_tokens']
            
            # Tokenize input with proper truncation and attention mask
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", truncation=True, max_length=2048)
            
            # Create attention mask
            attention_mask = torch.ones_like(inputs)
            
            if self.device == "cuda":
                inputs = inputs.to(self.device)
                attention_mask = attention_mask.to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    attention_mask=attention_mask,
                    max_new_tokens=max_new_tokens,
                    temperature=self.config['model']['temperature'],
                    top_p=self.config['model']['top_p'],
                    do_sample=self.config['model']['do_sample'],
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1,
                    length_penalty=1.0
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the input prompt from the response
            response = response[len(prompt):].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error: {str(e)}"
    
    def analyze_cv(self, cv_text: str, job_description: str) -> Dict:
        """
        Analyze a CV against a job description.
        
        Args:
            cv_text: Text content of the CV
            job_description: Job description text
            
        Returns:
            Dictionary containing analysis results
        """
        prompt = f"""
        Analyze the following CV against the job description and provide a structured evaluation.
        
        CV:
        {cv_text}
        
        Job Description:
        {job_description}
        
        Please provide your analysis in the following JSON format:
        {{
            "overall_score": 0-100,
            "skill_match": {{
                "required_skills": ["skill1", "skill2"],
                "missing_skills": ["skill3", "skill4"],
                "skill_match_percentage": 0-100
            }},
            "experience_assessment": {{
                "years_experience": "estimated_years",
                "relevant_experience": "yes/no",
                "experience_score": 0-100
            }},
            "recommendations": ["recommendation1", "recommendation2"],
            "confidence": 0-100
        }}
        """
        
        response = self.generate_response(prompt)
        return self._parse_json_response(response)
    
    def score_interview_response(self, question: str, response: str, criteria: List[str]) -> Dict:
        """
        Score an interview response based on specified criteria.
        
        Args:
            question: Interview question
            response: Candidate's response
            criteria: List of evaluation criteria
            
        Returns:
            Dictionary containing scoring results
        """
        criteria_str = ", ".join(criteria)
        prompt = f"""
        Score the following interview response based on the criteria: {criteria_str}
        
        Question: {question}
        Response: {response}
        
        Please provide your scoring in the following JSON format:
        {{
            "overall_score": 1-10,
            "criteria_scores": {{
                "technical_knowledge": 1-10,
                "communication": 1-10,
                "problem_solving": 1-10,
                "cultural_fit": 1-10
            }},
            "strengths": ["strength1", "strength2"],
            "weaknesses": ["weakness1", "weakness2"],
            "feedback": "detailed_feedback_here",
            "recommendation": "hire/consider/reject"
        }}
        """
        
        response_text = self.generate_response(prompt)
        return self._parse_json_response(response_text)
    
    def generate_report(self, cv_analysis: Dict, interview_scores: Dict) -> str:
        """
        Generate a comprehensive evaluation report.
        
        Args:
            cv_analysis: Results from CV analysis
            interview_scores: Results from interview scoring
            
        Returns:
            Formatted report text
        """
        prompt = f"""
        Generate a comprehensive candidate evaluation report based on the following data:
        
        CV Analysis: {cv_analysis}
        Interview Scores: {interview_scores}
        
        Please create a professional report that includes:
        1. Executive Summary
        2. Technical Assessment
        3. Interview Performance
        4. Overall Recommendation
        5. Next Steps
        
        Format the report in Markdown.
        """
        
        return self.generate_response(prompt)
    
    def _parse_json_response(self, response: str) -> Dict:
        """
        Parse JSON response from the model, with fallback to text.
        
        Args:
            response: Model response text
            
        Returns:
            Parsed dictionary or fallback text
        """
        try:
            # Try to extract JSON from the response
            import json
            import re
            
            # Find JSON-like content in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                return {"raw_response": response, "parse_error": "No JSON found"}
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response, returning raw text")
            return {"raw_response": response, "parse_error": "Invalid JSON"}
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model."""
        return {
            "model_name": self.config['model']['name'],
            "device": self.device,
            "max_length": self.config['model']['max_length'],
            "temperature": self.config['model']['temperature']
        }
