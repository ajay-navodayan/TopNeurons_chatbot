import json
import csv
import re
from collections import Counter

with open('../data/chunks.json', encoding='utf-8') as f:
    chunks = json.load(f)

print(f"Total chunks: {len(chunks)}")
print(f"Total pages : {len(set(c['url'] for c in chunks))}")

print("\n--- Tag Distribution ---")
for tag, count in Counter(c['tag'] for c in chunks).most_common():
    print(f"  {tag:15} {count} chunks")

print("\n--- Pages Crawled ---")
for url in sorted(set(c['url'] for c in chunks)):
    print(f"  {url}")

print("\n--- Sample: 1 chunk per tag ---")
seen = set()
for c in chunks:
    if c['tag'] not in seen:
        seen.add(c['tag'])
        print(f"\n[{c['tag'].upper()}] {c['section'].encode('ascii', 'ignore').decode()}")
        print(f"  URL : {c['url']}")
        print(f"  Text: {c['text'][:200].encode('ascii','ignore').decode()}...")


def is_clean(text):
    """Return True if text has no encoded/garbled characters."""
    # reject if more than 10% non-ASCII characters (Hindi/encoded content)
    non_ascii = sum(1 for ch in text if ord(ch) > 127)
    return (non_ascii / max(len(text), 1)) < 0.10


def clean_text(text):
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# Export clean labelled CSV
output_file = '../data/labelled_dataset.csv'
fields = ['chunk_id', 'tag', 'title', 'section', 'url', 'text']

clean_chunks = [
    c for c in chunks
    if is_clean(c['text'])
    and is_clean(c.get('section', ''))
    and '%' not in c['url']          # skip encoded Hindi URLs
    and c['tag'] != 'general'        # skip unclassified chunks
]

with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    for c in clean_chunks:
        writer.writerow({
            'chunk_id': c['chunk_id'],
            'tag':      c['tag'],
            'title':    clean_text(c.get('title', '')),
            'section':  clean_text(c.get('section', '')),
            'url':      c['url'],
            'text':     clean_text(c['text']),
        })

print(f"\nCSV exported: {output_file}")
print(f"Total rows  : {len(clean_chunks)} (filtered from {len(chunks)})")
from collections import Counter
print("Tag breakdown:")
for tag, count in Counter(c['tag'] for c in clean_chunks).most_common():
    print(f"  {tag:15} {count}")
