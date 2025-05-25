# parsers.py
from bs4 import BeautifulSoup
import uuid
import re

class DocumentParser:
    """
    Parses raw scraped items (with 'html', 'symbol', 'tags') into structured records.
    """
    def __init__(self, verbose=False):
        self.verbose = verbose

    def parse(self, raw_item):
        html = raw_item.get("html")
        symbol = raw_item.get("symbol", "")
        tags = raw_item.get("tags", [])

        if not html:
            if self.verbose:
                print("⚠️ No HTML content provided.")
            return []

        soup = BeautifulSoup(html, "html.parser")

        # Extract the first meaningful paragraph
        summary = self._extract_first_paragraph(soup)

        # Extract fields from infobox
        info = self._extract_infobox(soup)

        record = {
            "id": str(uuid.uuid4()),
            "symbol": symbol,
            "tags": tags,
            "summary": summary,
            "company_name": info.get("company_name", symbol),
            "company_type": info.get("company_type"),
            "ceo": info.get("ceo"),
            "headquarters": info.get("headquarters"),
            "industry": info.get("industry"),
            "products": info.get("products", [])
        }
        return [record]

    def _extract_first_paragraph(self, soup):
        for p in soup.select("#mw-content-text p"):
            text = p.get_text(strip=True)
            if text:
                return text
        return ""

    def _extract_infobox(self, soup):
        info = {}
        infobox = soup.select_one("table.infobox")
        if not infobox:
            if self.verbose:
                print("⚠️ No infobox found.")
            return info

        for row in infobox.select("tr"):
            th = row.select_one("th")
            td = row.select_one("td")
            if not th or not td:
                continue

            key = th.get_text(strip=True).lower()
            val = td.get_text(strip=True)

            if "name" in key and not info.get("company_name"):
                info["company_name"] = val
            elif "type" in key:
                info["company_type"] = val
            elif "headquarter" in key:
                info["headquarters"] = val
            elif any(term in key for term in ["industry", "sector", "category"]):
                info["industry"] = val
            elif "ceo" in key or "key people" in key:
                info["ceo"] = val.split("–")[0].split(",")[0]
            elif any(term in key for term in ["products", "brands"]):
                items = [i.strip() for i in re.split(r",|\n", val) if i.strip()]
                if not items:
                    items = re.findall(r"[A-Z][a-zA-Z0-9\s]*(?=[A-Z]|$)", val)
                info["products"] = items
        return info
