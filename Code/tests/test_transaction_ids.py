from regex_detector import regex_detector


def test_uuid_lowercase():
    assert regex_detector("Session ID: 123e4567-e89b-12d3-a456-426614174000") == [
        "123e4567-e89b-12d3-a456-426614174000"
    ]


def test_uuid_uppercase_and_mixed():
    assert regex_detector(
        "UUIDs: A0EEBC99-9C0B-4EF8-BB6D-6BB9BD380A11 and 550e8400-e29b-41d4-a716-446655440000"
    ) == [
        "A0EEBC99-9C0B-4EF8-BB6D-6BB9BD380A11",
        "550e8400-e29b-41d4-a716-446655440000",
    ]


def test_invalid_uuid_format():
    assert regex_detector("Invalid UUID: 123e4567-e89b-12d3-a456-42661417400") == []
    assert regex_detector("Invalid characters: 123g4567-e89b-12d3-a456-426614174000") == []
