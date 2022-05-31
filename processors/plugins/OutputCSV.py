# Standard Library
import csv

# First Party
from processors import ResultSet, hookimpl_processor
from seotool.crawl import Crawler


class OutputCSV:
    def __init__(self, crawler: Crawler) -> None:
        self.crawler = crawler

    @hookimpl_processor
    def process_output(self, resultsSets: list[ResultSet]):
        self.crawler.print("Writing CSVs")

        for result_set in resultsSets:
            path = self.crawler.get_output_name(result_set.title, "csv", "csv")

            with open(path, "w") as f:
                if result_set.data is None or len(result_set.data) == 0:
                    continue

                w = csv.DictWriter(f, result_set.data_headers)
                w.writeheader()

                for row in result_set.data_flat_dict:
                    w.writerow(row)
