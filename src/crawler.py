import time
from typing import Callable, Dict, Optional, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class CrawlerError(Exception):
    pass


def _sleep_if_needed(
    last_request_time: Optional[float],
    politeness_seconds: float,
    sleep_func: Callable[[float], None],
) -> None:
    if last_request_time is None:
        return
    elapsed = time.monotonic() - last_request_time
    wait_time = politeness_seconds - elapsed
    if wait_time > 0:
        sleep_func(wait_time)


def _fetch_with_retries(
    session: requests.Session,
    url: str,
    timeout_seconds: float,
    max_retries: int,
    backoff_seconds: float,
    politeness_seconds: float,
    last_request_time: Optional[float],
    sleep_func: Callable[[float], None],
) -> Tuple[requests.Response, float]:
    for attempt in range(max_retries + 1):
        _sleep_if_needed(last_request_time, politeness_seconds, sleep_func)
        try:
            response = session.get(url, timeout=timeout_seconds)
            last_request_time = time.monotonic()
            response.raise_for_status()
            return response, last_request_time
        except requests.RequestException as exc:
            last_request_time = time.monotonic()
            if attempt >= max_retries:
                raise CrawlerError(f"Request failed for {url}: {exc}") from exc
            sleep_func(backoff_seconds * (2**attempt))

    raise CrawlerError(f"Request failed for {url}")


def crawl_site(
    start_url: str,
    politeness_seconds: float = 6.0,
    max_pages: Optional[int] = None,
    max_retries: int = 2,
    backoff_seconds: float = 1.0,
    timeout_seconds: float = 10.0,
    user_agent: str = "cwk2-search-tool/1.0",
    sleep_func: Callable[[float], None] = time.sleep,
) -> Dict[str, str]:
    session = requests.Session()
    session.headers.update({"User-Agent": user_agent})
    pages: Dict[str, str] = {}
    current_url: Optional[str] = start_url
    last_request_time: Optional[float] = None

    while current_url:
        if current_url in pages:
            break
        if max_pages is not None and len(pages) >= max_pages:
            break

        response, last_request_time = _fetch_with_retries(
            session=session,
            url=current_url,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            backoff_seconds=backoff_seconds,
            politeness_seconds=politeness_seconds,
            last_request_time=last_request_time,
            sleep_func=sleep_func,
        )
        soup = BeautifulSoup(response.text, "html.parser")
        pages[current_url] = soup.get_text(" ", strip=True)

        next_link = soup.select_one("li.next a")
        if next_link and next_link.get("href"):
            current_url = urljoin(current_url, next_link["href"])
        else:
            current_url = None

    return pages
