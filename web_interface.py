#!/usr/bin/env python3
"""
Streamlit Web Application for Candidate Evaluation System

This application provides an interactive web interface for the candidate evaluation system,
allowing users to upload CVs, job descriptions, and interview responses, then view
comprehensive evaluation results.

Usage:
    streamlit run streamlit_app.py
"""

import streamlit as st
import sys
import os
from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from src.evaluation.cv_analyzer import CVAnalyzer
from src.evaluation.interview_scorer import InterviewScorer
from src.evaluation.report_generator import ReportGenerator
from src.utils.file_utils import FileUtils


def setup_page():
    """Setup the Streamlit page configuration."""
    st.set_page_config(
        page_title="Candidate Evaluation System",
        page_icon="👥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎯 Candidate Evaluation System")
    st.markdown("---")


def initialize_components():
    """Initialize evaluation components."""
    if 'cv_analyzer' not in st.session_state:
        with st.spinner("Initializing CV Analyzer..."):
            st.session_state.cv_analyzer = CVAnalyzer()
    
    if 'interview_scorer' not in st.session_state:
        with st.spinner("Initializing Interview Scorer..."):
            st.session_state.interview_scorer = InterviewScorer()
    
    if 'report_generator' not in st.session_state:
        with st.spinner("Initializing Report Generator..."):
            st.session_state.report_generator = ReportGenerator()
    
    if 'file_utils' not in st.session_state:
        st.session_state.file_utils = FileUtils()


def upload_section():
    """File upload section."""
    st.header("📁 Upload Files")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("CV Upload")
        uploaded_cv = st.file_uploader(
            "Upload CV (PDF, DOCX, TXT)",
            type=['pdf', 'docx', 'txt'],
            key="cv_upload"
        )
        
        if uploaded_cv:
            st.success(f"✅ CV uploaded: {uploaded_cv.name}")
            
            # Save uploaded file
            cv_path = f"temp/{uploaded_cv.name}"
            os.makedirs("temp", exist_ok=True)
            with open(cv_path, "wb") as f:
                f.write(uploaded_cv.getbuffer())
            st.session_state.cv_path = cv_path
    
    with col2:
        st.subheader("Job Description Upload")
        uploaded_jd = st.file_uploader(
            "Upload Job Description (PDF, DOCX, TXT)",
            type=['pdf', 'docx', 'txt'],
            key="jd_upload"
        )
        
        if uploaded_jd:
            st.success(f"✅ Job Description uploaded: {uploaded_jd.name}")
            
            # Save uploaded file
            jd_path = f"temp/{uploaded_jd.name}"
            with open(jd_path, "wb") as f:
                f.write(uploaded_jd.getbuffer())
            st.session_state.jd_path = jd_path


def cv_analysis_section():
    """CV analysis section."""
    st.header("📊 CV Analysis")
    
    if 'cv_path' in st.session_state and 'jd_path' in st.session_state:
        if st.button("🔍 Analyze CV", type="primary"):
            with st.spinner("Analyzing CV..."):
                try:
                    analysis_result = st.session_state.cv_analyzer.analyze_cv_against_job(
                        st.session_state.cv_path, st.session_state.jd_path
                    )
                    
                    if "error" not in analysis_result:
                        st.session_state.cv_analysis = analysis_result
                        st.success("✅ CV Analysis completed!")
                        display_cv_results(analysis_result)
                    else:
                        st.error(f"❌ Analysis failed: {analysis_result['error']}")
                        
                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")
    else:
        st.info("📝 Please upload both CV and Job Description files to begin analysis.")


def display_cv_results(analysis_result):
    """Display CV analysis results."""
    overall = analysis_result.get("overall_assessment", {})
    
    # Create metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Overall Score",
            f"{overall.get('overall_score', 0):.1f}/100",
            delta=None
        )
    
    with col2:
        recommendation = overall.get('hiring_recommendation', 'Unknown')
        st.metric("Recommendation", recommendation.replace('_', ' ').title())
    
    with col3:
        risk_level = overall.get('risk_level', 'Unknown')
        st.metric("Risk Level", risk_level.title())
    
    with col4:
        skill_gaps = analysis_result.get("skill_gaps", {})
        gap_score = skill_gaps.get("gap_score", 0)
        st.metric("Skill Gap", f"{gap_score:.1f}%")
    
    # Create tabs for detailed results
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🔍 Skill Gaps", "✅ Strengths", "⚠️ Areas of Concern"])
    
    with tab1:
        # Overall score chart
        score = overall.get('overall_score', 0)
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Score"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 70], 'color': "yellow"},
                    {'range': [70, 85], 'color': "orange"},
                    {'range': [85, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        skill_gaps = analysis_result.get("skill_gaps", {})
        missing_skills = skill_gaps.get("missing_technical_skills", [])
        
        if missing_skills:
            st.subheader("Missing Technical Skills")
            for skill in missing_skills:
                st.write(f"• {skill}")
        else:
            st.success("✅ No missing technical skills identified!")
    
    with tab3:
        strengths = overall.get("strengths", [])
        if strengths:
            st.subheader("Key Strengths")
            for strength in strengths:
                st.write(f"✅ {strength}")
        else:
            st.info("No specific strengths identified.")
    
    with tab4:
        weaknesses = overall.get("weaknesses", [])
        if weaknesses:
            st.subheader("Areas for Improvement")
            for weakness in weaknesses:
                st.write(f"⚠️ {weakness}")
        else:
            st.success("✅ No major areas of concern identified!")


def interview_section():
    """Interview scoring section."""
    st.header("🎤 Interview Scoring")
    
    if 'cv_analysis' in st.session_state:
        st.subheader("Generate Interview Questions")
        
        if st.button("❓ Generate Questions", type="secondary"):
            with st.spinner("Generating personalized interview questions..."):
                try:
                    jd_content = st.session_state.file_utils.read_file(st.session_state.jd_path)
                    questions = st.session_state.interview_scorer.generate_interview_questions(
                        jd_content, st.session_state.cv_analysis
                    )
                    
                    if "error" not in questions:
                        st.session_state.interview_questions = questions
                        st.success("✅ Interview questions generated!")
                        display_interview_questions(questions)
                    else:
                        st.error(f"❌ Question generation failed: {questions['error']}")
                        
                except Exception as e:
                    st.error(f"❌ Error generating questions: {str(e)}")
    
    # Manual interview scoring
    st.subheader("Score Interview Responses")
    
    col1, col2 = st.columns(2)
    
    with col1:
        question = st.text_area("Interview Question", height=100)
    
    with col2:
        response = st.text_area("Candidate Response", height=100)
    
    if question and response:
        if st.button("📊 Score Response", type="secondary"):
            with st.spinner("Scoring response..."):
                try:
                    score_result = st.session_state.interview_scorer.score_interview_response(
                        question, response
                    )
                    
                    if "error" not in score_result:
                        display_interview_score(score_result)
                    else:
                        st.error(f"❌ Scoring failed: {score_result['error']}")
                        
                except Exception as e:
                    st.error(f"❌ Error scoring response: {str(e)}")


def display_interview_questions(questions):
    """Display generated interview questions."""
    st.subheader("Generated Questions")
    
    if "technical_questions" in questions:
        st.write("**Technical Questions:**")
        for i, q in enumerate(questions["technical_questions"][:3], 1):
            with st.expander(f"Technical Question {i}"):
                st.write(f"**Question:** {q.get('question', 'N/A')}")
                st.write(f"**Purpose:** {q.get('purpose', 'N/A')}")
                st.write(f"**Difficulty:** {q.get('difficulty', 'N/A')}")
    
    if "behavioral_questions" in questions:
        st.write("**Behavioral Questions:**")
        for i, q in enumerate(questions["behavioral_questions"][:2], 1):
            with st.expander(f"Behavioral Question {i}"):
                st.write(f"**Question:** {q.get('question', 'N/A')}")
                st.write(f"**Purpose:** {q.get('purpose', 'N/A')}")


def display_interview_score(score_result):
    """Display interview scoring results."""
    st.subheader("Interview Score Results")
    
    overall_score = score_result.get("overall_score", 0)
    
    # Create metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Overall Score", f"{overall_score}/10")
    
    with col2:
        recommendation = score_result.get("recommendation", "Unknown")
        st.metric("Recommendation", recommendation.replace('_', ' ').title())
    
    with col3:
        confidence = score_result.get("confidence", 0)
        st.metric("Confidence", f"{confidence}%")
    
    # Criteria breakdown
    criteria_scores = score_result.get("criteria_scores", {})
    if criteria_scores:
        st.subheader("Criteria Breakdown")
        
        criteria_data = []
        for criteria, score in criteria_scores.items():
            criteria_data.append({
                "Criteria": criteria.replace('_', ' ').title(),
                "Score": score
            })
        
        df = pd.DataFrame(criteria_data)
        fig = px.bar(df, x="Criteria", y="Score", title="Interview Criteria Scores")
        st.plotly_chart(fig, use_container_width=True)
    
    # Strengths and weaknesses
    col1, col2 = st.columns(2)
    
    with col1:
        strengths = score_result.get("strengths", [])
        if strengths:
            st.subheader("Strengths")
            for strength in strengths:
                st.write(f"✅ {strength}")
    
    with col2:
        weaknesses = score_result.get("weaknesses", [])
        if weaknesses:
            st.subheader("Areas for Improvement")
            for weakness in weaknesses:
                st.write(f"⚠️ {weakness}")


def report_section():
    """Report generation section."""
    st.header("📋 Generate Report")
    
    if 'cv_analysis' in st.session_state:
        if st.button("📄 Generate Comprehensive Report", type="primary"):
            with st.spinner("Generating comprehensive report..."):
                try:
                    # Create mock interview scores for demonstration
                    mock_interview_scores = {
                        "overall_assessment": {
                            "overall_score": 7.5,
                            "performance_level": "good",
                            "recommendation": "hire"
                        }
                    }
                    
                    candidate_info = {
                        "name": "Uploaded Candidate",
                        "cv_file": "uploaded_cv",
                        "job_description": "uploaded_jd"
                    }
                    
                    report = st.session_state.report_generator.generate_comprehensive_report(
                        st.session_state.cv_analysis, mock_interview_scores, candidate_info
                    )
                    
                    if "error" not in report:
                        st.session_state.comprehensive_report = report
                        st.success("✅ Comprehensive report generated!")
                        display_comprehensive_report(report)
                    else:
                        st.error(f"❌ Report generation failed: {report['error']}")
                        
                except Exception as e:
                    st.error(f"❌ Error generating report: {str(e)}")
    else:
        st.info("📝 Please complete CV analysis first to generate a comprehensive report.")


def display_comprehensive_report(report):
    """Display comprehensive evaluation report."""
    st.subheader("Comprehensive Evaluation Report")
    
    # Executive summary
    structured_report = report.get("structured_report", {})
    executive_summary = structured_report.get("executive_summary", {})
    
    if executive_summary:
        overall_assessment = executive_summary.get("overall_assessment", {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            cv_score = overall_assessment.get("cv_score", 0)
            st.metric("CV Score", f"{cv_score:.1f}/100")
        
        with col2:
            interview_score = overall_assessment.get("interview_score", 0)
            st.metric("Interview Score", f"{interview_score:.1f}/10")
        
        with col3:
            overall_score = overall_assessment.get("overall_score", 0)
            st.metric("Overall Score", f"{overall_score:.1f}/100")
        
        with col4:
            final_rec = executive_summary.get("final_recommendation", "Unknown")
            st.metric("Final Recommendation", final_rec.replace('_', ' ').title())
    
    # Display summary report
    summary_report = report.get("summary_report", "")
    if summary_report:
        st.subheader("Summary Report")
        st.markdown(summary_report)


def sidebar():
    """Sidebar with navigation and information."""
    st.sidebar.title("🎯 Navigation")
    
    page = st.sidebar.selectbox(
        "Choose a section:",
        ["📁 Upload Files", "📊 CV Analysis", "🎤 Interview Scoring", "📋 Generate Report"]
    )
    
    st.sidebar.markdown("---")
    
    st.sidebar.subheader("ℹ️ About")
    st.sidebar.markdown("""
    This system provides AI-powered candidate evaluation using:
    - **CV Analysis**: Skill gap identification
    - **Interview Scoring**: Response evaluation
    - **Comprehensive Reports**: Detailed assessments
    
    Built with open-source Hugging Face models.
    """)
    
    st.sidebar.markdown("---")
    
    st.sidebar.subheader("📊 System Status")
    if 'cv_analyzer' in st.session_state:
        st.sidebar.success("✅ CV Analyzer Ready")
    else:
        st.sidebar.error("❌ CV Analyzer Not Ready")
    
    if 'interview_scorer' in st.session_state:
        st.sidebar.success("✅ Interview Scorer Ready")
    else:
        st.sidebar.error("❌ Interview Scorer Not Ready")
    
    if 'report_generator' in st.session_state:
        st.sidebar.success("✅ Report Generator Ready")
    else:
        st.sidebar.error("❌ Report Generator Not Ready")
    
    return page


def main():
    """Main application function."""
    setup_page()
    initialize_components()
    
    # Get current page from sidebar
    page = sidebar()
    
    # Display content based on selected page
    if page == "📁 Upload Files":
        upload_section()
    elif page == "📊 CV Analysis":
        cv_analysis_section()
    elif page == "🎤 Interview Scoring":
        interview_section()
    elif page == "📋 Generate Report":
        report_section()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Candidate Evaluation System | Built with Streamlit and Hugging Face"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
