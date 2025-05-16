from neo4j import GraphDatabase

class Neo4jHandler:
    def __init__(self):
        self.driver = GraphDatabase.driver("bolt://localhost:7687")
        self.database = "neo4j"

    def store_document(self, doc):
        query = """
        MERGE (d:Document {id: $id})
        SET d.text = $text, d.symbol = $symbol, d.tags = $tags
        """
        with self.driver.session(database=self.database) as session:
            session.run(query, doc)

    def create_company_kg_entry(self, company_info):
        query = """
        MERGE (c:Company {symbol: $symbol})
          ON CREATE SET c.name = $company_name, c.type = $company_type

        MERGE (i:Industry {name: $industry})
        MERGE (c)-[:PART_OF_INDUSTRY]->(i)

        MERGE (p:Product {name: $product})
        MERGE (c)-[:OFFERS]->(p)

        MERGE (ceo:Person {name: $ceo_name})
        MERGE (c)-[:HAS_EMPLOYEE {role: "CEO"}]->(ceo)
        """
        with self.driver.session(database=self.database) as session:
            session.run(query, company_info)

    def close(self):
        self.driver.close()
