#!/usr/bin/env python3
"""
Day 2: Interview Scoring Bot Script

This script demonstrates the interview scoring functionality of the candidate evaluation system.
It generates personalized interview questions and scores candidate responses.

Usage:
    python scripts/day2_interview_scoring.py

Features:
- Generate personalized interview questions based on CV analysis
- Score candidate responses using LLM evaluation
- Provide detailed feedback and recommendations
- Analyze multiple responses for consistency
- Generate comprehensive interview reports
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from src.evaluation.interview_scorer import InterviewScorer
from src.evaluation.cv_analyzer import CVAnalyzer
from src.utils.file_utils import FileUtils


def setup_logging():
    """Setup logging configuration."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        "logs/interview_scoring.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="1 day"
    )


def main():
    """Main function for Day 2 interview scoring demonstration."""
    logger.info("=" * 60)
    logger.info("DAY 2: INTERVIEW SCORING BOT DEMONSTRATION")
    logger.info("=" * 60)
    
    try:
        # Initialize components
        logger.info("Initializing Interview Scorer...")
        interview_scorer = InterviewScorer()
        cv_analyzer = CVAnalyzer()
        file_utils = FileUtils()
        
        # Create sample data if it doesn't exist
        logger.info("Setting up sample data...")
        file_utils.create_sample_data()
        
        # Get available CVs and job descriptions
        cv_files = file_utils.get_cv_samples()
        job_description_files = file_utils.get_job_descriptions()
        
        if not cv_files or not job_description_files:
            logger.error("Sample data not found. Please run Day 1 script first or add sample data.")
            return 1
        
        # Use first CV and job description for demonstration
        cv_file = cv_files[0]
        job_description_file = job_description_files[0]
        
        logger.info(f"Using CV: {Path(cv_file).name}")
        logger.info(f"Using Job Description: {Path(job_description_file).name}")
        
        # Step 1: Analyze CV to get context for question generation
        logger.info("\n" + "=" * 40)
        logger.info("STEP 1: CV ANALYSIS FOR QUESTION GENERATION")
        logger.info("=" * 40)
        
        cv_analysis = cv_analyzer.analyze_cv_against_job(cv_file, job_description_file)
        if "error" in cv_analysis:
            logger.error(f"CV analysis failed: {cv_analysis['error']}")
            return 1
        
        job_description = file_utils.read_file(job_description_file)
        
        # Step 2: Generate personalized interview questions
        logger.info("\n" + "=" * 40)
        logger.info("STEP 2: GENERATING PERSONALIZED INTERVIEW QUESTIONS")
        logger.info("=" * 40)
        
        questions = interview_scorer.generate_interview_questions(job_description, cv_analysis)
        
        if "error" in questions:
            logger.error(f"Question generation failed: {questions['error']}")
            return 1
        
        # Display generated questions
        logger.info("\n--- GENERATED INTERVIEW QUESTIONS ---")
        
        if "technical_questions" in questions:
            logger.info("\nTechnical Questions:")
            for i, q in enumerate(questions["technical_questions"][:3], 1):
                logger.info(f"{i}. {q.get('question', 'N/A')}")
                logger.info(f"   Purpose: {q.get('purpose', 'N/A')}")
                logger.info(f"   Difficulty: {q.get('difficulty', 'N/A')}")
        
        if "behavioral_questions" in questions:
            logger.info("\nBehavioral Questions:")
            for i, q in enumerate(questions["behavioral_questions"][:2], 1):
                logger.info(f"{i}. {q.get('question', 'N/A')}")
                logger.info(f"   Purpose: {q.get('purpose', 'N/A')}")
        
        # Save generated questions
        questions_file = f"outputs/interview_scores/generated_questions_{Path(cv_file).stem}.json"
        interview_scorer.save_interview_results(questions, questions_file)
        logger.info(f"Generated questions saved to: {questions_file}")
        
        # Step 3: Load sample candidate responses
        logger.info("\n" + "=" * 40)
        logger.info("STEP 3: LOADING SAMPLE CANDIDATE RESPONSES")
        logger.info("=" * 40)
        
        sample_responses_dir = "data/sample_responses"
        response_files = file_utils.list_files(sample_responses_dir, ['.json'])
        
        if not response_files:
            logger.error("No sample response files found.")
            return 1
        
        # Load first sample response file
        response_file = response_files[0]
        candidate_responses = file_utils.load_json(response_file)
        
        logger.info(f"Loaded responses for candidate: {candidate_responses.get('candidate_id', 'Unknown')}")
        
        # Step 4: Score individual responses
        logger.info("\n" + "=" * 40)
        logger.info("STEP 4: SCORING INDIVIDUAL RESPONSES")
        logger.info("=" * 40)
        
        # Create questions-responses pairs for scoring
        questions_responses = []
        
        # Get some sample questions from our generated questions
        sample_questions = []
        if "technical_questions" in questions:
            sample_questions.extend(questions["technical_questions"][:2])
        if "behavioral_questions" in questions:
            sample_questions.extend(questions["behavioral_questions"][:1])
        
        # Match questions with responses
        responses = candidate_responses.get("responses", {})
        for i, question_data in enumerate(sample_questions):
            question = question_data.get("question", "")
            # Use a response if available, otherwise create a placeholder
            response_key = f"tech_{i+1}" if i < 2 else f"behav_{i-1}"
            response = responses.get(response_key, "Sample response for demonstration purposes.")
            
            questions_responses.append({
                "question": question,
                "response": response
            })
        
        # Score each response
        logger.info("\n--- INDIVIDUAL RESPONSE SCORING ---")
        
        for i, qr in enumerate(questions_responses, 1):
            question = qr["question"]
            response = qr["response"]
            
            logger.info(f"\nScoring Response {i}:")
            logger.info(f"Question: {question[:100]}...")
            logger.info(f"Response: {response[:100]}...")
            
            score_result = interview_scorer.score_interview_response(question, response)
            
            if "error" in score_result:
                logger.warning(f"Scoring failed: {score_result['error']}")
                continue
            
            # Display scoring results
            overall_score = score_result.get("overall_score", 0)
            recommendation = score_result.get("recommendation", "Unknown")
            
            logger.info(f"Overall Score: {overall_score}/10")
            logger.info(f"Recommendation: {recommendation}")
            
            if "strengths" in score_result and score_result["strengths"]:
                logger.info(f"Strengths: {', '.join(score_result['strengths'][:2])}")
            
            if "weaknesses" in score_result and score_result["weaknesses"]:
                logger.info(f"Areas for Improvement: {', '.join(score_result['weaknesses'][:2])}")
        
        # Step 5: Score multiple responses together
        logger.info("\n" + "=" * 40)
        logger.info("STEP 5: COMPREHENSIVE MULTI-RESPONSE SCORING")
        logger.info("=" * 40)
        
        comprehensive_results = interview_scorer.score_multiple_responses(questions_responses)
        
        if "error" in comprehensive_results:
            logger.error(f"Comprehensive scoring failed: {comprehensive_results['error']}")
            return 1
        
        # Display comprehensive results
        logger.info("\n--- COMPREHENSIVE INTERVIEW RESULTS ---")
        
        overall_assessment = comprehensive_results.get("overall_assessment", {})
        logger.info(f"Overall Interview Score: {overall_assessment.get('overall_score', 'N/A')}/10")
        logger.info(f"Performance Level: {overall_assessment.get('performance_level', 'N/A')}")
        logger.info(f"Consistency Score: {overall_assessment.get('consistency_score', 'N/A')}%")
        logger.info(f"Final Recommendation: {overall_assessment.get('recommendation', 'N/A')}")
        
        # Display criteria breakdown
        summary_stats = comprehensive_results.get("summary_statistics", {})
        criteria_averages = summary_stats.get("criteria_averages", {})
        
        if criteria_averages:
            logger.info("\nCriteria Breakdown:")
            for criteria, score in criteria_averages.items():
                logger.info(f"  {criteria.replace('_', ' ').title()}: {score}/10")
        
        # Display recommendations
        recommendations = comprehensive_results.get("recommendations", [])
        if recommendations:
            logger.info("\nRecommendations:")
            for rec in recommendations[:3]:
                logger.info(f"  - {rec}")
        
        # Save comprehensive results
        results_file = f"outputs/interview_scores/comprehensive_results_{Path(cv_file).stem}.json"
        interview_scorer.save_interview_results(comprehensive_results, results_file)
        logger.info(f"Comprehensive results saved to: {results_file}")
        
        # Step 6: Generate interview summary
        logger.info("\n" + "=" * 40)
        logger.info("STEP 6: GENERATING INTERVIEW SUMMARY")
        logger.info("=" * 40)
        
        summary = interview_scorer.generate_interview_summary(comprehensive_results)
        summary_file = f"outputs/interview_scores/interview_summary_{Path(cv_file).stem}.md"
        file_utils.save_markdown(summary, summary_file)
        logger.info(f"Interview summary saved to: {summary_file}")
        
        # Display summary
        logger.info("\n--- INTERVIEW SUMMARY ---")
        print("\n" + summary)
        
        # Step 7: Demonstrate batch processing with multiple candidates
        logger.info("\n" + "=" * 40)
        logger.info("STEP 7: BATCH PROCESSING DEMONSTRATION")
        logger.info("=" * 40)
        
        # Process multiple response files
        batch_results = {}
        
        for response_file in response_files[:2]:  # Process first 2 response files
            candidate_id = Path(response_file).stem
            logger.info(f"Processing candidate: {candidate_id}")
            
            candidate_responses = file_utils.load_json(response_file)
            responses = candidate_responses.get("responses", {})
            
            # Create questions-responses pairs for this candidate
            candidate_qr = []
            for i, question_data in enumerate(sample_questions):
                question = question_data.get("question", "")
                response_key = f"tech_{i+1}" if i < 2 else f"behav_{i-1}"
                response = responses.get(response_key, "Sample response.")
                
                candidate_qr.append({
                    "question": question,
                    "response": response
                })
            
            # Score this candidate
            candidate_results = interview_scorer.score_multiple_responses(candidate_qr)
            batch_results[candidate_id] = candidate_results
        
        # Display batch results summary
        logger.info("\n--- BATCH RESULTS SUMMARY ---")
        
        for candidate_id, results in batch_results.items():
            if "error" in results:
                logger.warning(f"{candidate_id}: Error - {results['error']}")
                continue
            
            overall = results.get("overall_assessment", {})
            score = overall.get("overall_score", 0)
            recommendation = overall.get("recommendation", "Unknown")
            
            logger.info(f"{candidate_id}: Score {score:.1f}/10, Recommendation: {recommendation}")
        
        # Save batch results
        batch_file = f"outputs/interview_scores/batch_interview_results.json"
        interview_scorer.save_interview_results(batch_results, batch_file)
        logger.info(f"Batch results saved to: {batch_file}")
        
        logger.info("\n" + "=" * 60)
        logger.info("DAY 2 DEMONSTRATION COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        
        # Provide next steps
        logger.info("\nNEXT STEPS:")
        logger.info("1. Review the generated interview files in outputs/interview_scores/")
        logger.info("2. Run Day 3 script for complete workflow: python scripts/day3_complete_workflow.py")
        logger.info("3. Customize questions and scoring criteria in config/config.yaml")
        
    except Exception as e:
        logger.error(f"Day 2 demonstration failed: {e}")
        logger.exception("Full traceback:")
        return 1
    
    return 0


if __name__ == "__main__":
    setup_logging()
    exit_code = main()
    sys.exit(exit_code)
