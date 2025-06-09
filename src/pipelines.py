# pipelines.py
import csv
import re
import requests
import nltk
from parsers import DocumentParser
from neo4j_db import Neo4jHandler
from fsbi_loader import FSBILoader
from fred_loader import FREDLoader
from stock_loader import StockLoader

nltk.download("stopwords", quiet=True)
_STOPWORDS = set(nltk.corpus.stopwords.words("english"))

def remove_stopwords(tokens):
    return [t for t in tokens if t.lower() not in _STOPWORDS]

def clean_industry(raw):
    if not raw:
        return "Unspecified"
    cleaned = raw.strip().replace(",", ";").replace("&", "and")
    cleaned = re.sub(r"[^A-Za-z0-9\s;/\-]", "", cleaned)
    return cleaned

class DataPipeline:
    """
    Coordinates ingestion from multiple sources into Neo4j.
    """
    def __init__(
        self,
        csv_path="consumer_discretionary_sites.csv",
        fsbi_csv_path="fsbi_data_010122_040125.csv"
    ):
        # Path to your company wiki URLs CSV
        self.csv_path = csv_path
        # Path to your FSBI sector data CSV
        self.fsbi_csv_path = fsbi_csv_path

        self.parser = DocumentParser()
        self.db = Neo4jHandler()
        self.fsbi = FSBILoader(self.fsbi_csv_path)
        self.fred = FREDLoader()
        self.stock = StockLoader()

    def fetch_and_store_all(self):
        stored_count = 0

        # 1. Ingest FSBI from CSV
        try:
            self.fsbi.store_csv(self.db)
            print("✅ Loaded FSBI sector CSV data into Neo4j")
        except Exception as e:
            print(f"❌ FSBI CSV ingest failed: {e}")

        # 2. Ingest FRED macro indicators (global, starting 2022-01-01)
        fred_series = ["USSLIND", "PCE", "CPIAUCSL"]
        for series_id in fred_series:
            try:
                self.fred.store_series(self.db, series_id=series_id, start="2022-01-01")
                self.db.link_indicator_to_macro(series_id)
                print(f"✅ Loaded FRED series {series_id} into Neo4j")
            except Exception as e:
                print(f"❌ FRED ingest failed for {series_id}: {e}")

        # 3. Process each company from the ticker CSV
        total = sum(1 for _ in open(self.csv_path)) - 1
        print(f"🔍 Processing {total} company URLs...")

        with open(self.csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                symbol = row.get("symbol")
                wiki = row.get("wikipedia")
                if not (symbol and wiki):
                    continue

                # 3a. Wikipedia scraping & storage
                try:
                    resp = requests.get(wiki, timeout=10)
                    resp.raise_for_status()
                    parsed = self.parser.parse({
                        "html": resp.text,
                        "symbol": symbol,
                        "tags": remove_stopwords(
                            [symbol.lower()] + wiki.rsplit("/", 1)[-1].split("_")
                        )
                    })
                    for doc in parsed:
                        # 1) Create the Document node
                        self.db.store_document({
                            "id":     doc["id"],
                            "text":   doc["text"],
                            "symbol": doc["symbol"],
                            "tags":   doc["tags"]
                        })

                        # 2) Anchor the Document to its Company
                        self.db.link_document_to_company(doc["id"], doc["symbol"])

                        # 3) (Optional) Anchor to its Industry
                        if doc.get("industry"):
                            self.db.link_document_to_industry(doc["id"], doc["industry"])

                        stored_count += 1

                        # 4) Build out the rest of the company KG
                        self.db.create_company_kg_entry({
                            "symbol":       doc["symbol"],
                            "company_name": doc.get("company_name"),
                            "company_type": doc.get("company_type"),
                            "industry": (
                                clean_industry(doc.get("industry")).split(";")[0]
                                if doc.get("industry") else None
                            ),
                            "products":     doc.get("products", []),
                            "ceo":          doc.get("ceo")
                        })

                except Exception as e:
                    print(f"❌ Wiki fetch/parse failed for {symbol}: {e}")
                    continue

                # 3b. Stock price daily returns ingestion
                try:
                    returns = self.stock.fetch_daily_returns(
                        symbol,
                        start="2022-01-01"
                    )
                    for date, ret in returns.items():
                        self.db.store_stock_return(symbol, date, ret)
                    print(f"✅ Loaded daily returns for {symbol}")
                except Exception as e:
                    print(f"❌ Stock returns ingest failed for {symbol}: {e}")

        # Close Neo4j connection and return document count
        self.db.close()
        return stored_count
