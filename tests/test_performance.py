import time

import pytest

from indexer import InvertedIndex
from search import find_pages


@pytest.mark.performance
def test_index_and_search_performance_smoke():
    index = InvertedIndex()

    start = time.perf_counter()
    for page_number in range(200):
        text = "good friends nonsense " * 20
        index.add_document(f"page-{page_number}", text)
    build_duration = time.perf_counter() - start

    start = time.perf_counter()
    results = find_pages(index, "good friends")
    search_duration = time.perf_counter() - start

    assert len(results) == 200
    assert build_duration < 1.5
    assert search_duration < 0.2
