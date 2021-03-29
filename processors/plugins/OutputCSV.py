import csv
import os
from typing import List

from processors import ResultSet, hookimpl_processor
from seotool.crawl import Crawler


class OutputCSV:
    def __init__(self, crawler: Crawler) -> None:
        self.crawler = crawler

    @hookimpl_processor
    def process_output(self, resultsSets: List[ResultSet]):
        self.crawler.print("Writing CSVs")

        filenames_seen = []
        for result_set in resultsSets:
            filename = "".join(c for c in result_set.title if c.isalpha() or c.isdigit() or c == "-").rstrip()
            while filename in filenames_seen:
                filename += "-duplicate-name"
            filenames_seen.append(filename)
            path = os.path.join(self.crawler.results_base_path, f"{filename}.csv")

            with open(path, "w") as f:
                if result_set.data is None or len(result_set.data) == 0:
                    continue

                w = csv.DictWriter(f, result_set.data_headers)
                w.writeheader()

                for row in result_set.data_flat_dict:
                    w.writerow(row)
