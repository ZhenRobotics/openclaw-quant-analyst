from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="openclaw-quant-analyst",
    version="0.1.0",
    author="ZhenStaff",
    author_email="contact@zhenrobotics.com",
    description="Professional quantitative trading system for cryptocurrency markets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZhenRobotics/openclaw-quant-analyst",
    project_urls={
        "Bug Tracker": "https://github.com/ZhenRobotics/openclaw-quant-analyst/issues",
        "ClawHub": "https://clawhub.ai/ZhenStaff/quant-analyst",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "openclaw-quant-analyst=openclaw_quant.cli:main",
        ],
    },
    keywords=[
        "quantitative-trading",
        "backtesting",
        "cryptocurrency",
        "trading-bot",
        "algorithmic-trading",
        "strategy-optimization",
        "technical-analysis",
    ],
)
