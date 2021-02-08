#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name="seotool",
    version="1.0",
    packages=find_packages(),
    scripts=["crawl.py"],
    install_requires=[
        "beautifulsoup4",
        "Click",
        "pdfkit",
        "requests",
        "urllib3",
        "Markdown",
    ],
)
