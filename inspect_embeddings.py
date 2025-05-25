#inspect_embeddings.py

import os
from neo4j import GraphDatabase
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# 1) Connection params
URI  = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
USER = os.environ.get("NEO4J_USER", None)
PASS = os.environ.get("NEO4J_PASSWORD", None)

if USER and PASS:
    driver = GraphDatabase.driver(URI, auth=(USER, PASS))
else:
    driver = GraphDatabase.driver(URI)

# 2) Fetch all embeddings
with driver.session() as session:
    result = session.run(
        """
        MATCH (d:Document)
        WHERE d.embedding IS NOT NULL
        RETURN d.symbol AS symbol, d.embedding AS emb
        """
    )
    raw = [(r["symbol"], np.array(r["emb"])) for r in result]

driver.close()

# 3) Deduplicate by symbol, keeping first occurrence
unique = {}
for sym, vec in raw:
    if sym not in unique:
        unique[sym] = vec

symbols = list(unique.keys())
embs    = np.vstack(list(unique.values()))

# 4) Build a DataFrame summary
df = pd.DataFrame({
    "symbol": symbols,
    "dim":    [v.shape[0] for v in embs],
    "mean":   [v.mean()     for v in embs],
    "std":    [v.std()      for v in embs],
})

print("\nEmbedding summary (first 10 rows):")
print(df.head(10).to_string(index=False))

# 5) Nearest‐neighbor check with safe anchor choice
anchor = "AMZN"
if anchor not in symbols:
    print(f"\n⚠️ Anchor `{anchor}` not found. Available tickers: {symbols[:10]}")
    anchor = symbols[0]
    print(f"Using `{anchor}` as the anchor instead.\n")

idx = symbols.index(anchor)
sim = cosine_similarity(embs)
neighbors = np.argsort(-sim[idx])[1:6]

print(f"\nTop 5 neighbors of {anchor}:")
for j in neighbors:
    print(f"  {symbols[j]}  —  sim={sim[idx,j]:.4f}")
