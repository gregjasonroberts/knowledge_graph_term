# fsbi_loader.py
import csv
from datetime import datetime

class FSBILoader:
    """
    Reads FSBI sector CSV and writes records into Neo4j.
    """
    def __init__(self, csv_path):
        self.csv_path = csv_path

    def store_csv(self, handler):
        """
        For each row in the FSBI CSV:
        - Normalize date
        - Build an index_id from Sector + Sub-Sector
        - Store all metrics into Neo4j
        """
        with open(self.csv_path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f, delimiter="	")  # adjust delimiter if needed
            for row in reader:
                # Normalize the date
                period = row.get("Period")  # e.g. "20220101"
                date = datetime.strptime(period, "%Y%m%d").strftime("%Y-%m-%d")

                # Build index key from sector and sub-sector
                sector = row.get("Sector Name", "").strip()
                subsec = row.get("Sub-Sector Name", "").strip()
                index_id = f"{sector}::{subsec}"

                # Parse metrics
                sales_idx       = float(row.get("Sales Index - SA", 0))
                trans_idx       = float(row.get("Transactional Index - SA", 0))
                sales_mom_pct   = float(row.get("Sales MOM % - SA", 0))
                sales_yoy_pct   = float(row.get("Sales YOY % - SA", 0))
                trans_mom_pct   = float(row.get("Transaction MOM % - SA", 0))
                trans_yoy_pct   = float(row.get("Transaction YOY %  - SA", 0))

                # Persist into Neo4j via handler
                handler.store_fsbi_record(
                    index_id=index_id,
                    date=date,
                    sales_index=sales_idx,
                    transaction_index=trans_idx,
                    sales_mom_pct=sales_mom_pct,
                    sales_yoy_pct=sales_yoy_pct,
                    trans_mom_pct=trans_mom_pct,
                    trans_yoy_pct=trans_yoy_pct
                )