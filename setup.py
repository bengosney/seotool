#!/usr/bin/env python
# Third Party
from setuptools import find_packages, setup

setup(
    name="seotool",
    version="2.0.0",
    packages=find_packages(),
    python_requires="~=3.8",
    install_requires=[
        "beautifulsoup4",
        "click",
        "rich",
        "markdown",
        "pdfkit",
        "pyppeteer",
        "requests",
        "pluggy",
        "Jinja2",
    ],
    entry_points={
        # "seo_processor": ["search=processors.plugins.IgnoreSearchPages"]
        "console_scripts": ["seo-crawl=seotool.cli:main"],
        "seo_engines": [
            "pyppeteer=engines.pyppeteer:pyppeteer",
            "requests=engines.requests:requests",
        ],
    },
)
