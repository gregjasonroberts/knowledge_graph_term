# pipelines.py
import csv
import re
import requests
import nltk
from neo4j_db import Neo4jHandler
from parsers import DocumentParser

nltk.download("stopwords", quiet=True)
_STOPWORDS = set(nltk.corpus.stopwords.words("english"))

def remove_stopwords(tokens):
    return [t for t in tokens if t.lower() not in _STOPWORDS]

def clean_industry(raw):
    if not raw:
        return "Unspecified"
    cleaned = raw.strip()
    cleaned = cleaned.replace(",", ";").replace("&", "and")
    cleaned = re.sub(r"[^A-Za-z0-9\s;/\-]", "", cleaned)
    return cleaned

class DataPipeline:
    """
    Fetches Wikipedia URLs from CSV, parses, and stores to Neo4j.
    """
    def __init__(self, csv_path="consumer_discretionary_sites.csv"):
        self.csv_path = csv_path
        self.parser = DocumentParser()
        self.db_handler = Neo4jHandler()

    def fetch_and_store_all(self):
        total_rows = sum(1 for _ in open(self.csv_path)) - 1  # subtract header
        print(f"🔍 Found {total_rows} total rows in CSV.")

        stored_count = 0
        with open(self.csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                symbol   = row.get("symbol")
                wiki_url = row.get("wikipedia")
                if not (symbol and wiki_url):
                    continue

                try:
                    resp = requests.get(wiki_url, timeout=10)
                    resp.raise_for_status()
                    html = resp.text
                    print(f"📄 Successfully fetched: {symbol} ({wiki_url})")
                except requests.RequestException as e:
                    print(f"❌ Failed to fetch {symbol}: {e}")
                    continue

                raw = re.sub(r'[^A-Za-z0-9_]', '', wiki_url.rsplit("/", 1)[-1])
                tokens = [symbol.lower()] + raw.split("_")
                tags = remove_stopwords(tokens)

                raw_item = {"html": html, "symbol": symbol, "tags": tags}
                parsed_docs = self.parser.parse(raw_item)
                print(f"🧠 Parsed {len(parsed_docs)} document(s) from {symbol}")

                for doc in parsed_docs:
                    self.db_handler.store_document(doc)
                    stored_count += 1

                    raw_industries = clean_industry(doc.get("industry")).split(";")
                    industries = [i.strip() for i in raw_industries if i.strip()]
                    products = doc.get("product") or []

                    for industry in industries:
                        for product in products:
                            self.db_handler.create_company_kg_entry({
                                "company_name": doc.get("company_name") or symbol,
                                "symbol": doc.get("symbol") or symbol,
                                "company_type": "For-Profit",
                                "ceo_name": doc.get("ceo_name") or "Unknown",
                                "industry": industry,
                                "product": product
                            })

        self.db_handler.close()
        return stored_count
