# Standard Library
import os
from typing import Callable

# Third Party
import click
from click.decorators import FC
from jinja2 import Environment, FileSystemLoader, Template

# First Party
from processors import ResultSet, hookimpl_processor
from seotool.crawl import Crawler


class OutputHTML:
    def __init__(self, crawler: Crawler, html_template: str | None = None) -> None:
        self.crawler = crawler
        self.template = html_template

    @hookimpl_processor
    def process_output(self, resultsSets: list[ResultSet]) -> None:
        self.crawler.print("Writing HTML")

        path = self.crawler.get_output_name("report", "html")
        data = {"url": self.crawler.base_url, "results_sets": resultsSets, "styles": self.get_styles()}

        if self.template is not None:
            loader = FileSystemLoader(searchpath=os.getcwd())
            templateEnv = Environment(loader=loader)
            template = templateEnv.get_template(self.template)
        else:
            template = Template(self.get_template())

        with open(path, "w") as f:
            f.write(template.render(**data))

    @hookimpl_processor
    def get_options(self) -> list[Callable[[FC], FC]]:
        return [
            click.option("--html-template", default=None, help="Jinja template used to render the report"),
        ]

    def get_template(self) -> str:
        return """
<html>
<head>
    <title>SEO Report for {{ url }}</title>
    <style>{{ styles }}</style>
</head>
<body>
    <h1>SEO Report for {{ url }}</h1>
    {% for results_set in results_sets %}
        <div>
            <h2>{{ results_set.title }}</h2>
            <p>{{ results_set.body }}<p>
            {% if results_set.has_data %}
            <table>
                <thead>
                    <tr>
                        {% for val in results_set.data_headers %}
                        <th>{{ val }}</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for row in results_set.data_list %}
                        <tr>
                        {% for val in row %}
                            <td>{{ val }}</td>
                        {% endfor %}
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
                <p>No issues found</p>
            {% endif %}
        </div>
    {% endfor %}
</body>
</html>
"""

    def get_styles(self) -> str:
        return """
@page {
    margin: 1cm;
}
html {
    font-size: 12px;
}
body {
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        Segoe UI,
        Helvetica,
        Arial,
        sans-serif,
        Apple Color Emoji,
        Segoe UI Emoji,
        Segoe UI Symbol;
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
