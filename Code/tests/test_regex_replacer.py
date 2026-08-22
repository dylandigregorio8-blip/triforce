from regex_detector import REGEX_CONFIG, regex_detector


def test_empty_document():
    assert regex_detector("") == []


def test_document_with_no_matches(load_document):
    assert regex_detector(load_document("none.txt")) == []


def test_mixed_document_preserves_left_to_right_order(load_document):
    assert regex_detector(load_document("mixed.txt")) == [
        "2024-08-21",
        "ada@example.com",
        "415-555-2671",
        "4111-1111-1111-1111",
    ]


def test_overlapping_matches_are_reported_once():
    matches = regex_detector("Call 415-555-2671")
    assert matches == ["415-555-2671"]


def test_config_covers_required_categories():
    assert set(REGEX_CONFIG) == {"date", "emails", "accounts", "phone_numbers"}
    assert all(REGEX_CONFIG[category] for category in REGEX_CONFIG)
