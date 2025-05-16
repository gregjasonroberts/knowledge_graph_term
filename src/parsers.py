from bs4 import BeautifulSoup
import uuid
import re

class DocumentParser:
    """
    Turns each scraped item dict (with 'html') into structured dicts.
    """
    def parse(self, raw_item):
        html = raw_item.get("html")
        symbol = raw_item.get("symbol", "")
        tags = raw_item.get("tags", [])

        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")

        # Extract first valid paragraph
        p_tags = soup.select("#mw-content-text p")
        text = ""
        for tag in p_tags:
            candidate = tag.get_text(strip=True)
            if candidate:
                text = candidate
                break

        if not text:
            print("⚠️ No valid <p> text found.")
            return []

        # Structured data from infobox
        infobox = soup.select_one("table.infobox")
        company_name = None
        ceo = None
        headquarters = None
        industry = None
        brands = []

        if infobox:
            rows = infobox.select("tr")
            for row in rows:
                header = row.select_one("th")
                data = row.select_one("td")
                if not header or not data:
                    continue

                key = header.get_text(strip=True).lower()
                val = data.get_text(strip=True)
                print("🧾 Infobox field:", key)

                if "name" in key:
                    company_name = val
                elif "headquarter" in key:
                    headquarters = val
                elif any(term in key for term in ["industry", "type", "sector", "category"]):
                    industry = val
                elif "key people" in key or "ceo" in key:
                    ceo = val.split("–")[0].split(",")[0]
                elif "products" in key or "brands" in key:
                    if "," in val:
                        items = [x.strip() for x in val.split(",") if x.strip()]
                    else:
                        items = re.findall(r'[A-Z][a-zA-Z0-9\s]*(?=[A-Z]|$)', val)
                    brands.extend(items)

        return [{
            "id": str(uuid.uuid4()),
            "text": text,
            "symbol": symbol,
            "tags": tags,
            "company_name": company_name or symbol,
            "ceo_name": ceo,
            "headquarters": headquarters,
            "industry": industry,
            "product": brands if brands else [] 
        }]