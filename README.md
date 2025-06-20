# Consumer Discretionary Knowledge Graph

## Overview

This repository hosts an extensible, data‑rich knowledge graph for the consumer discretionary sector, built in Neo4j. It combines a manually curated list of **10** core companies and a structured product taxonomy with programmatic ingestion of market indices, financial metrics, macroeconomic series, and corporate documents. The graph enables competitive‑intelligence queries and supports retrieval‑augmented generation (RAG) for natural‑language analytics.

## Data Ingestion & Graph Construction

Our knowledge base ingests **five distinct data streams** and unifies them in Neo4j. A custom `DocumentParser` class normalizes scraped and parsed sources into Python dictionaries, and relationships are anchored to company, industry, and macro nodes.

1. **Textual Documents**: Wikipedia Infoboxes & Articles

   * Scrape each company’s Wikipedia page with BeautifulSoup, extracting infobox fields (e.g., name, CEO, headquarters, industry) and the first valid paragraph of body text.
   * Parse and normalize into `Document` nodes using `DocumentParser`.

2. **Market Indices & Financial Metrics** (Future work)

   * Fetch historical index values (e.g., S\&P 500, Dow Jones Consumer Discretionary) and key financial ratios (revenue, market cap, P/E, EBITDA) via the Yahoo Finance API and official index providers.
   * Store in `Index` nodes with related `IndexPoint` children and link metrics (`FinancialMetric`) to `Company` nodes.

3. **Macroeconomic Time Series**

   * Ingest U.S. time series from FRED: Personal Consumption Expenditures (PCE), Consumer Price Index (CPI), and Leading Economic Indicators (LEI).
   * Persist under `SpendingSeries` and `SpendingPoint` nodes.

4. **Corporate Filings**: SEC EDGAR 10‑K / 8‑K  (Future data source)

   * Retrieve the three most recent annual and quarterly filings per ticker via the SEC EDGAR API.
   * Parse XBRL metadata and HTML sections, storing metadata (`type`, `date`, `url`) and linking each `Document` node to its `Company` and, optionally, `Industry`.
  
5. **Business New Sentiment Analysis**
   * Retrieve news articles with the web automation library `playwright` developed by Microsoft that can control web browsers like Chromium, Firefox, and WebKit.
   * Articles were scraped with asynch_playwright and the sentiment was determined by financial BerTokenizer model called FinBERT.
   * The model returned probabilities for negative, neutral and positive and the weighted average for each company was saved to a csv.

## Data Sources

* **Manual Curation**
  CSV of 10 consumer‑discretionary companies (symbol, name, sector) and JSON taxonomies for products and subcategories.

* **APIs**

  * **FRED**: PCE, CPI, LEI series.
  * **Fiserv FSBI**: Monthly small‑business index for consumer discretionary.
  * **Yahoo Finance**: Company financial metrics via `yfinance`.

* **Web Scraping**

  * **Wikipedia**: Infobox data and article intros via BeautifulSoup & `DocumentParser`.
  * **Yahoo Finace News**:  News articles aggregated by Yahoo Finance and scraped with BeautifulSoup for sentiment scoring with FinBERT transformer.
  * **SEC EDGAR**: 10‑K / 8‑K filings parsed through XBRL and HTML parsing.

## Graph Schema

### Node Labels & Properties

* **Company**: `symbol`, `name`, `sector`, `CEO`, `headquarters`
* **Industry**: `name`
* **Product**: `category`, `subcategory`
* **Index**: `name` & **IndexPoint**: `date`, `value`
* **SpendingSeries**: `series_name` & **SpendingPoint**: `date`, `value`
* **Document**: `id`, `type`, `date`, `url`, `tags`
* **FinancialMetric**: `metric_name`, `value`, `date`
* **Sentiment**: `date`, `score`, `source`

### Relationships

```
(c:Company)-[:PART_OF_INDUSTRY]->(i:Industry)
(c:Company)-[:OFFERS]->(p:Product)
(idx:Index)-[:HAS_POINT]->(pt:IndexPoint)
(ss:SpendingSeries)-[:MEASURED_AT]->(sp:SpendingPoint)
(c:Company)-[:HAS_METRIC]->(m:FinancialMetric)
(d:Document)-[:RELATED_TO]->(c:Company)
(d:Document)-[:ANCHOR_INDUSTRY]->(i:Industry)
```

Documents can optionally be anchored to their industry nodes for richer context.

## Pipeline Components

This project breaks down into discrete scripts located under `scripts/` that can be run independently or orchestrated together.

| Script                        | Description                                                                                          |
|-------------------------------|------------------------------------------------------------------------------------------------------|
| `scripts/parsers.py`          | Normalize raw scraped sources (Wikipedia or EDGAR filings) into intermediate JSON for downstream use. |
| `scripts/fred_loader.py`      | Ingest FRED economic series (PCE, CPI, LEI) into the processed dataset.                             |
| `scripts/fsbi_loader.py`      | Load Fiserv FSBI consumer-discretionary small-business index values.                                 |
| `scripts/stock_loader.py`     | Fetch company financial metrics (closing price, revenue, market cap, P/E, EBITDA) via Yahoo Finance.               |
| `scripts/embed_documents.py`  | Generate vector embeddings for Document and Entity nodes using a transformer model and store them as properties on those nodes in Neo4j.|
| `scripts/neo4j_db.py`         | Provide Neo4j connection utilities and helper functions for node/relationship creation.              |
| `scripts/pipelines.py`        | Define and sequence the ETL stages (ingest -> transform -> load -> embed) as a dependency graph.        |
| `scripts/run_pipeline.py`     | CLI entrypoint that executes the full ETL -> Neo4j load -> embedding pipeline in one command.         |



## Configuration

* Other requirements and API keys:
  * openai for future use, currently applying a free transformer and API wrapper from Huggingface: SentenceTransfomer with `all-mpnet-base-v2`
  ```
  FRED_API_KEY=<your_fred_key>
  EDGAR_API_KEY=<your_edgar_key>
  OPENAI_API_KEY=<your_openai_key>
  NEO4J_URI
  ```
* Adjust Neo4j connection settings in `config.yml`.

---

*Last updated: June 2025*
