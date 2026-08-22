from regex_detector import regex_detector


def test_iso_date():
    assert regex_detector("Signed on 2024-08-21.") == ["2024-08-21"]


def test_numeric_date_slash_and_dot():
    assert regex_detector("Due 21/08/2024 and 21.08.24.") == ["21/08/2024", "21.08.24"]


def test_month_name_dates():
    assert regex_detector("August 21, 2024 and 21st January 2025") == [
        "August 21, 2024",
        "21st January 2025",
    ]


def test_dates_fixture_file(load_document):
    document = load_document("dates.txt")
    assert regex_detector(document) == [
        "2024-08-21",
        "21/08/2024",
        "August 21, 2024",
        "21st January 2025",
    ]
