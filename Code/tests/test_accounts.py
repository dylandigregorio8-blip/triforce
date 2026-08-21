from regex_detector import regex_detector


def test_iban():
    assert regex_detector("IBAN GB82WEST12345698765432") == ["GB82WEST12345698765432"]


def test_card_number_with_spaces_or_dashes():
    assert regex_detector("4111 1111 1111 1111 then 4111-1111-1111-1111") == [
        "4111 1111 1111 1111",
        "4111-1111-1111-1111",
    ]


def test_account_keyword_prefix():
    assert regex_detector("Use account 123456789012") == []


def test_short_digit_run_is_not_an_account():
    assert regex_detector("Not an account: 12345") == []


def test_accounts_fixture_file(load_document):
    document = load_document("accounts.txt")
    assert regex_detector(document) == [
        "GB82WEST12345698765432",
        "4111 1111 1111 1111",
    ]
