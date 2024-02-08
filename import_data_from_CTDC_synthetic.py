from neo4j import GraphDatabase
import csv


class TraffickingGraphModel:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_shared_nodes(self, file_path):
        # Extract unique values for each category from the file
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter='\t')
            countries = set()
            means_of_controls = set()
            forced_labours = set()
            sexual_exploits = set()
            recruiters = set()

            for row in reader:
                countries.add(row['citizenship'])
                countries.add(row['CountryOfExploitation'])
                # Add other values for means of control, forced labour, sexual exploit, recruiters, etc.
                # Assuming the presence of '1' indicates a truthy value
                for control in [
                    "DebtBondage", "TakesEarnings", "Threats", "PsychologicalAbuse",
                    "PhysicalAbuse", "SexualAbuse", "FalsePromises", "PsychoactiveSubstances",
                    "RestrictsMovement", "RestrictsMedicalCare", "ExcessiveWorkingHours", "ThreatOfLawEnforce",
                    "WithholdsNecessities", "WithholdsDocuments", "Other"
                ]:
                    if row.get(f"meansOfControl{control}") == '1':
                        means_of_controls.add(control)

                for labour_type in [
                    "Agriculture", "Construction", "DomesticWork", "Hospitality", "Other"
                ]:
                    if row.get(f"typeOfLabour{labour_type}") == '1':
                        forced_labours.add(labour_type)

                for exploit_type in [
                    "Prostitution", "Pornography", "Other"
                ]:
                    if row.get(f"typeOfSex{exploit_type}") == '1':
                        sexual_exploits.add(exploit_type)

                for recruiter_relation in [
                    "IntimatePartner", "Friend", "Family", "Other"
                ]:
                    if row.get(f"recruiterRelation{recruiter_relation}") == '1':
                        recruiters.add(recruiter_relation)

        # Now create the nodes in the database
        with self.driver.session() as session:
            session.execute_write(self._merge_countries, countries)
            session.execute_write(self._merge_means_of_controls, means_of_controls)
            session.execute_write(self._merge_forced_labours, forced_labours)
            session.execute_write(self._merge_sexual_exploits, sexual_exploits)
            session.execute_write(self._merge_recruiters, recruiters)

    def import_victim_nodes_and_relationships(self, file_path):
        with self.driver.session() as session:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter='\t')
                for row in reader:
                    session.execute_write(self._create_victim_and_relationships, row)

    @staticmethod
    def _merge_countries(tx, countries):
        for country in countries:
            if country:  # Ensure the country name is not empty
                tx.run("MERGE (:Country {name: $country})", country=country)

    @staticmethod
    def _merge_means_of_controls(tx, means_of_controls):
        for control in means_of_controls:
            if control:  # Ensure the control type is not empty
                tx.run("MERGE (:MeansOfControl {type: $control})", control=control)

    @staticmethod
    def _merge_forced_labours(tx, forced_labours):
        for labour_type in forced_labours:
            if labour_type:
                tx.run("MERGE (:typeOfLabour {type: $labour_type})", labour_type=labour_type)

    @staticmethod
    def _merge_sexual_exploits(tx, sexual_exploits):
        for exploit_type in sexual_exploits:
            if exploit_type:
                tx.run("MERGE (:typeOfSex {type: $exploit_type})", exploit_type=exploit_type)

    @staticmethod
    def _merge_recruiters(tx, recruiters):
        for recruiter_relation in recruiters:
            if recruiter_relation:
                tx.run("MERGE (:recruiterRelation {type: $recruiter_relation})", recruiter_relation=recruiter_relation)

    @staticmethod
    def _create_victim_and_relationships(tx, row):
        # Create Victim node
        victim_id = tx.run(
            "CREATE (v:Victim {yearOfRegistration: $yearOfRegistration, gender: $gender, "
            "ageBroad: $ageBroad, majorityStatusAtExploit: $majorityStatusAtExploit, "
            "traffickMonths: $traffickMonths}) RETURN id(v)",
            row
        ).single()[0]

        # Create relationships to Country nodes
        citizenship_country = row['citizenship']
        exploitation_country = row['CountryOfExploitation']
        if citizenship_country:
            tx.run(
                "MATCH (c:Country {name: $name}), (v:Victim) WHERE id(v) = $victim_id "
                "MERGE (v)-[:FROM_COUNTRY]->(c)",
                name=citizenship_country, victim_id=victim_id
            )
        if exploitation_country:
            tx.run(
                "MATCH (e:Country {name: $name}), (v:Victim) WHERE id(v) = $victim_id "
                "MERGE (v)-[:EXPLOITED_IN]->(e)",
                name=exploitation_country, victim_id=victim_id
            )

        # Create relationships to MeansOfControl nodes
        for control_type in [
            "DebtBondage", "TakesEarnings", "Threats", "PsychologicalAbuse",
            "PhysicalAbuse", "SexualAbuse", "FalsePromises", "PsychoactiveSubstances",
            "RestrictsMovement", "RestrictsMedicalCare", "ExcessiveWorkingHours",
            "ThreatOfLawEnforce", "WithholdsNecessities", "WithholdsDocuments", "Other"
        ]:
            if row.get(f"meansOfControl{control_type}") == '1':
                tx.run(
                    "MATCH (m:MeansOfControl {type: $type}), (v:Victim) WHERE id(v) = $victim_id "
                    "MERGE (v)-[:SUBJECTED_TO]->(m)",
                    type=control_type, victim_id=victim_id
                )

        # Create relationships to typeOfLabour nodes
        for labour_type in [
            "Agriculture", "Construction", "DomesticWork", "Hospitality", "Other"
        ]:
            if row.get(f"typeOfLabour{labour_type}") == '1':
                tx.run(
                    "MATCH (l:typeOfLabour {type: $type}), (v:Victim) WHERE id(v) = $victim_id "
                    "MERGE (v)-[:FORCED_INTO]->(l)",
                    type=labour_type, victim_id=victim_id
                )

        # Create relationships to typeOfSex nodes
        for exploit_type in [
            "Prostitution", "Pornography", "Other"
        ]:
            if row.get(f"typeOfSex{exploit_type}") == '1':
                tx.run(
                    "MATCH (s:typeOfSex {type: $type}), (v:Victim) WHERE id(v) = $victim_id "
                    "MERGE (v)-[:EXPLOITED_AS]->(s)",
                    type=exploit_type, victim_id=victim_id
                )

        # Create relationships to recruiterRelation nodes
        for recruiter_relation in [
            "IntimatePartner", "Friend", "Family", "Other"
        ]:
            if row.get(f"recruiterRelation{recruiter_relation}") == '1':
                tx.run(
                    "MATCH (r:recruiterRelation {type: $type}), (v:Victim) WHERE id(v) = $victim_id "
                    "MERGE (v)-[:RECRUITED_BY]->(r)",
                    type=recruiter_relation, victim_id=victim_id
                )


# Usage example
db = TraffickingGraphModel("neo4j://localhost:7687", "", "")
db.create_shared_nodes('CTDC_synthetic_20210825.tsv')
db.import_victim_nodes_and_relationships('CTDC_synthetic_20210825.tsv')
db.close()
