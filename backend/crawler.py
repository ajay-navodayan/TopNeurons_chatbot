import warnings
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from config import BASE_URL, MAX_PAGES

warnings.filterwarnings("ignore")

# Full browser headers to avoid 406 rejections
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Only crawl content-rich sitemap types; skip student application pages (7000+)
SITEMAP_WHITELIST = ["post-sitemap", "page-sitemap"]

# Skip these URL patterns — individual notice pages are repetitive noise
URL_BLOCKLIST = ["/notice_board/", "/students_application/", "/photogallery/",
                 "/slider/", "/testimony/", "/video/", "/partner/",
                 "/logout/", "/login/", "/change-password/", "/forgot-password/",
                 "/application-status/", "/application-details/"]

# High-value pages to always crawl first
PRIORITY_URLS = [
    "https://www.topneurons.org/",
    "https://www.topneurons.org/about-us/",
    "https://www.topneurons.org/program-details/",
    "https://www.topneurons.org/admission-exam/",
    "https://www.topneurons.org/faqs/",
    "https://www.topneurons.org/contact/",
    "https://www.topneurons.org/notice-board/",
    "https://www.topneurons.org/apply-for-scholarship/",
    "https://www.topneurons.org/success-stories/",
    "https://www.topneurons.org/get-involved/",
    "https://www.topneurons.org/our-partners/",
    "https://www.topneurons.org/legal/",
]


def _fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=15, verify=False)
    r.raise_for_status()
    return r


def get_sitemap_urls(base_url):
    """Handle both plain sitemaps and sitemap index files."""
    try:
        r = _fetch(base_url + "/sitemap.xml")
        soup = BeautifulSoup(r.content, "lxml-xml")

        # Sitemap index — contains <sitemap><loc> entries
        sub_sitemaps = [loc.text.strip() for loc in soup.find_all("sitemap")]
        if sub_sitemaps:
            # It's a sitemap index; fetch whitelisted sub-sitemaps only
            all_urls = []
            for sm_tag in soup.find_all("sitemap"):
                loc = sm_tag.find("loc")
                if not loc:
                    continue
                sm_url = loc.text.strip()
                if not any(w in sm_url for w in SITEMAP_WHITELIST):
                    continue
                try:
                    r2 = _fetch(sm_url)
                    soup2 = BeautifulSoup(r2.content, "lxml-xml")
                    page_urls = [
                        u.text.strip() for u in soup2.find_all("loc")
                        if not u.text.strip().endswith((".jpg", ".png", ".jpeg", ".gif", ".pdf"))
                    ]
                    all_urls.extend(page_urls)
                    print(f"[Sitemap] {sm_url} -> {len(page_urls)} URLs")
                except Exception as e:
                    print(f"[Sitemap] Skip {sm_url}: {e}")
            return all_urls

        # Plain sitemap — contains <url><loc> entries directly
        urls = [
            loc.text.strip() for loc in soup.find_all("loc")
            if not loc.text.strip().endswith((".jpg", ".png", ".jpeg", ".gif", ".pdf"))
        ]
        if urls:
            print(f"[Sitemap] Found {len(urls)} URLs")
            return urls
    except Exception as e:
        print(f"[Sitemap] Failed: {e}")
    return []


def is_internal(url, base):
    return urlparse(url).netloc == urlparse(base).netloc


def crawl(base_url=BASE_URL, max_pages=MAX_PAGES):
    visited, pages = set(), []

    # Start with priority URLs, then sitemap
    sitemap_urls = get_sitemap_urls(base_url)
    queue = PRIORITY_URLS + [u for u in sitemap_urls if u not in PRIORITY_URLS]
    queue = queue[:max_pages * 2]  # buffer for blocked URLs

    while queue and len(visited) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        if any(block in url for block in URL_BLOCKLIST):
            continue
        try:
            r = _fetch(url)
            if "text/html" not in r.headers.get("Content-Type", ""):
                continue
            visited.add(url)
            soup = BeautifulSoup(r.text, "html.parser")
            pages.append({"url": url, "html": r.text})
            print(f"[Crawl] {len(visited)}/{max_pages} - {url}")

            if not sitemap_urls:
                for a in soup.find_all("a", href=True):
                    full = urljoin(url, a["href"]).split("#")[0].split("?")[0]
                    if is_internal(full, base_url) and full not in visited:
                        queue.append(full)
        except Exception as e:
            print(f"[Skip] {url} - {e}")

    print(f"[Done] Crawled {len(pages)} pages")
    return pages
