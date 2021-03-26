import csv
import os
from typing import List

from processors import ResultSet, hookimpl_output_processor
from seotool.crawl import Crawler


class OutputCSV:
    def __init__(self, crawler: Crawler) -> None:
        self.crawler = crawler

    @hookimpl_output_processor
    def process_output(self, resultsSets: List[ResultSet]):
        self.crawler.print("Writing CSVs")

        for result_set in resultsSets:
            filename = "".join(c for c in result_set.title if c.isalpha() or c.isdigit() or c == "-").rstrip()
            path = os.path.join(self.crawler.results_base_path, f"{filename}.csv")

            with open(path, "w") as f:
                if result_set.data is None:
                    continue

                w = csv.DictWriter(f, result_set.data[0].keys())
                w.writeheader()
                for row in result_set.data:
                    w.writerow(row)
