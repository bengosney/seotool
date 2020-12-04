from markdown import markdown
import pdfkit
import re
import os

CSS = """
@page {
    margin: 1cm;
}

html {
    font-size: 12px;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif, Apple Color Emoji, Segoe UI Emoji, Segoe UI Symbol;
    font-weight: 400;
    line-height: 1.45
}

p {
    margin-bottom: 1.25em;
}

h1, h2, h3, h4, h5 {
    margin: 2.75rem 0 1rem;
    font-weight: 400;
    line-height: 1.15;
}

h1 {
    margin-top: 0;
    font-size: 3.052em;
}

h2 {
    font-size: 2.441em;
}

h3 {
    font-size: 1.953em;
}

h4 {
    font-size: 1.563em;
}

h5 {
    font-size: 1.25em;
}

small, .text_small {
    font-size: 0.8em;
}

table {
    width: 100%;
    border-collapse: collapse;
}

table td, table th {
    border: 1px solid #000000;
    padding: .5em 1em;
}

table tr:nth-child(even) {
    background: #D0E4F5;
}

table thead {
    background: #CFCFCF;
    border-bottom: 3px solid #000000;
}

table thead th {
    font-size: 1.2em;
    font-weight: bold;
    text-align: left;
}

table tfoot {
    font-weight: bold;
    color: #000000;
    border-top: 3px solid #000000;
}

table tfoot td {
    font-size: 14px;
}
"""


class ToPDF:
    def __init__(self, crawler):
        self.crawler = crawler

    def process_results(self, results):
        text = "#SEO Results"
        for block in results:
            try:
                title = re.sub("(?<!^)([A-Z0-9]+)", " \\1", block)
                
                if title in ["Link Map", "External Links Per Page"]:
                    continue

                text = f"{text}\n\n##{title}\n"
                if len(results[block]) > 1:
                    cols = max([len(r) for r in results[block]])
                    table = ""
                    headdings = []
                    for i, row in enumerate(results[block]):
                        text = f"{text}\n| {' | '.join(row[:5])} | {'   |' * (cols - len(row))}"
                        if i == 0:
                            text = f"{text}\n|{'---|' * cols}"
                else:
                    text = f"{text}\nNo issues found"
            except:
                pass

        report_html = markdown(text, output_format="html5", extensions=["tables"])
        html = (
            f"<html><head><style>{CSS}</style></head><body>{report_html}</body></html>"
        )
        with open(
            os.path.join(
                self.crawler.results_base_path,
                f"report-for-{self.crawler.base_netloc}.html",
            ),
            "w",
        ) as f:
            f.write(html)
        report_path = os.path.join(
            self.crawler.results_base_path, f"report-for-{self.crawler.base_netloc}.pdf"
        )
        pdfkit.from_string(html, report_path)
        self.crawler.print(f"Saved pdf report to {report_path}")
