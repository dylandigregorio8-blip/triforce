from regex_detector import regex_detector


def test_iban():
    assert regex_detector("IBAN GB82WEST12345698765432") == ["GB82WEST12345698765432"]


def test_iban_with_spaces():
    assert regex_detector("CH93 0023 0230 1234 5678 9 and GB82 WEST 1234 5698 7654 32") == [
        "CH93 0023 0230 1234 5678 9",
        "GB82 WEST 1234 5698 7654 32",
    ]



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
