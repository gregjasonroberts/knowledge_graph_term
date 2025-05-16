# run_pipeline.py
from pipelines import DataPipeline

print("🧪 Script started running...")

if __name__ == "__main__":
    try:
        print("📦 Starting data pipeline...")
        pipeline = DataPipeline(csv_path="consumer_discretionary_sites.csv")
        num_stored = pipeline.fetch_and_store_all()
        print(f"✅ Pipeline finished successfully. Stored {num_stored} document(s) in Neo4j.")
    except Exception as e:
        print(f"❌ Pipeline failed with error: {e}")
