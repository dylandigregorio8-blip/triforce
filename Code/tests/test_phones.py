from regex_detector import regex_detector


def test_international_phone():
    assert regex_detector("Call +1 (415) 555-2671 now.") == ["+1 (415) 555-2671"]


def test_european_phone():
    assert regex_detector("Call +33 1 23 45 67 89 or 06 12 34 56 78.") == [
        "+33 1 23 45 67 89",
        "06 12 34 56 78",
    ]


def test_dashed_and_parenthetical_us_phones():
    assert regex_detector("415-555-2671 or (202) 555-0134") == [
        "415-555-2671",
        "(202) 555-0134",
    ]


def test_phones_fixture_file(load_document):
    document = load_document("phones.txt")
    assert regex_detector(document) == [
        "+1 (415) 555-2671",
        "415-555-2671",
        "(202) 555-0134",
        "+33 1 23 45 67 89",
        "06 12 34 56 78",
    ]
