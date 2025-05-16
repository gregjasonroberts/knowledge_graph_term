# Consumer Discretionary Knowledge Graph

## Overview

This repository hosts an extensible, data‑rich knowledge graph for the consumer discretionary sector, built in Neo4j. It combines a manually curated list of **10** core companies and a structured product taxonomy with programmatic ingestion of market indices, financial metrics, macroeconomic series, and corporate documents. The graph enables competitive‑intelligence queries and supports retrieval‑augmented generation (RAG) for natural‑language analytics.

## Objectives

* Integrate and normalize heterogeneous data sources for publicly traded consumer discretionary companies.
* Maintain raw and processed data for auditability and reusability under version control.
* Centralize entities, relationships, and embeddings in Neo4j for graph queries and analytics.
* Provide a RAG interface combining graph traversals and vector similarity search to answer business questions.

## Architecture

1. **Data Ingestion**

   * Python scripts and Scrapy spiders fetch data from APIs, web pages, and file drops on a regular schedule.

2. **Raw Data Storage**

   * Persist unmodified JSON, CSV, and HTML outputs in `/data/raw` for full audit trails and reprocessing.

3. **Transformation & Enrichment**

   * Pandas‑based ETL cleans, normalizes, and enriches records, writing outputs to `/data/processed`.

4. **Graph Database Layer**

   * **Neo4j** manages entities, relationships, and vector indexes.
   * **Embeddings**: Document and entity vectors stored as node properties; Neo4j Graph Data Science library enables k‑NN and similarity queries.

5. **Embedding Generation**

   * Batch Python jobs call the OpenAI API to compute embeddings, then attach vectors to nodes in Neo4j.

6. **RAG Pipeline**

   * LangChain chains combine Cypher queries and embedding‑based similarity search to serve natural‑language answers via FastAPI.

## Data Sources

* **Manual Curation**: CSV of 10 consumer‑discretionary companies (symbol, name, sector); JSON taxonomies for products and subcategories.

* **APIs**:

  * **FRED**: U.S. consumer‑spending series (Retail Trade, Food Services, etc.).
  * **Fiserv FSBI**: Monthly small‑business index values for consumer discretionary.
  * **Yahoo Finance**: Financial metrics (revenue, market capitalization, P/E ratio, EBITDA).

* **Web Scraping**:

  * **Wikipedia**: Company profiles (CEO, headquarters, founding date, sector classification).
  * **EDGAR Filings**: 10‑K and 8‑K metadata (type, date, URL) parsed via BeautifulSoup.

## Graph Schema

### Node Labels & Key Properties

* **Company**: `symbol`, `name`, `sector`, `CEO`, `headquarters`
* **Industry**: `name`
* **Product**: `category`, `subcategory`
* **Index**: `name`
* **IndexPoint**: `date`, `value`
* **SpendingSeries**: `seriesName`
* **SpendingPoint**: `date`, `value`
* **Document**: `type`, `date`, `url`

### Relationships

* `(c:Company)-[:PART_OF_INDUSTRY]->(i:Industry)`
* `(c:Company)-[:OFFERS]->(p:Product)`
* `(idx:Index)-[:HAS_POINT]->(pt:IndexPoint)`
* `(ss:SpendingSeries)-[:MEASURED_AT]->(sp:SpendingPoint)`
* `(c:Company)-[:HAS_METRIC]->(m:FinancialMetric)`
* `(d:Document)-[:RELATED_TO]->(c:Company)`

## Pipeline Components

1. **Ingest**

   ```bash
   python scripts/ingest.py
   ```

   Fetch and store raw data under `/data/raw`.

2. **Transform**

   ```bash
   python scripts/transform.py
   ```

   Clean, normalize, and output processed files to `/data/processed`.

3. **Load Neo4j**

   ```bash
   python scripts/load_neo4j.py
   ```

   Create nodes, relationships, and attach embeddings in Neo4j.

4. **RAG Service** - Not yet tested

   ```bash
   uvicorn app.main:app --reload
   ```

   Serve a FastAPI that merges graph queries with vector search for natural‑language responses.

## Getting Started

1. Clone the repository:

   ```bash
   git clone https://gitlab.com/<your-namespace>/consumer-discretionary-kg.git
   cd consumer-discretionary-kg
   ```

2. Configure environment:

   ```bash
   cp env.example .env
   ```

   Set `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, and `OPENAI_API_KEY`.

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the full pipeline following **Pipeline Components**.


