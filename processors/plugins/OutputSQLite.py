# Standard Library
import sqlite3
from dataclasses import fields
from functools import cached_property
from typing import Any, Dict, List

# First Party
from processors import ResultSet, hookimpl_processor
from processors.dataModels import BaseResultData
from seotool.crawl import Crawler


class SQLite:
    tables: List[str] = []

    def __init__(self, file="sqlite.db"):
        self.file = file

    def __enter__(self):
        self.connection = sqlite3.connect(self.file)

        return self

    def __exit__(self, type, value, traceback):
        self.connection.close()
        self.connection = None

    def _get_sql_type(self, python_type: Any) -> str:
        field_mappings: Dict[Any, str] = {
            str: "TEXT",
            int: "INTEGER",
        }

        try:
            field_type = field_mappings[python_type]
        except KeyError:
            field_type = field_mappings[str]

        return field_type

    def _build_table_sql(self, dataclass: BaseResultData) -> str:
        sql_fields = [
            "_id INTEGER PRIMARY KEY AUTOINCREMENT",
            "_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        ]

        for field in fields(dataclass):
            field_type = self._get_sql_type(field.type)
            sql_fields.append(f"{field.name} {field_type} NOT NULL")

        return f"CREATE TABLE IF NOT EXISTS {dataclass.name} ({','.join(sql_fields)});"

    def save(self, dataclass: BaseResultData):
        if dataclass.name not in self.tables:
            table_sql = self._build_table_sql(dataclass)

            self.connection.execute(table_sql)
            self.tables.append(dataclass.name)

        with self.connection:
            data_fields = fields(dataclass)
            sql_fields = ", ".join(f.name for f in data_fields)
            sql_values = ", ".join("?" for _ in data_fields)
            sql = f"INSERT INTO {dataclass.name}({sql_fields}) VALUES ({sql_values})"
            data = [f"{dataclass[f.name]}" for f in data_fields]
            self.connection.execute(sql, data)


class OutputSQLite:
    def __init__(self, crawler: Crawler) -> None:
        self.crawler = crawler

        self.storage = SQLite(self.file)

    @cached_property
    def file(self) -> str:
        try:
            return self.crawler.get_output_name("results", "db")
        except AttributeError:
            return ":memory:"

    @hookimpl_processor()
    def process_output(self, resultsSets: List[ResultSet]) -> None:
        with self.storage as storage:
            for resultSet in resultsSets:
                if not resultSet.has_data:
                    continue

                for d in resultSet.data:
                    storage.save(d)
