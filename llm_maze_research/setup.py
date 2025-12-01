"""Setup configuration for LLM maze research framework."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="llm-maze-research",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Research framework for studying LLM overreliance on external tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/llm_maze_research",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    install_requires=[
        "gymnasium>=0.29.0",
        "numpy>=1.24.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "langchain>=0.1.0",
        "langchain-openai>=0.0.1",
        "langchain-anthropic>=0.0.1",
        "openai>=1.0.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "httpx>=0.25.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.13.0",
        "jupyter>=1.0.0",
        "pytest>=7.4.0",
        "structlog>=23.2.0",
    ],
    extras_require={
        "dev": [
            "black>=23.11.0",
            "ruff>=0.1.0",
            "mypy>=1.7.0",
            "pytest-asyncio>=0.21.0",
        ]
    },
)
