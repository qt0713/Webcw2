from unittest.mock import Mock

import pytest
import requests

from crawler import CrawlerError, crawl_site


def test_crawl_site_follow_next(monkeypatch):
    page1 = """
    <html><body>
    <div class="quote">Quote one</div>
    <li class="next"><a href="/page/2/">Next</a></li>
    </body></html>
    """
    page2 = """
    <html><body>
    <div class="quote">Quote two</div>
    </body></html>
    """

    responses = {
        "https://quotes.toscrape.com/": page1,
        "https://quotes.toscrape.com/page/2/": page2,
    }

    def fake_get(url, timeout=10, **_kwargs):
        response = Mock(spec=requests.Response)
        response.status_code = 200
        response.text = responses[url]
        response.raise_for_status = Mock()
        return response

    monkeypatch.setattr(requests.Session, "get", staticmethod(fake_get))

    pages = crawl_site("https://quotes.toscrape.com/", politeness_seconds=0)
    assert list(pages.keys()) == [
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/page/2/",
    ]
    assert "Quote one" in pages["https://quotes.toscrape.com/"]
    assert "Quote two" in pages["https://quotes.toscrape.com/page/2/"]


def test_crawl_site_retries_then_success(monkeypatch):
    page1 = "<html><body>Quote one</body></html>"
    calls = {"count": 0}

    def flaky_get(url, timeout=10, **_kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            raise requests.RequestException("temporary")
        response = Mock(spec=requests.Response)
        response.status_code = 200
        response.text = page1
        response.raise_for_status = Mock()
        return response

    monkeypatch.setattr(requests.Session, "get", staticmethod(flaky_get))

    pages = crawl_site(
        "https://quotes.toscrape.com/",
        politeness_seconds=0,
        max_pages=1,
        max_retries=1,
        backoff_seconds=0,
        sleep_func=lambda _s: None,
    )
    assert calls["count"] == 2
    assert "https://quotes.toscrape.com/" in pages


def test_crawl_site_raises_after_retries(monkeypatch):
    def failing_get(url, timeout=10, **_kwargs):
        raise requests.RequestException("down")

    monkeypatch.setattr(requests.Session, "get", staticmethod(failing_get))

    with pytest.raises(CrawlerError):
        crawl_site(
            "https://quotes.toscrape.com/",
            politeness_seconds=0,
            max_pages=1,
            max_retries=1,
            backoff_seconds=0,
            sleep_func=lambda _s: None,
        )
