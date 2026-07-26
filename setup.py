"""Setup for mdtrace — Molecular Dynamics Trace."""
from setuptools import setup, find_packages

setup(
    name="mdtrace",
    version="1.0.0",
    description="Molecular Dynamics Trace — trace the physics inside your MD trajectory",
    author="Ting Liang",
    author_email="liangting.zj@gmail.com",
    url="https://github.com/Tingliangstu/mdtrace",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "netCDF4",
        "matplotlib",
        "seaborn",
        "psutil",
    ],
    extras_require={
        "cupy": ["cupy"],
    },
    entry_points={
        "console_scripts": [
            "mdtrace=mdtrace.main:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Physics",
    ],
)
