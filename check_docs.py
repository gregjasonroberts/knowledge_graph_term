# inspect_docs.py
import asyncio
import edgedb

async def main():
    # ─── Hard‑coded connection info ────────────────────────────────
    user     = "admin"
    password = "BYCEoMRWBTaTkoDMd13dDL7K"
    host     = "localhost"
    port     = 10701
    dbname   = "WebFocusedCrawlWork"   # <-- the branch where your data lives

    # Build a valid DSN for the Python client (no tls_ca_file, just skip verification)
    dsn = f"edgedb://{user}:{password}@{host}:{port}/{dbname}?tls_security=insecure"
    print(f"Connecting with DSN: {dsn}\n")

    # Create the client, skipping cert checks
    client = edgedb.create_async_client(dsn=dsn, tls_security="insecure")

    # 1) Total count
    count = await client.query_single("SELECT count(default::Document);")
    print(f"Total documents ingested: {count}\n")

    # 2) Sample the first 5
    print("Sample documents:")
    docs = await client.query("""
        SELECT default::Document { text }
        ORDER BY .id
        LIMIT 5;
    """)
    for i, doc in enumerate(docs, 1):
        snippet = doc.text.replace("\n", " ")[:120]
        print(f"{i}. {snippet}…\n")

    await client.aclose()

if __name__ == "__main__":
    asyncio.run(main())
