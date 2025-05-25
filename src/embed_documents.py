# embed_documents.py
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
import os

# Load environment variables if needed
# from dotenv import load_dotenv
# load_dotenv()

# Neo4j connection parameters from environment or defaults
URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
USER = os.environ.get("NEO4J_USER", "neo4j")
PASS = os.environ.get("NEO4J_PASSWORD", "password")

# Initialize the embedding model
model = SentenceTransformer("all-mpnet-base-v2")

# Connect to Neo4j
# Connect to Neo4j without authentication (password disabled)
driver = GraphDatabase.driver(URI)

with driver.session() as session:
    # Fetch all documents without embeddings
    results = session.run(
        "MATCH (d:Document) WHERE d.embedding IS NULL RETURN d.id AS id, d.text AS text"
    )
    for record in results:
        doc_id = record["id"]
        text = record["text"]
        # Generate embedding
        emb = model.encode(text)
        # Write back to Neo4j
        session.run(
            "MATCH (d:Document {id:$id}) SET d.embedding = $emb",
            id=doc_id,
            emb=emb.tolist()
        )

driver.close()
print("✅ Document embeddings generated and stored.")
