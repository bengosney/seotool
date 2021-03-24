#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name="seotool",
    version="1.0",
    packages=find_packages(),
    python_requires="~=3.7",
    install_requires=[
        "beautifulsoup4",
        "click",
        "markdown",
        "pdfkit",
        "pyppeteer",
        "requests",
        "pyqt5",
        "pyqt5-tools",
    ],
    entry_points={
        "console_scripts": ["seo-crawl=seotool.cli:main"],
    },
)
