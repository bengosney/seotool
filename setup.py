#!/usr/bin/env python
# Third Party
from setuptools import find_packages, setup

setup(
    name="seotool",
    version="2.2.1",
    packages=find_packages(),
    python_requires="~=3.10",
    install_requires=[
        "Jinja2",
        "beautifulsoup4",
        "click",
        "markdown",
        "pdfkit",
        "playwright",
        "pluggy",
        "pygments",
        "requests",
        "rich",
    ],
    entry_points={
        "console_scripts": ["seo-crawl=seotool.cli:main"],
        "seo_engines": [
            "playwright=engines.playwright:playwright",
            "pyppeteer=engines.pyppeteer:pyppeteer",
            "requests=engines.requests:requests",
        ],
    },
)
