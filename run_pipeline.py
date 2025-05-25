# run_pipeline.py
# from dotenv import load_dotenv
import subprocess
import sys
from pipelines import DataPipeline

# Load environment variables from .env (if present)
# load_dotenv()

# Install dependencies
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

if __name__ == "__main__":
    print("🧪 Script started running...")
    try:
        # Initialize pipeline with paths to your CSVs (relative to working dir)
        dp = DataPipeline(
            ticker_csv_file="consumer_discretionary_sites.csv",
            fsbi_csv_file="fsbi_data_010122_040125.csv"
        )
        num_stored = dp.fetch_and_store_all()
        print(f"✅ Pipeline finished successfully. Stored {num_stored} document(s) in Neo4j.")
    except Exception as e:
        print(f"❌ Pipeline failed with error: {e}")
