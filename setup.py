#!/usr/bin/env python3
"""
Setup script for Airborne Radar Target Behavior Analysis System
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="radar-target-analyzer",
    version="1.0.0",
    author="Radar Analysis Team",
    description="Airborne Radar Target Behavior Analysis and Synthetic Data Generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "pandas>=2.0.0",
        "PyQt5>=5.15.9",
        "matplotlib>=3.7.0",
        "h5py>=3.8.0",
        "pillow>=9.5.0",
        "cffi>=1.15.1",
        "scikit-learn>=1.2.0",
        "pyyaml>=6.0",
        "colorlog>=6.7.0",
    ],
    extras_require={
        "dev": ["pytest>=7.3.0", "pytest-cov>=4.0.0"],
    },
    entry_points={
        "console_scripts": [
            "radar-analyzer=radar_analyzer.main:main",
        ],
    },
)
