# fsbi_loader.py
import csv
from datetime import datetime

class FSBILoader:
    """
    Reads an FSBI CSV (comma- or tab-delimited), normalizes dates,
    writes records, and links each index to its Industry.
    """
    def __init__(self, csv_path):
        self.csv_path = csv_path

    def store_csv(self, handler):
        with open(self.csv_path, encoding="utf-8-sig", newline="") as f:
            sample = f.read(1024)
            f.seek(0)
            # auto-detect comma vs tab
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",\t")
            except csv.Error:
                dialect = csv.get_dialect("excel")
            reader = csv.DictReader(f, dialect=dialect)

            for row in reader:
                # grab the Period field (skip if missing)
                period = row.get("Period") or row.get("period")
                if not period:
                    print(f"⚠️ Skipping row with no Period: {row}")
                    continue

                # parse YYYYMMDD → YYYY-MM-DD
                try:
                    date = datetime.strptime(period, "%Y%m%d")\
                                   .strftime("%Y-%m-%d")
                except ValueError:
                    print(f"⚠️ Invalid Period format '{period}'")
                    continue

                # build your index key
                sector  = (row.get("Sector Name") or "").strip()
                subsec  = (row.get("Sub-Sector Name") or "").strip()
                index_id = f"{sector}::{subsec}"

                # parse each metric (default to 0.0)
                sales_idx     = float(row.get("Sales Index - SA", 0) or 0)
                trans_idx     = float(row.get("Transactional Index - SA", 0) or 0)
                sales_mom     = float(row.get("Sales MOM % - SA", 0) or 0)
                sales_yoy     = float(row.get("Sales YOY % - SA", 0) or 0)
                trans_mom     = float(row.get("Transaction MOM % - SA", 0) or 0)
                trans_yoy     = float(row.get("Transaction YOY %  - SA", 0) or 0)

                # 1) store the raw FSBI record
                handler.store_fsbi_record(
                    index_id=index_id,
                    date=date,
                    sales_index=sales_idx,
                    transaction_index=trans_idx,
                    sales_mom_pct=sales_mom,
                    sales_yoy_pct=sales_yoy,
                    trans_mom_pct=trans_mom,
                    trans_yoy_pct=trans_yoy
                )

                # 2) link the index to its Industry
                handler._write(
                    """
                    MERGE (idx:FSBIIndex {id: $index_id})
                    MERGE (i:Industry     {name: $sector})
                    MERGE (idx)-[:AFFECTS_INDUSTRY]->(i)
                    """,
                    {"index_id": index_id, "sector": sector}
                )
