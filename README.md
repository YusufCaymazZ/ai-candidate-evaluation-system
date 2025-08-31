# AI-Powered Candidate Evaluation System

A comprehensive AI-powered candidate evaluation platform that automates CV analysis, interview scoring, and candidate assessment using open-source language models.

## 🎯 Project Overview

This system demonstrates a complete candidate evaluation pipeline for AI-powered recruitment platforms:

- **CV Analysis**: Automated gap analysis between candidate CVs and job requirements
- **Interview Scoring**: AI-conducted text-based interviews with structured evaluation
- **Candidate Assessment**: Comprehensive scoring and recommendation generation
- **Web Interface**: Interactive Streamlit application for real-time evaluation

## 🏗️ Architecture

```
candidate-evaluation-system/
├── README.md                           # Project documentation
├── requirements.txt                    # Python dependencies
├── setup.py                           # Package configuration
├── web_interface.py                   # Streamlit web application
├── config/
│   └── config.yaml                    # System configuration
├── data/
│   ├── cv_samples/                     # Sample CV files
│   ├── job_descriptions/              # Sample job descriptions
│   ├── interview_questions/           # Question templates
│   └── sample_responses/              # Simulated candidate answers
├── src/
│   ├── models/
│   │   └── llm_client.py              # Hugging Face model interface
│   ├── utils/
│   │   ├── file_utils.py              # File handling utilities
│   │   └── prompt_templates.py        # LLM prompt templates
│   └── evaluation/
│       ├── cv_analyzer.py             # CV analysis logic
│       ├── interview_scorer.py        # Interview scoring logic
│       └── report_generator.py        # Report generation
├── scripts/
│   ├── cv_analysis_runner.py          # CV analysis script
│   ├── interview_scoring_runner.py    # Interview scoring script
│   └── complete_evaluation_runner.py  # Complete workflow script
└── tests/
    └── test_evaluation_system.py      # Unit tests
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd candidate-evaluation-system

# Install dependencies
pip install -r requirements.txt
```

### 2. Model Setup

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

# Download and cache the model (first time only)
model_name = "mistralai/Mistral-7B-Instruct-v0.2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
```

### 3. Run the Application

```bash
# Web interface
streamlit run web_interface.py

# Or run individual scripts
python scripts/cv_analysis_runner.py
python scripts/interview_scoring_runner.py
python scripts/complete_evaluation_runner.py
```

## 🔧 Key Features

### 🤖 AI-Powered Evaluation
- **Open Source Models**: Uses Hugging Face models (Mistral-7B, DialoGPT)
- **Prompt Engineering**: Optimized prompts for consistent evaluation
- **Multi-Model Support**: Fallback mechanisms and model benchmarking

### 📊 Comprehensive Analysis
- **CV Gap Analysis**: Skill matching and experience assessment
- **Interview Scoring**: Multi-criteria evaluation with detailed feedback
- **Structured Output**: JSON and Markdown reports for easy integration

### 🌐 Web Interface
- **Interactive UI**: Streamlit-based web application
- **Real-time Processing**: Upload and evaluate candidates instantly
- **Visual Reports**: Charts and tables for easy interpretation

### 🧪 Testing & Quality
- **Unit Tests**: Comprehensive test coverage
- **Error Handling**: Robust error management and logging
- **Modular Design**: Easy to extend and maintain

## 📋 System Requirements

- **Python**: 3.8+
- **RAM**: Minimum 8GB (16GB recommended)
- **GPU**: Optional, 4GB+ VRAM for acceleration
- **Storage**: 10GB+ for model caching

## 🎯 Use Cases

### For HR Teams
- **High-Volume Screening**: Process hundreds of CVs automatically
- **Bias Reduction**: Structured evaluation criteria
- **Time Savings**: 5x faster candidate processing

### For Recruiters
- **Consistent Evaluation**: Standardized scoring across candidates
- **Detailed Insights**: Comprehensive gap analysis and recommendations
- **Integration Ready**: JSON outputs for existing ATS systems

### For AI Researchers
- **Model Benchmarking**: Compare different LLM performance
- **Prompt Optimization**: Test and refine evaluation prompts
- **Custom Evaluation**: Extensible scoring criteria

## 🔍 Technical Details

### Model Architecture
- **Primary**: Mistral-7B-Instruct-v0.2 (instruction-tuned)
- **Fallback**: DialoGPT-medium (conversational)
- **Optimization**: GPU acceleration with CPU fallback

### Evaluation Criteria
- **Technical Skills**: Programming languages, frameworks, tools
- **Experience Level**: Years of experience, project complexity
- **Communication**: Clarity, completeness, relevance
- **Cultural Fit**: Alignment with company values and team dynamics

### Output Formats
- **JSON**: Structured data for API integration
- **Markdown**: Human-readable reports
- **Streamlit**: Interactive web interface

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

MIT License - Feel free to use and modify for your needs.

## 🔗 Related Projects

This project demonstrates skills relevant to:
- **AI Research Internships**
- **HR Tech Development**
- **LLM Application Development**
- **Prompt Engineering**
- **Model Benchmarking**

---

**Built with ❤️ for AI-powered recruitment**
