"""Replace identifier strings in a document with reversible tags."""

from __future__ import annotations

import ahocorasick


def replace(identifiers: list[str], document: str) -> tuple[str, list[tuple[str, str]]]:
    """Substitute each identifier in *document* with a unique replacement tag.

    The same original string always maps to the same tag. Overlapping matches
    keep the leftmost, then longest span so a short identifier cannot consume
    part of a longer one. Occurrences are located with an Aho-Corasick
    automaton (pyahocorasick), scanning the document once.

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

    if not mapping:
        return document, mapping

    unique_identifiers = [identifier for identifier, _ in mapping]
    tag_by_index = [tag for _, tag in mapping]

    # Build Aho-Corasick automaton using pyahocorasick
    automaton = ahocorasick.Automaton()
    for pattern_index, identifier in enumerate(unique_identifiers):
        automaton.add_word(identifier, (pattern_index, len(identifier)))
    automaton.make_automaton()

    # Find every identifier occurrence in a single pass over the document
    spans: list[tuple[int, int, int]] = []
    for end_idx, (pattern_index, length) in automaton.iter(document):
        start_idx = end_idx - length + 1
        end_pos = end_idx + 1
        spans.append((start_idx, end_pos, pattern_index))

    # Leftmost, then longest span wins; then select greedily without overlaps.
    spans.sort(key=lambda item: (item[0], -(item[1] - item[0])))

    parts: list[str] = []
    last = 0
    cursor = 0
    for start, end, pattern_index in spans:
        if start < cursor:
            continue
        parts.append(document[last:start])
        parts.append(tag_by_index[pattern_index])
        last = end
        cursor = end
    parts.append(document[last:])

    return "".join(parts), mapping


def restore(replacements: list[tuple[str, str]], document: str) -> str:
    """Substitute replacement tags back with their original values in document.

    Uses an Aho-Corasick automaton (pyahocorasick) to locate all tags in a
    single pass over the document and substitute their original values.

    Args:
        replacements: List of (original, tag) tuples.
        document: The document or LLM response containing tags.

    Returns:
        Document with all replacement tags substituted back to their original values.
    """
    if not replacements or not document:
        return document

    automaton = ahocorasick.Automaton()
    for original, tag in replacements:
        automaton.add_word(tag, (original, len(tag)))
    automaton.make_automaton()

    # Find every tag occurrence in a single pass over the document
    spans: list[tuple[int, int, str]] = []
    for end_idx, (original, length) in automaton.iter(document):
        start_idx = end_idx - length + 1
        end_pos = end_idx + 1
        spans.append((start_idx, end_pos, original))

    if not spans:
        return document

    # Leftmost, then longest span wins
    spans.sort(key=lambda item: (item[0], -(item[1] - item[0])))

    parts: list[str] = []
    last = 0
    cursor = 0
    for start, end, original in spans:
        if start < cursor:
            continue
        parts.append(document[last:start])
        parts.append(original)
        last = end
        cursor = end
    parts.append(document[last:])

    return "".join(parts)

