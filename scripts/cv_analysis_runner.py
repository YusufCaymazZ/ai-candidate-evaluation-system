#!/usr/bin/env python3
"""
Day 1: CV Gap Analyzer Script

This script demonstrates the CV analysis functionality of the candidate evaluation system.
It analyzes CVs against job descriptions to identify skill gaps and provide recommendations.

Usage:
    python scripts/day1_cv_analysis.py

Features:
- Load and analyze CV files (PDF, DOCX, TXT)
- Compare against job descriptions
- Extract skills and identify gaps
- Generate comprehensive analysis reports
- Save results in multiple formats
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
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
        "logs/cv_analysis.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="1 day"
    )


def main():
    """Main function for Day 1 CV analysis demonstration."""
    logger.info("=" * 60)
    logger.info("DAY 1: CV GAP ANALYZER DEMONSTRATION")
    logger.info("=" * 60)
    
    try:
        # Initialize components
        logger.info("Initializing CV Analyzer...")
        cv_analyzer = CVAnalyzer()
        file_utils = FileUtils()
        
        # Create sample data if it doesn't exist
        logger.info("Setting up sample data...")
        file_utils.create_sample_data()
        
        # Get available CVs and job descriptions
        cv_files = file_utils.get_cv_samples()
        job_description_files = file_utils.get_job_descriptions()
        
        if not cv_files:
            logger.error("No CV files found. Please add CV files to data/cv_samples/")
            return
        
        if not job_description_files:
            logger.error("No job description files found. Please add job descriptions to data/job_descriptions/")
            return
        
        logger.info(f"Found {len(cv_files)} CV files and {len(job_description_files)} job description files")
        
        # Demonstrate single CV analysis
        logger.info("\n" + "=" * 40)
        logger.info("SINGLE CV ANALYSIS DEMONSTRATION")
        logger.info("=" * 40)
        
        # Analyze senior CV against junior job description (to test overqualification)
        cv_file = cv_files[1]  # senior_developer.txt
        job_description_file = job_description_files[0]  # junior_developer.txt (junior job)
        
        logger.info(f"Analyzing CV: {Path(cv_file).name}")
        logger.info(f"Against Job Description: {Path(job_description_file).name}")
        
        # Perform analysis
        analysis_result = cv_analyzer.analyze_cv_against_job(cv_file, job_description_file)
        
        if "error" in analysis_result:
            logger.error(f"Analysis failed: {analysis_result['error']}")
            return
        
        # Display key results
        logger.info("\n--- ANALYSIS RESULTS ---")
        
        # Overall assessment
        overall = analysis_result.get("overall_assessment", {})
        logger.info(f"Overall Score: {overall.get('overall_score', 'N/A'):.1f}/100")
        logger.info(f"Hiring Recommendation: {overall.get('hiring_recommendation', 'N/A')}")
        logger.info(f"Risk Level: {overall.get('risk_level', 'N/A')}")
        
        # Overqualification analysis
        if overall.get("overqualification_risk"):
            logger.info(f"Overqualification Risk: {overall.get('overqualification_risk', 'N/A')}")
            logger.info(f"Retention Risk: {overall.get('retention_risk', 'N/A')}")
            if overall.get("risk_factors"):
                logger.info(f"Risk Factors: {', '.join(overall['risk_factors'][:2])}")
        
        # Skill gaps
        skill_gaps = analysis_result.get("skill_gaps", {})
        missing_skills = skill_gaps.get("missing_technical_skills", [])
        gap_score = skill_gaps.get("gap_score", 0)
        
        logger.info(f"Skill Gap Score: {gap_score:.1f}%")
        if missing_skills:
            logger.info(f"Missing Skills: {', '.join(missing_skills[:5])}")
        
        # Strengths and weaknesses
        if overall.get("strengths"):
            logger.info(f"Strengths: {', '.join(overall['strengths'][:3])}")
        
        if overall.get("weaknesses"):
            logger.info(f"Areas of Concern: {', '.join(overall['weaknesses'][:3])}")
        
        # Save detailed results
        output_file = f"outputs/cv_analysis_results/{Path(cv_file).stem}_analysis.json"
        cv_analyzer.save_analysis_results(analysis_result, output_file)
        logger.info(f"Detailed analysis saved to: {output_file}")
        
        # Demonstrate batch analysis
        logger.info("\n" + "=" * 40)
        logger.info("BATCH CV ANALYSIS DEMONSTRATION")
        logger.info("=" * 40)
        
        # Analyze all CVs against the first job description
        logger.info(f"Analyzing {len(cv_files)} CVs against job description: {Path(job_description_file).name}")
        
        batch_results = cv_analyzer.batch_analyze_cvs(cv_files, job_description_file)
        
        # Display batch results summary
        logger.info("\n--- BATCH ANALYSIS SUMMARY ---")
        
        for cv_name, result in batch_results.items():
            if "error" in result:
                logger.warning(f"{cv_name}: Error - {result['error']}")
                continue
            
            overall = result.get("overall_assessment", {})
            score = overall.get("overall_score", 0)
            recommendation = overall.get("hiring_recommendation", "Unknown")
            
            logger.info(f"{cv_name}: Score {score:.1f}/100, Recommendation: {recommendation}")
        
        # Save batch results
        batch_output_file = f"outputs/cv_analysis_results/batch_analysis_{Path(job_description_file).stem}.json"
        cv_analyzer.save_analysis_results(batch_results, batch_output_file)
        logger.info(f"Batch analysis results saved to: {batch_output_file}")
        
        # Generate summary report
        logger.info("\n" + "=" * 40)
        logger.info("GENERATING SUMMARY REPORT")
        logger.info("=" * 40)
        
        summary = cv_analyzer.generate_analysis_summary(batch_results)
        summary_file = f"outputs/cv_analysis_results/analysis_summary.md"
        file_utils.save_markdown(summary, summary_file)
        logger.info(f"Summary report saved to: {summary_file}")
        
        # Display summary
        logger.info("\n--- SUMMARY REPORT ---")
        print("\n" + summary)
        
        logger.info("\n" + "=" * 60)
        logger.info("DAY 1 DEMONSTRATION COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        
        # Provide next steps
        logger.info("\nNEXT STEPS:")
        logger.info("1. Review the generated analysis files in outputs/cv_analysis_results/")
        logger.info("2. Run Day 2 script for interview scoring: python scripts/day2_interview_scoring.py")
        logger.info("3. Run Day 3 script for complete workflow: python scripts/day3_complete_workflow.py")
        
    except Exception as e:
        logger.error(f"Day 1 demonstration failed: {e}")
        logger.exception("Full traceback:")
        return 1
    
    return 0


if __name__ == "__main__":
    setup_logging()
    exit_code = main()
    sys.exit(exit_code)
