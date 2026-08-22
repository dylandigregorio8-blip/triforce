"""Replace configured PII patterns in a document and return the matches found."""

from __future__ import annotations

import re
from typing import Pattern

# All patterns used by regex_detector. Each category may list several alternatives.
REGEX_CONFIG: dict[str, list[str]] = {
    "date": [
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b",
        r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|"
        r"Dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b",
        r"\b\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|"
        r"Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|"
        r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}\b",
    ],
    "emails": [
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    ],
    "accounts": [
        # IBAN with optional spaces (e.g., CH93 0023 0230 1234 5678 9)
        r"\b[A-Z]{2}\d{2}(?:\s?[A-Z0-9]{4}){3,7}\s?[A-Z0-9]{1,4}\b",
        # Standard continuous IBAN
        r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b",
        # Credit cards / account numbers
        r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
    ],
    "transaction_ids": [
        # Transaction IDs like TXN-2026-0801
        # r"\b(?:TXN|REF|ID|INV|ORD)[-:][A-Z0-9-]+\b",
        # UUIDs
        r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b",
    ],
    "phone_numbers": [
        # International E.164-style: +country then national number, optional grouping
        r"\+[1-9]\d{0,2}[\s.-]*\(?\d{1,4}\)?(?:[\s.-]*\d{2,8})+",
        # European: 00 international prefix or national leading 0 with grouped digits
        r"(?:00[1-9]\d{0,2}|0\d{1,4})(?:[\s-]\d{2,4}){2,5}",
        r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b",
        r"\(\d{3}\)\s*\d{3}[-.\s]?\d{4}",
    ],
    "national_ids": [
        # Swiss AHV/AVS (756.XXXX.XXXX.XX)
        r"\b756\.\d{4}\.\d{4}\.\d{2}\b",
        # US SSN
        r"\b\d{3}-\d{2}-\d{4}\b",
    ],
}
_COMPILED: list[tuple[str, Pattern[str]]] = [
    (category, re.compile(pattern, re.IGNORECASE))
    for category, patterns in REGEX_CONFIG.items()
    for pattern in patterns
]


def regex_detector(document: str) -> list[str]:
    """Find configured date, email, account, and phone matches in *document*.

    Returns the matched strings in document order (leftmost, then longest).
    Overlapping matches are skipped so each span is reported once.
    """
    candidates: list[tuple[int, int, str]] = []
    for _category, compiled in _COMPILED:
        for match in compiled.finditer(document):
            candidates.append((match.start(), match.end(), match.group(0)))

    candidates.sort(key=lambda item: (item[0], -(item[1] - item[0])))

    matches: list[str] = []
    cursor = 0
    for start, end, text in candidates:
        if start < cursor:
            continue
        matches.append(text)
        cursor = end
    return matches
