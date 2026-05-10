from indexer import InvertedIndex
from search import find_pages, print_entry


def test_find_pages_multi_word():
    index = InvertedIndex()
    index.add_document("page1", "good friends")
    index.add_document("page2", "good night")

    assert find_pages(index, "good") == ["page1", "page2"]
    assert find_pages(index, "good friends") == ["page1"]
    assert find_pages(index, "missing") == []


def test_find_pages_empty_query():
    index = InvertedIndex()
    index.add_document("page1", "good friends")

    assert find_pages(index, "") == []
    assert find_pages(index, "   ") == []


def test_print_entry_missing():
    index = InvertedIndex()
    assert "No entry found" in print_entry(index, "nonsense")
