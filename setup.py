#!/usr/bin/env python3
"""
Setup script for Candidate Evaluation System

This script helps users set up the candidate evaluation system by:
1. Installing dependencies
2. Creating necessary directories
3. Downloading sample data
4. Testing the installation
"""

import os
import sys
import subprocess
from pathlib import Path


def print_banner():
    """Print setup banner."""
    print("=" * 60)
    print("🎯 CANDIDATE EVALUATION SYSTEM SETUP")
    print("=" * 60)
    print()


def check_python_version():
    """Check if Python version is compatible."""
    print("🔍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating directories...")
    
    directories = [
        "data/cv_samples",
        "data/job_descriptions",
        "data/interview_questions",
        "data/sample_responses",
        "outputs/cv_analysis_results",
        "outputs/interview_scores",
        "outputs/final_reports",
        "logs",
        "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created: {directory}")
    
    print("✅ All directories created")


def create_sample_data():
    """Create sample data for testing."""
    print("\n📝 Creating sample data...")
    
    try:
        # Use subprocess to run the script that creates sample data
        # This avoids import issues with relative imports
        sample_data_script = """
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from src.utils.file_utils import FileUtils

file_utils = FileUtils()
file_utils.create_sample_data()
print("Sample data created successfully")
"""
        
        # Write temporary script
        temp_script = Path("temp_create_sample_data.py")
        temp_script.write_text(sample_data_script)
        
        # Run the script
        result = subprocess.run([
            sys.executable, str(temp_script)
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        # Clean up
        temp_script.unlink(missing_ok=True)
        
        if result.returncode == 0:
            print("✅ Sample data created successfully")
            return True
        else:
            print(f"❌ Failed to create sample data: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        return False


def test_installation():
    """Test the installation by running a simple analysis."""
    print("\n🧪 Testing installation...")
    
    try:
        # Use subprocess to run the test script
        # This avoids import issues with relative imports
        test_script = """
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from src.evaluation.cv_analyzer import CVAnalyzer
from src.utils.file_utils import FileUtils

# Initialize components
cv_analyzer = CVAnalyzer()
file_utils = FileUtils()

# Get sample files
cv_files = file_utils.get_cv_samples()
jd_files = file_utils.get_job_descriptions()

if not cv_files or not jd_files:
    print("Sample data not found")
    sys.exit(1)

# Run a simple test
print("Running test analysis...")
result = cv_analyzer.analyze_cv_against_job(cv_files[0], jd_files[0])

if "error" not in result:
    print("Test analysis completed successfully")
    sys.exit(0)
else:
    print(f"Test analysis failed: {result['error']}")
    sys.exit(1)
"""
        
        # Write temporary script
        temp_script = Path("temp_test_installation.py")
        temp_script.write_text(test_script)
        
        # Run the script
        result = subprocess.run([
            sys.executable, str(temp_script)
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        # Clean up
        temp_script.unlink(missing_ok=True)
        
        if result.returncode == 0:
            print("✅ Test analysis completed successfully")
            return True
        else:
            print(f"❌ Test analysis failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    print("\n📋 NEXT STEPS:")
    print("1. Run Day 1 demo: python scripts/day1_cv_analysis.py")
    print("2. Run Day 2 demo: python scripts/day2_interview_scoring.py")
    print("3. Run Day 3 demo: python scripts/day3_complete_workflow.py")
    print("4. Launch Streamlit UI: streamlit run streamlit_app.py")
    
    print("\n📚 DOCUMENTATION:")
    print("- README.md: Project overview and setup instructions")
    print("- config/config.yaml: Configuration settings")
    print("- outputs/: Generated analysis results")
    
    print("\n🔧 CUSTOMIZATION:")
    print("- Add your CVs to data/cv_samples/")
    print("- Add job descriptions to data/job_descriptions/")
    print("- Modify config/config.yaml for your needs")
    print("- Customize evaluation criteria in src/evaluation/")
    
    print("\n💡 TIPS:")
    print("- The system uses open-source Hugging Face models")
    print("- First run may take longer to download models")
    print("- Check logs/ directory for detailed logs")
    print("- Use smaller models for faster processing")


def main():
    """Main setup function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create sample data
    if not create_sample_data():
        print("\n❌ Setup failed at sample data creation")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("\n❌ Setup failed at installation test")
        print("   You may need to manually download models or check your internet connection")
        sys.exit(1)
    
    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main()
