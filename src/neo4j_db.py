#neo4j_db.py

# from neo4j import GraphDatabase
from neo4j import GraphDatabase, basic_auth

import os

class Neo4jHandler:
    def __init__(self, uri=None, user=None, password=None, database="neo4j"):
        self.uri = uri or os.environ.get("NEO4J_URI")
        self.user = user or os.environ.get("NEO4J_USER")
        self.password = password or os.environ.get("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(
            self.uri,
            auth=basic_auth(self.user, self.password)
        )


        self.database = database

    def close(self):
        self.driver.close()

    def store_document(self, doc):
        query = """
        MERGE (d:Document {id: $id})
        SET d.text = $text,
            d.symbol = $symbol,
            d.tags = $tags
        """
        self._write(query, doc)

    def create_company_kg_entry(self, info):
        query = """
        MERGE (c:Company {symbol: $symbol})
        ON CREATE SET c.name = $company_name, c.type = coalesce($company_type, "")
        SET c.name = $company_name

        FOREACH (_ IN CASE WHEN $industry IS NOT NULL THEN [1] ELSE [] END |
            MERGE (i:Industry {name: $industry})
            MERGE (c)-[:PART_OF_INDUSTRY]->(i)
        )

        FOREACH (prod IN $products |
            MERGE (p:Product {name: prod})
            MERGE (c)-[:PRODUCTS]->(p)
        )

        FOREACH (_ IN CASE WHEN $ceo IS NOT NULL THEN [1] ELSE [] END |
            MERGE (ceo:Person {name: $ceo})
            MERGE (c)-[:HAS_EMPLOYEE {role: "CEO"}]->(ceo)
        )
        """
        self._write(query, info)

    def store_index_metric(self, index_id, date, value):
        query = """
        MERGE (idx:Index {id: $index_id})
        MERGE (rec:IndexMetric {index_id: $index_id, date: $date})
        SET rec.value = $value
        MERGE (rec)-[:OF_INDEX]->(idx)
        """
        params = {"index_id": index_id, "date": date, "value": value}
        self._write(query, params)

    def store_fsbi_record(
        self,
        index_id,
        date,
        sales_index,
        transaction_index,
        sales_mom_pct,
        sales_yoy_pct,
        trans_mom_pct,
        trans_yoy_pct
    ):
        query = """
        MERGE (idx:FSBIIndex {id: $index_id})
        MERGE (rec:FSBIRecord {index_id: $index_id, date: $date})
        SET rec.sales_index       = $sales_index,
            rec.transaction_index = $transaction_index,
            rec.sales_mom_pct     = $sales_mom_pct,
            rec.sales_yoy_pct     = $sales_yoy_pct,
            rec.trans_mom_pct     = $trans_mom_pct,
            rec.trans_yoy_pct     = $trans_yoy_pct
        MERGE (rec)-[:OF_INDEX]->(idx)
        """
        params = {
            "index_id": index_id,
            "date": date,
            "sales_index": sales_index,
            "transaction_index": transaction_index,
            "sales_mom_pct": sales_mom_pct,
            "sales_yoy_pct": sales_yoy_pct,
            "trans_mom_pct": trans_mom_pct,
            "trans_yoy_pct": trans_yoy_pct
        }
        self._write(query, params)

    def store_indicator(self, indicator_id, date, value):
        query = """
        MERGE (ind:Indicator {id: $indicator_id})
        MERGE (rec:IndicatorRecord {indicator_id: $indicator_id, date: $date})
        SET rec.value = $value
        MERGE (rec)-[:OF_INDICATOR]->(ind)
        """
        params = {"indicator_id": indicator_id, "date": date, "value": value}
        self._write(query, params)

    def store_filing(self, symbol, filing):
        query = """
        MERGE (c:Company {symbol: $symbol})
        MERGE (f:Filing {accession_number: $accessionNumber})
        SET f.form_type = $formType, f.filing_date = $filedAt
        MERGE (c)-[:FILED]->(f)
        """
        self._write(query, {"symbol": symbol, **filing})

    def store_subsidiary(self, parent_symbol, sub_name):
        query = """
        MERGE (p:Company {symbol: $parent_symbol})
        MERGE (s:Company {company_name: $sub_name})
        MERGE (p)-[:OWNS]->(s)
        """
        params = {"parent_symbol": parent_symbol, "sub_name": sub_name}
        self._write(query, params)

    def store_stock_return(self, symbol, date, value):
        query = """
        MERGE (c:Company {symbol: $symbol})
        MERGE (r:StockReturn {symbol: $symbol, date: $date})
        SET r.value = $value
        MERGE (r)-[:OF_COMPANY]->(c)
        """
        self._write(query, {"symbol": symbol, "date": date, "value": value})

    def _write(self, query, params):
        with self.driver.session(database=self.database) as session:
            session.write_transaction(lambda tx: tx.run(query, **params))

    def link_document_to_company(self, doc_id, symbol):
        """
        After creating a Document and a Company, link them.
        """
        query = """
        MATCH (d:Document {id: $id})
        MERGE (c:Company  {symbol: $symbol})
        MERGE (d)-[:DESCRIBES]->(c)
        """
        params = {"id": doc_id, "symbol": symbol}
        self._write(query, params)

    def link_document_to_industry(self, doc_id, industry):
        """
        Optionally anchor each Document into its Industry.
        """
        query = """
        MATCH (d:Document {id: $id})
        MERGE (i:Industry {name: $industry})
        MERGE (d)-[:CONTEXTUALIZES]->(i)
        """
        params = {"id": doc_id, "industry": industry}
        self._write(query, params)

    def link_indicator_to_macro(self, indicator_id):
        """
        Ensures every Indicator is connected under a single Macro node.
        """
        query = """
        MERGE (m:Macro {name: 'GlobalEconomy'})
        MERGE (ind:Indicator {id: $indicator_id})
        MERGE (m)-[:TRACKS]->(ind)
        """
        self._write(query, {"indicator_id": indicator_id})
    
