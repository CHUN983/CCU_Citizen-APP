"""
Citizen Urban Planning Participation System - Python Package Setup
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the requirements from requirements.txt
requirements_path = Path(__file__).parent.parent.parent / "requirements.txt"

def read_requirements():
    """Read requirements from requirements.txt"""
    try:
        with open(requirements_path, 'r', encoding='utf-8') as f:
            requirements = []
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    requirements.append(line)
            return requirements
    except FileNotFoundError:
        # Fallback to hardcoded requirements if file not found
        return [
            "fastapi>=0.109.0",
            "uvicorn[standard]>=0.27.0",
            "pydantic>=2.5.3",
            "pydantic[email]>=2.5.3",
            "mysql-connector-python>=8.3.0",
            "sqlalchemy>=2.0.25",
            "bcrypt>=4.1.2",
            "PyJWT>=2.8.0",
            "python-multipart>=0.0.6",
            "python-dotenv>=1.0.0",
            "Pillow>=10.2.0",
            "pytest>=7.4.4",
            "pytest-asyncio>=0.23.3",
            "pytest-cov>=4.1.0",
            "pytest-html>=4.1.1",
            "httpx>=0.26.0",
            "openai>=0.27.8",
            "requests>=2.31.0",
        ]

setup(
    name="citizenapp",
    version="1.0.0",
    description="Citizen Urban Planning Participation System - Backend API",
    author="V&V Team",
    author_email="dev@citizenapp.example.com",
    python_requires=">=3.10",

    # Package discovery
    packages=find_packages(exclude=["tests", "tests.*"]),

    # Package data
    include_package_data=True,

    # Dependencies
    install_requires=read_requirements(),

    # Entry points (optional - for CLI commands)
    entry_points={
        'console_scripts': [
            # 'citizenapp-server=core.app:main',  # Uncomment if you have a main() function
        ],
    },

    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: FastAPI",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],

    # Additional metadata
    project_urls={
        "Source": "https://github.com/your-org/citizenApp",
        "Documentation": "https://github.com/your-org/citizenApp/docs",
    },
)
