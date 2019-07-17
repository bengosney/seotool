from markdown import markdown
import pdfkit
import re
import os

CSS = """
@page {
  margin: 1cm;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif, Apple Color Emoji, Segoe UI Emoji, Segoe UI Symbol;
    font-weight: 400;
    line-height: 1.45
}
"""

class ToPDF:
    def __init__(self, crawler):
        self.crawler = crawler

    def process_results(self, results):
        text = "#SEO Results"
        for block in results:
            try:
                title = re.sub('(?<!^)([A-Z0-9]+)', ' \\1', block)
                text = f"{text}\n\n##{title}\n"
            
                cols = max([len(r) for r in results[block]])
                table = ""
                headdings = []
                for i, row in enumerate(results[block]):
                    text = f"{text}\n| {' | '.join(row[:5])} | {'   |' * (cols - len(row))}"
                    if i == 0:
                        text = f"{text}\n|{'---|' * cols}"
            except:
                pass

        report_html = markdown(text, output_format='html5', extensions=['tables'])
        html = f"<html><head><style>{CSS}</style></head><body>{report_html}</body></html>"
        with open(os.path.join(self.crawler.results_base_path, f'report-for-{self.crawler.base_netloc}.html'), 'w') as f:
            f.write(html)
        report_path = os.path.join(self.crawler.results_base_path, f'report-for-{self.crawler.base_netloc}.pdf')
        pdfkit.from_string(html, report_path)
        self.crawler.print(f"Saved pdf report to {report_path}")
