# inspect_docs.py
import asyncio
import edgedb
from edgedb.errors import SchemaError

async def main():
    # ─── Connection info ───────────────────────────────────────────
    user     = "admin"
    password = "BYCEoMRWBTaTkoDMd13dDL7K"
    host     = "localhost"
    port     = 10701
    dbname   = "main"  # <-- the branch where your data lives

    dsn = f"edgedb://{user}:{password}@{host}:{port}/{dbname}?tls_security=insecure"
    print(f"Connecting with DSN: {dsn}\n")

    client = edgedb.create_async_client(dsn=dsn, tls_security="insecure")

    # ─── 0) Ensure schema exists ────────────────────────────────────
    try:
        await client.execute(r"""
            CREATE TYPE default::Document {
              CREATE REQUIRED PROPERTY id -> uuid {
                SET DEFAULT := <uuid>uuid_generate_v4();
              };
              CREATE REQUIRED PROPERTY text -> str;
              CREATE MULTI PROPERTY embedding -> array<float32>;
            };
        """)
        print("✅ Created default::Document type.\n")
    except SchemaError as e:
        if "already exists" in str(e):
            print("ℹ️  default::Document already exists, skipping creation.\n")
        else:
            raise

    # ─── 1) Total count ────────────────────────────────────────────
    try:
        count = await client.query_single("SELECT count(default::Document);")
        print(f"Total documents ingested: {count}\n")
    except Exception as e:
        print("❌ Failed to count documents:", e)
        await client.aclose()
        return

    # ─── 2) Sample a few ───────────────────────────────────────────
    try:
        docs = await client.query("""
            SELECT default::Document { text }
            ORDER BY .id
            LIMIT 5;
        """)
        print("Sample documents:")
        for i, doc in enumerate(docs, start=1):
            snippet = doc.text.replace("\n", " ")[:120]
            print(f"{i}. {snippet}…\n")
    except Exception as e:
        print("❌ Failed to fetch samples:", e)

    await client.aclose()

if __name__ == "__main__":
    asyncio.run(main())
