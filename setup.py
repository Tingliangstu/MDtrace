"""Setup for mdtrace — Molecular Dynamics Trace."""

from pathlib import Path

from setuptools import find_packages, setup


ROOT = Path(__file__).parent

setup(
    name="mdtrace",
    version="1.0.0",
    description="Molecular Dynamics Trace — trace the physics inside your MD trajectory",
    long_description=(ROOT / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Ting Liang",
    author_email="liangting.zj@gmail.com",
    url="https://github.com/Tingliangstu/mdtrace",
    packages=find_packages(exclude=("tests", "tests.*")),
    install_requires=[
        "numpy",
        "scipy",
        "netCDF4",
        "matplotlib",
        "seaborn",
    ],
    entry_points={
        "console_scripts": [
            "mdtrace=mdtrace.main:main",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Physics",
    ],
)
