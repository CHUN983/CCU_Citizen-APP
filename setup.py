"""
Setup script for citizenApp Python backend
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="citizenapp",
    version="1.0.0",
    description="Citizen Urban Planning Participation System - Python Backend",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="citizenApp Team",
    python_requires=">=3.10",

    # 指定包的位置
    package_dir={"": "src/main/python"},
    packages=find_packages(where="src/main/python"),

    # 依賴
    install_requires=requirements,

    # 額外的依賴組
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-asyncio>=0.23.3",
            "pytest-cov>=4.1.0",
            "pytest-html>=4.1.1",
        ],
    },

    # 包含非 Python 文件
    include_package_data=True,

    # 分類
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
)
