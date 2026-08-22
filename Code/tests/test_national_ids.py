from regex_detector import regex_detector


def test_swiss_ahv():
    assert regex_detector("Swiss AHV/AVS number is 756.9217.0769.85 in document.") == [
        "756.9217.0769.85"
    ]


def test_us_ssn():
    assert regex_detector("SSN: 123-45-6789 and another 987-65-4321.") == [
        "123-45-6789",
        "987-65-4321",
    ]


def test_invalid_national_ids():
    assert regex_detector("Wrong AHV prefix: 755.1234.5678.90") == []
    assert regex_detector("Wrong SSN length: 12-345-6789") == []
