import pandas as pd
import re
from neo4j import GraphDatabase


class PerpetratorImporter:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def import_perpetrators(self, csv_path):
        df = pd.read_csv(csv_path)

        with self.driver.session() as session:
            for index, row in df.iterrows():
                session.execute_write(self._create_perpetrator_and_relationships, row)

    @staticmethod
    def _create_perpetrator_and_relationships(tx, row):
        # Create Perpetrator node
        perp = tx.run(
            "CREATE (p:Perpetrator {yearOfRegistration: $yearOfRegistration, gender: $gender, ageBroad: $ageBroad}) RETURN id(p)",
            yearOfRegistration=row['yearRegister'], gender=row['IP_Gender'], ageBroad=row['IP_ageBroad']
        ).single()[0]

        # Create CITIZEN_OF relationship with Continent
        # Handle multiple continents
        if pd.notna(row['IP_citizen_UNRegion']):
            continents = re.split(';|/', row['IP_citizen_UNRegion'])
            for continent in continents:
                continent = continent.strip()  # Remove any leading/trailing whitespace
                tx.run(
                    "MATCH (p:Perpetrator), (ct:ContinentalRegion {name: $continent}) WHERE id(p) = $perp_id "
                    "MERGE (p)-[:CITIZEN_OF]->(ct)",
                    perp_id=perp, continent=continent
                )

        # Mapping new categories to existing recruiterRelation types
        recruiter_map = {
            'StrangerUnknownOther': ['Other'],
            'FriendAcquaintance': ['Friend'],
            'FamilyIntimatePartner': ['Family', 'IntimatePartner']
            # Add more mappings if needed
        }

        # Create relationship with recruiterRelation
        if pd.notna(row['IP_Relation']):
            ip_relations = re.split(';', row['IP_Relation'])
            for ip_relation in ip_relations:
                ip_relation = ip_relation.strip()
                recruiter_types = recruiter_map.get(ip_relation, '')
                for recruiter_type in recruiter_types:
                    tx.run(
                        "MATCH (p:Perpetrator) WHERE id(p) = $perp_id "
                        "MATCH (r:recruiterRelation {type: $recruiter_type}) "
                        "MERGE (p)-[:IDENTIFIED_AS]->(r)",
                        perp_id=perp, recruiter_type=recruiter_type
                    )


# Usage example
importer = PerpetratorImporter("neo4j://localhost:7687", "username", "password")
importer.import_perpetrators('CTDC_VPsynthetic_condensed.csv')
importer.close()
