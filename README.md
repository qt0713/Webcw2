# Search Tool for quotes.toscrape.com

## Project overview and purpose
This command-line search tool crawls the site https://quotes.toscrape.com/, builds an inverted index of words found on the crawled pages, and provides search functionality over the index. The index stores per-word statistics for each page (frequency and positions) to support accurate retrieval and position-aware features. The current implementation also includes crawler robustness improvements, integration tests, and a lightweight performance benchmark.

## Installation / setup
1. Create and activate a Python virtual environment (recommended):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows PowerShell
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

Required packages are listed in `requirements.txt`.

## Dependencies
- `requests` — HTTP requests
- `beautifulsoup4` — HTML parsing
- `pytest` — test runner (development)
- `coverage` — optional coverage reporting used during development
- `ruff` — optional style checker used during development

Install the runtime and test dependencies with `pip install -r requirements.txt`. Optional development tools can be installed separately if needed.

## Usage examples (all four commands)
Run the interactive CLI from the project root:

```powershell
python src\main.py
```

Inside the CLI, use the following commands:

- `build`
  - Description: Crawl the target website, build the inverted index, and save it to `data/index.json`. The crawler follows pagination, respects the politeness window, and uses retries/backoff for transient network errors.
  - Example input: `build`
  - Expected result: a message like `Indexed N pages and saved to data/index.json.`

- `load`
  - Description: Load an existing index from `data/index.json` into memory for queries.
  - Example input: `load`
  - Expected result: a message like `Loaded index from data/index.json.`

- `print <word>`
  - Description: Print the inverted-index entry for a single word (case-insensitive). Displays URLs with `count` and `positions`.
  - Example input: `print nonsense`
  - Example output:
    - `Word: nonsense`
    - `- https://quotes.toscrape.com/page/2/: count=1, positions=[417]`

- `find <terms>`
  - Description: Find pages that contain all specified terms (space-separated). Search is case-insensitive and uses AND semantics.
  - Example input: `find good friends`
  - Example output:
    - `Matches:`
    - `- https://quotes.toscrape.com/`
    - `- https://quotes.toscrape.com/page/2/`

Exit the CLI with `exit`.

## Testing instructions
Run the automated tests from the project root:

```powershell
pytest
```

Included tests:
- `tests/test_indexer.py` — validates tokenization, counts, positions, and save/load roundtrip.
- `tests/test_search.py` — validates single-word, multi-word AND queries, and empty-query handling.
- `tests/test_crawler.py` — validates pagination, alternate HTML structures, retry/backoff, wait handling, and cycle protection using mocks.
- `tests/test_integration.py` — end-to-end crawl, index, save/load, and search flow.
- `tests/test_performance.py` — lightweight performance smoke test for indexing and search.

Optional development commands:

```powershell
python -m coverage run -m pytest
python -m coverage report -m
pytest -m integration
pytest -m performance
```

## Architecture overview and design rationale

- Files:
  - `src/crawler.py`: crawler that fetches pages starting from `https://quotes.toscrape.com/`, follows multiple next-link patterns for pagination, extracts text from several common HTML structures, enforces a configurable politeness window, and implements configurable timeout/retry/backoff.
  - `src/indexer.py`: tokenizer and inverted-index implementation; stores `word -> url -> {count, positions}` and supports save/load to a single JSON file.
  - `src/search.py`: query utilities — `print` formatting and `find` (multi-word AND intersection).
  - `src/main.py`: CLI glue that runs `build`, `load`, `print`, and `find`.

- Design decisions and rationale:
  - Index shape (`word -> url -> {count, positions}`) was chosen because it directly supports the assignment requirements (frequency and positional information) and allows for position-aware features without additional passes.
  - Tokenization uses a regular expression capturing letters, digits, and apostrophes to keep contractions like `don't` intact; all tokens are lowercased so search is case-insensitive, which simplifies matching and meets the assignment constraint.
  - Persistence to a single JSON file (`data/index.json`) makes the submission and manual inspection straightforward. For larger-scale systems, a database or incremental storage would be preferable, but is unnecessary here given the small target site.
  - Respecting a politeness window (>= 6 seconds) is required by the assignment; retry and backoff logic improves robustness against transient network failures while keeping politeness guarantees between attempts.
  - The crawler now handles a broader range of HTML structures by trying several content selectors and next-link selectors before falling back to full-document text.

## Notes
- `build` performs real network requests. Do not interrupt during polite sleeps unless necessary. The default politeness window is 6 seconds as required.
