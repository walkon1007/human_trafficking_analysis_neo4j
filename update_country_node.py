import pandas as pd
from neo4j import GraphDatabase


class CountryUpdater:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def update_countries_and_regions(self, excel_path, sheet_name):
        df = pd.read_excel(excel_path, sheet_name=sheet_name, engine='openpyxl')

        # Extract unique continental regions
        continental_regions = df['UNRegion'].unique()

        with self.driver.session() as session:
            # Create ContinentalRegion nodes
            for region in continental_regions:
                if pd.notna(region):  # Check for NaN values
                    session.execute_write(self._merge_continental_region, region)

            # Update Country nodes with UNSubRegion
            for index, row in df.iterrows():
                name = row['ISO3']
                full_name = row['Country']
                sub_region = row['UNSubRegion']
                if pd.notna(name) and pd.notna(sub_region):
                    session.execute_write(self._add_unsubregion_to_country, name, full_name, sub_region)

    def create_country_continent_relationships(self, excel_path, sheet_name):
        df = pd.read_excel(excel_path, sheet_name=sheet_name, engine='openpyxl')

        with self.driver.session() as session:
            for index, row in df.iterrows():
                country_name = row['ISO3']  # Adjust if necessary
                continent_name = row['UNRegion']  # Adjust if necessary
                if pd.notna(country_name) and pd.notna(continent_name):
                    session.execute_write(self._create_located_at_relationship, country_name, continent_name)

    @staticmethod
    def _merge_continental_region(tx, region_name):
        tx.run(
            "MERGE (:ContinentalRegion {name: $name})",
            name=region_name
        )

    @staticmethod
    def _add_unsubregion_to_country(tx, name, full_name, sub_region):
        tx.run(
            "MATCH (c:Country {name: $name}) "
            "SET c.full_name = $full_name,"
            "c.UNSubRegion = $sub_region",
            name=name, full_name=full_name, sub_region=sub_region
        )

    @staticmethod
    def _create_located_at_relationship(tx, country_name, continent_name):
        tx.run(
            "MATCH (c:Country {name: $country_name}), (ct:ContinentalRegion {name: $continent_name}) "
            "MERGE (c)-[:LOCATED_AT]->(ct)",
            country_name=country_name, continent_name=continent_name
        )

# Usage example
updater = CountryUpdater("neo4j://localhost:7687", "", "")
updater.update_countries_and_regions('CTDC_VPsynthetic_dict_20221201.xlsx', 'Region')
updater.create_country_continent_relationships('CTDC_VPsynthetic_dict_20221201.xlsx', 'Region')
updater.close()
