from regex_detector import regex_detector
from replace import replace, restore


def test_empty_document_and_no_identifiers():
    assert replace([], "") == ("", [])
    assert replace([], "nothing to mask") == ("nothing to mask", [])
    assert replace(["ada@example.com"], "") == ("", [("ada@example.com", "<ID_1>")])


def test_single_identifier_is_replaced():
    document = "Write to ada@example.com please."
    redacted, mapping = replace(["ada@example.com"], document)

    assert redacted == "Write to <ID_1> please."
    assert mapping == [("ada@example.com", "<ID_1>")]


def test_repeated_identifier_reuses_the_same_tag():
    document = "ada@example.com and again ada@example.com"
    redacted, mapping = replace(["ada@example.com", "ada@example.com"], document)

    assert redacted == "<ID_1> and again <ID_1>"
    assert mapping == [("ada@example.com", "<ID_1>")]


def test_multiple_identifiers_keep_first_seen_order():
    document = "On 2024-08-21 write ada@example.com."
    redacted, mapping = replace(["2024-08-21", "ada@example.com"], document)

    assert redacted == "On <ID_1> write <ID_2>."
    assert mapping == [
        ("2024-08-21", "<ID_1>"),
        ("ada@example.com", "<ID_2>"),
    ]


def test_longer_identifier_wins_when_spans_overlap():
    document = "Contact Dr. Ursula Meier today."
    redacted, mapping = replace(["Ursula Meier", "Dr. Ursula Meier"], document)

    assert redacted == "Contact <ID_2> today."
    assert mapping == [
        ("Ursula Meier", "<ID_1>"),
        ("Dr. Ursula Meier", "<ID_2>"),
    ]


def test_replace_uses_regex_detector_matches(load_document):
    document = load_document("mixed.txt")
    identifiers = regex_detector(document)
    redacted, mapping = replace(identifiers, document)

    assert [original for original, _tag in mapping] == identifiers
    assert redacted == "On <ID_1> write <ID_2>, call <ID_3>, pay with <ID_4>.\n"
    for original, tag in mapping:
        assert original not in redacted
        assert tag in redacted


def test_restore_replaces_tags_back_to_original():
    mapping = [("2024-08-21", "<ID_1>"), ("ada@example.com", "<ID_2>")]
    llm_output = "The event on <ID_1> was organized by <ID_2>."
    restored = restore(mapping, llm_output)
    assert restored == "The event on 2024-08-21 was organized by ada@example.com."


def test_restore_roundtrip_with_replace():
    document = "Contact Dr. Ursula Meier at ursula@example.com on 2024-08-21."
    identifiers = ["Dr. Ursula Meier", "ursula@example.com", "2024-08-21"]
    redacted, mapping = replace(identifiers, document)
    restored = restore(mapping, redacted)
    assert restored == document

