#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name="seotool",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4",
        "click",
        "markdown",
        "pdfkit",
        "pyppeteer",
        "requests",
    ],
    entry_points={
        "console_scripts": ["seo-crawl=cli:main"],
    },
)
