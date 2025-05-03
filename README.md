# knowledge_graph_term
Term project and related assignments from group - Consumer Discretionary Sector
# Consumer Discretionary Sector Knowledge Graph
By Greg Roberts and Flavio Mota

## Overview of Project
This repository hosts a research and development effort to build a knowledge graph for the consumer discretionary sector. The graph integrates real‑time transaction records from a payments network, macroeconomic indicators, firm fundamentals, and qualitative context from regulatory filings and industry news. Nodes represent entities such as companies, product categories, consumer segments, economic indicators, transaction records, and data sources. Edges capture relationships extracted via named entity recognition and relationship extraction, enabling multi‑hop exploration of how spending patterns, macro signals, and firm attributes interact. Automated pipelines ingest data from indices, government surveys, financial APIs, web sources, and focused crawlers, then normalize and upsert this information into an EdgeDB schema designed for strong typing and graph semantics. A prototype dashboard and natural‑language interface demonstrate how users can pose complex queries to uncover competitive intelligence in seconds.

## Scope of Research Paper
The accompanying research paper is structured as a formal report with the following sections:

* **Abstract**  
  A concise summary of the topic, objectives, methodology, and work completed to date.  

* **Introduction**  
  Motivation for the study, target user groups (equity analysts, portfolio managers, marketing strategists, data science teams), and intended applications such as targeted stock recommendations and precision marketing insights.  

* **Literature Review**  
  Survey of prior work in knowledge graph construction in domains like biomedical research, corporate network analysis, and RAG augmented retrieval systems. Discussion of best practices in ontology design and graph database implementation.  

* **Methods**  
  Detailed description of how the five core research questions are addressed:  
  * Topic selection rationale based on economic cycle sensitivity and access to transaction data  
  * EdgeDB schema design guided by RDF Schema principles with defined node and edge types  
  * Automated ingestion pipelines for indices, surveys, APIs, web sources, and filings  
  * Identification of sample user queries and personas  
  * Application stack architecture including interactive graph exploration, RAG‑powered chatbot, and recommendation engine  

* **Results**  
  Findings from initial data ingestion and schema trials, utility of each data source in populating the graph, emergence of new node types through cluster analysis, and early visualizations demonstrating multi‑hop query performance.  

* **Conclusions**  
  Reflection on how the collected data and graph schema address the management problem of competitive intelligence in the consumer discretionary sector, considerations for entity resolution and data governance, and next steps to scale and maintain the knowledge base.

## Repository Structure
* `schema/`  
  EdgeDB schema definitions  
* `pipelines/`  
  Scrapy spiders and ETL scripts for data ingestion  
* `docs/`  
  Research paper draft and supplementary materials  
* `dashboard/`  
  Prototype graph exploration and query interface  

## Data Sources
* Fiserv Small Business Index  
* BEA consumer expenditure surveys  
* U.S. Census Bureau retail sales reports  
* Federal Reserve Economic Data APIs  
* Wikipedia sector constituent lists  
* Yahoo Finance real‑time price and fundamental data  
* SEC EDGAR filings  
* Industry news via focused crawler
