"""Replace identifier strings in a document with reversible tags."""

from __future__ import annotations

from collections import deque


class _AhoCorasick:
    """Aho-Corasick automaton for locating many patterns in one pass.

    Nodes are stored as parallel lists indexed by node id. ``goto`` holds the
    trie transitions, ``fail`` the failure links, and ``output`` the pattern
    indices that end at (or via failure links, through) each node.
    """

    def __init__(self, patterns: list[str]) -> None:
        self._goto: list[dict[str, int]] = [{}]
        self._fail: list[int] = [0]
        self._output: list[list[int]] = [[]]
        self._lengths: list[int] = [len(pattern) for pattern in patterns]

        for pattern_index, pattern in enumerate(patterns):
            self._add(pattern, pattern_index)
        self._build_failure_links()

    def _add(self, pattern: str, pattern_index: int) -> None:
        node = 0
        for char in pattern:
            next_node = self._goto[node].get(char)
            if next_node is None:
                next_node = len(self._goto)
                self._goto.append({})
                self._fail.append(0)
                self._output.append([])
                self._goto[node][char] = next_node
            node = next_node
        self._output[node].append(pattern_index)

    def _build_failure_links(self) -> None:
        queue: deque[int] = deque()
        for next_node in self._goto[0].values():
            self._fail[next_node] = 0
            queue.append(next_node)

        while queue:
            node = queue.popleft()
            for char, next_node in self._goto[node].items():
                queue.append(next_node)
                fallback = self._fail[node]
                while fallback and char not in self._goto[fallback]:
                    fallback = self._fail[fallback]
                self._fail[next_node] = self._goto[fallback].get(char, 0)
                self._output[next_node].extend(self._output[self._fail[next_node]])

    def find(self, text: str) -> list[tuple[int, int, int]]:
        """Return every match as ``(start, end, pattern_index)``."""

        matches: list[tuple[int, int, int]] = []
        node = 0
        for position, char in enumerate(text):
            while node and char not in self._goto[node]:
                node = self._fail[node]
            node = self._goto[node].get(char, 0)
            for pattern_index in self._output[node]:
                end = position + 1
                start = end - self._lengths[pattern_index]
                matches.append((start, end, pattern_index))
        return matches


def replace(identifiers: list[str], document: str) -> tuple[str, list[tuple[str, str]]]:
    """Substitute each identifier in *document* with a unique replacement tag.

    The same original string always maps to the same tag. Overlapping matches
    keep the leftmost, then longest span so a short identifier cannot consume
    part of a longer one. Occurrences are located with an Aho-Corasick
    automaton, so the document is scanned only once regardless of how many
    identifiers are supplied.

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

    # Find every identifier occurrence in a single pass over the document.
    automaton = _AhoCorasick(unique_identifiers)
    spans = automaton.find(document)

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
