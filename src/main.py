import shlex
from pathlib import Path

from crawler import CrawlerError, crawl_site
from indexer import InvertedIndex
from search import find_pages, print_entry

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
INDEX_PATH = DATA_DIR / "index.json"
START_URL = "https://quotes.toscrape.com/"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def cmd_build() -> InvertedIndex:
    ensure_data_dir()
    pages = crawl_site(START_URL)
    index = InvertedIndex()
    for url, text in pages.items():
        index.add_document(url, text)
    index.save(str(INDEX_PATH))
    print(f"Indexed {len(pages)} pages and saved to {INDEX_PATH}.")
    return index


def cmd_load() -> InvertedIndex:
    if not INDEX_PATH.exists():
        raise FileNotFoundError(f"Index file not found at {INDEX_PATH}.")
    index = InvertedIndex.load(str(INDEX_PATH))
    print(f"Loaded index from {INDEX_PATH}.")
    return index


def repl() -> None:
    index = None
    print("Search tool ready. Commands: build, load, print <word>, find <terms>, exit")

    while True:
        try:
            raw = input("> ").strip()
        except EOFError:
            print()
            break

        if not raw:
            print("Empty command. Try build, load, print, find, or exit.")
            continue

        parts = shlex.split(raw)
        command = parts[0].lower()
        args = parts[1:]

        if command == "exit":
            break
        if command == "build":
            try:
                index = cmd_build()
            except CrawlerError as exc:
                print(f"Build failed: {exc}")
            continue
        if command == "load":
            try:
                index = cmd_load()
            except FileNotFoundError as exc:
                print(exc)
            continue

        if index is None:
            print("Index not loaded. Run build or load first.")
            continue

        if command == "print":
            if not args:
                print("Usage: print <word>")
                continue
            print(print_entry(index, " ".join(args)))
            continue

        if command == "find":
            if not args:
                print("Usage: find <terms>")
                continue
            results = find_pages(index, " ".join(args))
            if results:
                print("Matches:")
                for url in results:
                    print(f"- {url}")
            else:
                print("No matches found.")
            continue

        print("Unknown command. Try build, load, print, find, or exit.")


if __name__ == "__main__":
    repl()
