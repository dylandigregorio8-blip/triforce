from regex_detector import regex_detector


def test_simple_email():
    assert regex_detector("Write to ada@example.com please.") == ["ada@example.com"]


def test_tagged_and_subdomain_email():
    assert regex_detector("first.last+tag@sub.domain.org") == [
        "first.last+tag@sub.domain.org"
    ]


def test_invalid_email_fragments_are_ignored():
    assert regex_detector("user@ and @domain.com are incomplete.") == []


def test_emails_fixture_file(load_document):
    document = load_document("emails.txt")
    assert regex_detector(document) == [
        "ada@example.com",
        "first.last+tag@sub.domain.org",
    ]
