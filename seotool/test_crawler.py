# Third Party
import pytest

# First Party
from seotool.crawl import Crawler
from seotool.exceptions import SkipPage


def test_clean_name_no_change():
    name = "bob"
    cleaned_name = Crawler._clean_filename(name)
    assert name == cleaned_name


def test_clean_name_changes():
    name = "-bOb:: '#' ::dOd-"
    cleaned_name = Crawler._clean_filename(name)
    assert cleaned_name == "bob-dod"


def test_skip_page():
    c = Crawler("localhost")
    with pytest.raises(SkipPage):
        c.skip_page()
