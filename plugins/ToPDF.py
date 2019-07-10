from markdown import markdown
import pdfkit
import re
import os

class ToPDF:
    def __init__(self, crawler):
        self.crawler = crawler

    def process_results(self, results):
        text = "#SEO Results"
        for block in results:
            title = re.sub('(?<!^)([A-Z0-9]+)', ' \\1', block)
            text = f"{text}\n\n##{title}\n"

            cols = max([len(r) for r in results[block]])
            table = ""
            headdings = []
            for i, row in enumerate(results[block]):
                text = f"{text}\n| {' | '.join(row[:5])} | {'   |' * (cols - len(row))}"
                if i == 0:
                    text = f"{text}\n|{'---|' * cols}"

        html = markdown(text, output_format='html4', extensions=['tables'])
        report_path = os.path.join(self.crawler.results_base_path, f'report-for-{self.crawler.base_netloc}.pdf')
        pdfkit.from_string(html, report_path)
        self.crawler.print(f"Saved pdf report to {report_path}")
