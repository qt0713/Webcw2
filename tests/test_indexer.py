from indexer import InvertedIndex, tokenize


def test_indexer_positions_and_counts():
    index = InvertedIndex()
    index.add_document("http://example.com", "Good good friends")

    assert "good" in index.data
    entry = index.data["good"]["http://example.com"]
    assert entry["count"] == 2
    assert entry["positions"] == [0, 1]

    friends = index.data["friends"]["http://example.com"]
    assert friends["count"] == 1
    assert friends["positions"] == [2]


def test_tokenize_punctuation_and_case():
    tokens = tokenize("Hello, world! Don't stop.")
    assert tokens == ["hello", "world", "don't", "stop"]


def test_index_save_load_roundtrip(tmp_path):
    index = InvertedIndex()
    index.add_document("page", "good friends")

    path = tmp_path / "index.json"
    index.save(str(path))
    loaded = InvertedIndex.load(str(path))

    assert loaded.data == index.data
