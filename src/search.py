from typing import List

from indexer import InvertedIndex, tokenize


def print_entry(index: InvertedIndex, word: str) -> str:
    key = word.lower()
    entry = index.data.get(key)
    if not entry:
        return f"No entry found for '{word}'."
    lines = [f"Word: {key}"]
    for url, stats in sorted(entry.items()):
        lines.append(f"- {url}: count={stats['count']}, positions={stats['positions']}")
    return "\n".join(lines)


def find_pages(index: InvertedIndex, query: str) -> List[str]:
    tokens = tokenize(query)
    if not tokens:
        return []

    pages_sets = []
    for token in tokens:
        entry = index.data.get(token, {})
        pages_sets.append(set(entry.keys()))

    if not pages_sets:
        return []

    common = set.intersection(*pages_sets)
    return sorted(common)
