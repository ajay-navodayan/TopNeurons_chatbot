import re
from bs4 import BeautifulSoup

REMOVE_TAGS = ["nav", "footer", "header", "script", "style", "noscript", "aside"]


def clean_text(text):
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_page(url, html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(REMOVE_TAGS):
        tag.decompose()

    title = soup.title.get_text(strip=True) if soup.title else ""

    sections = []
    current_heading = "General"
    current_texts = []

    for el in soup.find_all(["h1", "h2", "h3", "p", "li", "ul", "ol"]):
        if el.name in ["h1", "h2", "h3"]:
            if current_texts:
                sections.append({"heading": current_heading, "text": " ".join(current_texts)})
                current_texts = []
            current_heading = clean_text(el.get_text())
        else:
            t = clean_text(el.get_text())
            if len(t) >= 40:
                current_texts.append(t)

    if current_texts:
        sections.append({"heading": current_heading, "text": " ".join(current_texts)})

    return {"url": url, "title": title, "sections": sections}


def extract_all(pages):
    results = []
    seen_texts = set()
    for p in pages:
        doc = extract_page(p["url"], p["html"])
        deduped = []
        for s in doc["sections"]:
            if s["text"] not in seen_texts:
                seen_texts.add(s["text"])
                deduped.append(s)
        doc["sections"] = deduped
        if deduped:
            results.append(doc)
    return results
