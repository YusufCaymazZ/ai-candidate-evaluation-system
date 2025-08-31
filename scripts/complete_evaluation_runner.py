#!/usr/bin/env python3
"""
Day 3: Complete End-to-End Workflow Script

This script demonstrates the complete candidate evaluation workflow, combining
CV analysis, interview scoring, and comprehensive report generation.

Usage:
    python scripts/day3_complete_workflow.py

Features:
- Complete end-to-end candidate evaluation pipeline
- CV analysis → Interview question generation → Response scoring → Final report
- Batch processing for multiple candidates
- Comprehensive evaluation reports in multiple formats
- Integration of all system components
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from loguru import logger
from src.evaluation.cv_analyzer import CVAnalyzer
from src.evaluation.interview_scorer import InterviewScorer
from src.evaluation.report_generator import ReportGenerator
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
        "logs/complete_workflow.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="1 day"
    )


def main():
    """Main function for Day 3 complete workflow demonstration."""
    logger.info("=" * 60)
    logger.info("DAY 3: COMPLETE END-TO-END WORKFLOW DEMONSTRATION")
    logger.info("=" * 60)
    
    try:
        # Initialize all components
        logger.info("Initializing all evaluation components...")
        cv_analyzer = CVAnalyzer()
        interview_scorer = InterviewScorer()
        report_generator = ReportGenerator()
        file_utils = FileUtils()
        
        # Create sample data if it doesn't exist
        logger.info("Setting up sample data...")
        file_utils.create_sample_data()
        
        # Get available data
        cv_files = file_utils.get_cv_samples()
        job_description_files = file_utils.get_job_descriptions()
        response_files = file_utils.list_files("data/sample_responses", ['.json'])
        
        if not cv_files or not job_description_files or not response_files:
            logger.error("Sample data not found. Please ensure all sample data is available.")
            return 1
        
        logger.info(f"Found {len(cv_files)} CVs, {len(job_description_files)} job descriptions, and {len(response_files)} response files")
        
        # Use first job description for all evaluations
        job_description_file = job_description_files[0]
        job_description = file_utils.read_file(job_description_file)
        
        logger.info(f"Using job description: {Path(job_description_file).name}")
        
        # Complete workflow for each candidate
        all_evaluations = {}
        
        for i, cv_file in enumerate(cv_files):
            cv_name = Path(cv_file).stem
            logger.info(f"\n{'='*50}")
            logger.info(f"PROCESSING CANDIDATE {i+1}: {cv_name}")
            logger.info(f"{'='*50}")
            
            try:
                # Step 1: CV Analysis
                logger.info("\nSTEP 1: CV ANALYSIS")
                logger.info("-" * 20)
                
                cv_analysis = cv_analyzer.analyze_cv_against_job(cv_file, job_description_file)
                if "error" in cv_analysis:
                    logger.error(f"CV analysis failed for {cv_name}: {cv_analysis['error']}")
                    continue
                
                # Display CV analysis results
                overall = cv_analysis.get("overall_assessment", {})
                logger.info(f"CV Score: {overall.get('overall_score', 'N/A'):.1f}/100")
                logger.info(f"CV Recommendation: {overall.get('hiring_recommendation', 'N/A')}")
                
                # Step 2: Generate Interview Questions
                logger.info("\nSTEP 2: GENERATING INTERVIEW QUESTIONS")
                logger.info("-" * 20)
                
                questions = interview_scorer.generate_interview_questions(job_description, cv_analysis)
                if "error" in questions:
                    logger.error(f"Question generation failed for {cv_name}: {questions['error']}")
                    continue
                
                logger.info(f"Generated {len(questions.get('technical_questions', []))} technical questions")
                logger.info(f"Generated {len(questions.get('behavioral_questions', []))} behavioral questions")
                
                # Step 3: Load and Score Interview Responses
                logger.info("\nSTEP 3: INTERVIEW RESPONSE SCORING")
                logger.info("-" * 20)
                
                # Find matching response file for this candidate
                matching_response_file = None
                for response_file in response_files:
                    if cv_name.lower() in Path(response_file).stem.lower():
                        matching_response_file = response_file
                        break
                
                if not matching_response_file:
                    logger.warning(f"No matching response file found for {cv_name}, using first available")
                    matching_response_file = response_files[0]
                
                # Load candidate responses
                candidate_responses = file_utils.load_json(matching_response_file)
                responses = candidate_responses.get("responses", {})
                
                # Create questions-responses pairs
                questions_responses = []
                sample_questions = []
                
                if "technical_questions" in questions:
                    sample_questions.extend(questions["technical_questions"][:2])
                if "behavioral_questions" in questions:
                    sample_questions.extend(questions["behavioral_questions"][:1])
                
                for i, question_data in enumerate(sample_questions):
                    question = question_data.get("question", "")
                    response_key = f"tech_{i+1}" if i < 2 else f"behav_{i-1}"
                    response = responses.get(response_key, "Sample response for demonstration.")
                    
                    questions_responses.append({
                        "question": question,
                        "response": response
                    })
                
                # Score interview responses
                interview_scores = interview_scorer.score_multiple_responses(questions_responses)
                if "error" in interview_scores:
                    logger.error(f"Interview scoring failed for {cv_name}: {interview_scores['error']}")
                    continue
                
                # Display interview results
                interview_overall = interview_scores.get("overall_assessment", {})
                logger.info(f"Interview Score: {interview_overall.get('overall_score', 'N/A')}/10")
                logger.info(f"Interview Recommendation: {interview_overall.get('recommendation', 'N/A')}")
                
                # Step 4: Generate Comprehensive Report
                logger.info("\nSTEP 4: GENERATING COMPREHENSIVE REPORT")
                logger.info("-" * 20)
                
                # Extract candidate info
                candidate_info = {
                    "name": cv_name,
                    "cv_file": Path(cv_file).name,
                    "job_description": Path(job_description_file).name
                }
                
                # Generate comprehensive report
                comprehensive_report = report_generator.generate_comprehensive_report(
                    cv_analysis, interview_scores, candidate_info
                )
                
                if "error" in comprehensive_report:
                    logger.error(f"Report generation failed for {cv_name}: {comprehensive_report['error']}")
                    continue
                
                # Display final recommendation
                final_rec = comprehensive_report.get("final_recommendation", "Unknown")
                logger.info(f"Final Recommendation: {final_rec}")
                
                # Save individual candidate report
                report_file = f"outputs/final_reports/{cv_name}_complete_evaluation.json"
                report_generator.save_report(comprehensive_report, report_file)
                
                # Save markdown summary
                summary_file = f"outputs/final_reports/{cv_name}_summary.md"
                report_generator.save_report(comprehensive_report, summary_file, "markdown")
                
                logger.info(f"Complete evaluation saved to: {report_file}")
                logger.info(f"Summary saved to: {summary_file}")
                
                # Store for batch processing
                all_evaluations[cv_name] = {
                    "cv_analysis": cv_analysis,
                    "interview_scores": interview_scores,
                    "comprehensive_report": comprehensive_report,
                    "candidate_info": candidate_info
                }
                
                logger.info(f"✓ Completed evaluation for {cv_name}")
                
            except Exception as e:
                logger.error(f"Error processing candidate {cv_name}: {e}")
                continue
        
        # Step 5: Generate Batch Summary Report
        logger.info(f"\n{'='*50}")
        logger.info("STEP 5: GENERATING BATCH SUMMARY REPORT")
        logger.info(f"{'='*50}")
        
        if all_evaluations:
            # Create batch summary
            batch_summary = generate_batch_summary(all_evaluations)
            batch_summary_file = "outputs/final_reports/batch_evaluation_summary.md"
            file_utils.save_markdown(batch_summary, batch_summary_file)
            
            logger.info(f"Batch summary saved to: {batch_summary_file}")
            
            # Display batch summary
            logger.info("\n--- BATCH EVALUATION SUMMARY ---")
            print("\n" + batch_summary)
            
            # Generate comparison table
            comparison_table = generate_comparison_table(all_evaluations)
            comparison_file = "outputs/final_reports/candidate_comparison.md"
            file_utils.save_markdown(comparison_table, comparison_file)
            
            logger.info(f"Comparison table saved to: {comparison_file}")
            
        else:
            logger.warning("No successful evaluations to summarize")
        
        # Step 6: Generate Final Recommendations
        logger.info(f"\n{'='*50}")
        logger.info("STEP 6: FINAL RECOMMENDATIONS")
        logger.info(f"{'='*50}")
        
        if all_evaluations:
            recommendations = generate_final_recommendations(all_evaluations)
            recommendations_file = "outputs/final_reports/final_recommendations.md"
            file_utils.save_markdown(recommendations, recommendations_file)
            
            logger.info(f"Final recommendations saved to: {recommendations_file}")
            
            # Display recommendations
            logger.info("\n--- FINAL RECOMMENDATIONS ---")
            print("\n" + recommendations)
        
        logger.info("\n" + "=" * 60)
        logger.info("DAY 3 COMPLETE WORKFLOW DEMONSTRATION FINISHED!")
        logger.info("=" * 60)
        
        # Provide summary
        logger.info(f"\nSUMMARY:")
        logger.info(f"- Processed {len(cv_files)} candidates")
        logger.info(f"- Successfully evaluated {len(all_evaluations)} candidates")
        logger.info(f"- Generated comprehensive reports for each candidate")
        logger.info(f"- Created batch summary and comparison tables")
        
        # Provide next steps
        logger.info(f"\nNEXT STEPS:")
        logger.info("1. Review all generated reports in outputs/final_reports/")
        logger.info("2. Customize evaluation criteria in config/config.yaml")
        logger.info("3. Add your own CVs and job descriptions to data/ directories")
        logger.info("4. Integrate with your existing HR systems")
        logger.info("5. Consider adding Streamlit UI for interactive evaluation")
        
    except Exception as e:
        logger.error(f"Day 3 demonstration failed: {e}")
        logger.exception("Full traceback:")
        return 1
    
    return 0


def generate_batch_summary(evaluations):
    """Generate a summary report for all evaluated candidates."""
    summary = "# Batch Evaluation Summary\n\n"
    summary += f"**Total Candidates Evaluated:** {len(evaluations)}\n\n"
    
    summary += "## Candidate Overview\n\n"
    summary += "| Candidate | CV Score | Interview Score | Overall Score | Final Recommendation |\n"
    summary += "|-----------|----------|-----------------|---------------|---------------------|\n"
    
    for candidate_name, evaluation in evaluations.items():
        cv_analysis = evaluation["cv_analysis"]
        interview_scores = evaluation["interview_scores"]
        comprehensive_report = evaluation["comprehensive_report"]
        
        cv_score = cv_analysis.get("overall_assessment", {}).get("overall_score", 0)
        interview_score = interview_scores.get("overall_assessment", {}).get("overall_score", 0)
        final_rec = comprehensive_report.get("final_recommendation", "Unknown")
        
        # Calculate overall score (CV: 40%, Interview: 60%)
        overall_score = (cv_score * 0.4) + (interview_score * 10 * 0.6)
        
        summary += f"| {candidate_name} | {cv_score:.1f}/100 | {interview_score:.1f}/10 | {overall_score:.1f}/100 | {final_rec.replace('_', ' ').title()} |\n"
    
    summary += "\n## Key Insights\n\n"
    
    # Count recommendations
    recommendations = {}
    for evaluation in evaluations.values():
        rec = evaluation["comprehensive_report"].get("final_recommendation", "Unknown")
        recommendations[rec] = recommendations.get(rec, 0) + 1
    
    for rec, count in recommendations.items():
        percentage = (count / len(evaluations)) * 100
        summary += f"- **{rec.replace('_', ' ').title()}**: {count} candidates ({percentage:.1f}%)\n"
    
    return summary


def generate_comparison_table(evaluations):
    """Generate a detailed comparison table of all candidates."""
    comparison = "# Candidate Comparison Table\n\n"
    
    comparison += "## Detailed Comparison\n\n"
    comparison += "| Metric | " + " | ".join(evaluations.keys()) + " |\n"
    comparison += "|--------|" + "|".join(["---" for _ in evaluations]) + "|\n"
    
    # CV Scores
    cv_scores = []
    for evaluation in evaluations.values():
        score = evaluation["cv_analysis"].get("overall_assessment", {}).get("overall_score", 0)
        cv_scores.append(f"{score:.1f}")
    comparison += f"| CV Score | {' | '.join(cv_scores)} |\n"
    
    # Interview Scores
    interview_scores = []
    for evaluation in evaluations.values():
        score = evaluation["interview_scores"].get("overall_assessment", {}).get("overall_score", 0)
        interview_scores.append(f"{score:.1f}")
    comparison += f"| Interview Score | {' | '.join(interview_scores)} |\n"
    
    # Overall Scores
    overall_scores = []
    for evaluation in evaluations.values():
        cv_score = evaluation["cv_analysis"].get("overall_assessment", {}).get("overall_score", 0)
        interview_score = evaluation["interview_scores"].get("overall_assessment", {}).get("overall_score", 0)
        overall = (cv_score * 0.4) + (interview_score * 10 * 0.6)
        overall_scores.append(f"{overall:.1f}")
    comparison += f"| Overall Score | {' | '.join(overall_scores)} |\n"
    
    # Final Recommendations
    final_recs = []
    for evaluation in evaluations.values():
        rec = evaluation["comprehensive_report"].get("final_recommendation", "Unknown")
        final_recs.append(rec.replace("_", " ").title())
    comparison += f"| Final Recommendation | {' | '.join(final_recs)} |\n"
    
    # Risk Levels
    risk_levels = []
    for evaluation in evaluations.values():
        risk = evaluation["cv_analysis"].get("overall_assessment", {}).get("risk_level", "Unknown")
        risk_levels.append(risk.title())
    comparison += f"| Risk Level | {' | '.join(risk_levels)} |\n"
    
    return comparison


def generate_final_recommendations(evaluations):
    """Generate final recommendations based on all evaluations."""
    recommendations = "# Final Recommendations\n\n"
    
    # Group candidates by recommendation
    grouped_candidates = {}
    for candidate_name, evaluation in evaluations.items():
        rec = evaluation["comprehensive_report"].get("final_recommendation", "Unknown")
        if rec not in grouped_candidates:
            grouped_candidates[rec] = []
        grouped_candidates[rec].append(candidate_name)
    
    recommendations += "## Hiring Recommendations\n\n"
    
    # Strong Hire candidates
    if "strong_hire" in grouped_candidates:
        recommendations += "### Strong Hire Candidates\n\n"
        for candidate in grouped_candidates["strong_hire"]:
            recommendations += f"- **{candidate}**: Excellent fit, recommend immediate offer\n"
        recommendations += "\n"
    
    # Hire candidates
    if "hire" in grouped_candidates:
        recommendations += "### Hire Candidates\n\n"
        for candidate in grouped_candidates["hire"]:
            recommendations += f"- **{candidate}**: Good fit, recommend offer with standard onboarding\n"
        recommendations += "\n"
    
    # Consider candidates
    if "consider" in grouped_candidates:
        recommendations += "### Consider Candidates\n\n"
        for candidate in grouped_candidates["consider"]:
            recommendations += f"- **{candidate}**: Potential fit, recommend additional assessment or probationary period\n"
        recommendations += "\n"
    
    # Reject candidates
    if "reject" in grouped_candidates:
        recommendations += "### Reject Candidates\n\n"
        for candidate in grouped_candidates["reject"]:
            recommendations += f"- **{candidate}**: Not a good fit, recommend rejection with constructive feedback\n"
        recommendations += "\n"
    
    # Next steps
    recommendations += "## Next Steps\n\n"
    recommendations += "1. **Immediate Actions**:\n"
    recommendations += "   - Contact strong hire candidates within 24 hours\n"
    recommendations += "   - Schedule follow-up interviews for consider candidates\n"
    recommendations += "   - Send rejection letters with feedback\n\n"
    
    recommendations += "2. **Process Improvements**:\n"
    recommendations += "   - Review evaluation criteria based on outcomes\n"
    recommendations += "   - Gather feedback from hiring managers\n"
    recommendations += "   - Refine scoring algorithms if needed\n\n"
    
    recommendations += "3. **System Enhancements**:\n"
    recommendations += "   - Consider adding reference checking automation\n"
    recommendations += "   - Implement candidate tracking system integration\n"
    recommendations += "   - Add diversity and inclusion metrics\n"
    
    return recommendations


if __name__ == "__main__":
    setup_logging()
    exit_code = main()
    sys.exit(exit_code)
