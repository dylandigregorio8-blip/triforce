"""Replace identifier strings in a document with reversible tags."""

from __future__ import annotations


def replace(identifiers: list[str], document: str) -> tuple[str, list[tuple[str, str]]]:
    """Substitute each identifier in *document* with a unique replacement tag.

    The same original string always maps to the same tag. Overlapping matches
    keep the leftmost, then longest span so a short identifier cannot consume
    part of a longer one.

    Returns:
        (redacted_document, [(original, tag), ...]) in first-seen identifier order.
    """

    # Create tokens for each identifier.
    mapping: list[tuple[str, str]] = []
    seen: set[str] = set()
    for identifier in identifiers:
        if not identifier or identifier in seen:
            continue
        seen.add(identifier)
        mapping.append((identifier, f"<ID_{len(mapping) + 1}>"))

    tag_by_identifier = dict(mapping)

    # Find each identifier in the document.    
    spans: list[tuple[int, int, str]] = []
    for identifier in tag_by_identifier:
        start = 0
        while True:
            index = document.find(identifier, start)
            if index == -1:
                break
            spans.append((index, index + len(identifier), identifier))
            start = index + 1

    spans.sort(key=lambda item: (item[0], -(item[1] - item[0])))

    chosen: list[tuple[int, int, str]] = []
    cursor = 0
    for start, end, identifier in spans:
        if start < cursor:
            continue
        chosen.append((start, end, identifier))
        cursor = end

    parts: list[str] = []
    last = 0
    for start, end, identifier in chosen:
        parts.append(document[last:start])
        parts.append(tag_by_identifier[identifier])
        last = end
    parts.append(document[last:])

    return "".join(parts), mapping


def restore(replacements: list[tuple[str, str]], document: str) -> str:
    """Substitute replacement tags back with their original values in document.

    Args:
        replacements: List of (original, tag) tuples.
        document: The document or LLM response containing tags.

    Returns:
        Document with all replacement tags substituted back to their original values.
    """
    sorted_replacements = sorted(replacements, key=lambda item: len(item[1]), reverse=True)
    result = document
    for original, tag in sorted_replacements:
        result = result.replace(tag, original)
    return result
