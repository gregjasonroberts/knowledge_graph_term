# run_pipeline.py

import os
from pipelines import DataPipeline

print("🧪 Script started running...")

if __name__ == "__main__":
    try:
        print("📦 Starting data pipeline…")
        # 1) This file is in .../my-repo/src/run_pipeline.py
        script_dir   = os.path.dirname(os.path.abspath(__file__))
        # 2) Go up from src/ to my-repo/
        repo_dir     = os.path.dirname(script_dir)
        # 3) Go up again from my-repo/ to WebFocusedCrawlWork/
        project_root = os.path.dirname(repo_dir)

        # 4) Now point at the CSVs sitting in WebFocusedCrawlWork/
        # ticker_csv = os.path.join(project_root, "consumer_discretionary_sites.csv")
        # fsbi_csv   = os.path.join(project_root, "fsbi_data_010122_040125.csv")
        
        #for colab, use absolute paths
        ticker_csv = "/content/drive/My Drive/Colab Notebooks/MSDS459_Final_Project/consumer_discretionary_sites.csv"
        fsbi_csv = "/content/drive/My Drive/Colab Notebooks/MSDS459_Final_Project/fsbi_data_010122_040125.csv"


        pipeline = DataPipeline(
            csv_path=ticker_csv,
            fsbi_csv_path=fsbi_csv
        )
        num_stored = pipeline.fetch_and_store_all()
        print(f"✅ Pipeline finished successfully. Stored {num_stored} document(s) in Neo4j.")
    except Exception as e:
        print(f"❌ Pipeline failed with error: {e}")
