
import requests

from crawler import crawl_site
from indexer import InvertedIndex
from search import find_pages, print_entry


def test_end_to_end_crawl_index_and_search(monkeypatch, tmp_path):
    page1 = """
    <html>
      <body>
        <main>
          <div class="quote">Good friends are rare.</div>
        </main>
        <li class="next"><a href="/page/2/">Next</a></li>
      </body>
    </html>
    """
    page2 = """
    <html>
      <body>
        <article>
          <p>Nonsense and indifference appear here.</p>
        </article>
      </body>
    </html>
    """

    responses = {
        "https://quotes.toscrape.com/": page1,
        "https://quotes.toscrape.com/page/2/": page2,
    }

    def fake_get(url, timeout=10, **_kwargs):
        response = requests.Response()
        response.status_code = 200
        response._content = responses[url].encode("utf-8")
        response.url = url
        response.raise_for_status = lambda: None
        return response

    monkeypatch.setattr(requests.Session, "get", staticmethod(fake_get))

    pages = crawl_site(
        "https://quotes.toscrape.com/",
        politeness_seconds=0,
        max_pages=2,
        max_retries=0,
        sleep_func=lambda _s: None,
    )

    assert len(pages) == 2

    index = InvertedIndex()
    for url, text in pages.items():
        index.add_document(url, text)

    path = tmp_path / "index.json"
    index.save(str(path))
    loaded = InvertedIndex.load(str(path))

    assert find_pages(loaded, "good friends") == ["https://quotes.toscrape.com/"]
    assert find_pages(loaded, "nonsense indifference") == ["https://quotes.toscrape.com/page/2/"]
    assert "Word: nonsense" in print_entry(loaded, "nonsense")
