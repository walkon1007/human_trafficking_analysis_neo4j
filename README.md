# Analyzing CTDC datasets with Neo4j
## **How to use**
CTDC Datasets: https://www.ctdatacollaborative.org/

1. Update the datasets from the CTDC website(if applicable).
2. Set up the Neo4j database.
3. Run the `import_data_from_CTDC_systhetic.py` to import the victim data into the Neo4j database.
4. Update the country data with `update_country_node.py`.
5. Import the perpetrator data with `import_perpetrator.py`.
6. Ananlyze with Neo4j.

## **Nodes**

**1.Victim**

properties: yearOfRegistration,gender,ageBroad,majorityStatusAtExploit,traffickMonths

**2.Country**

properties: name, full_name, UNSubRegion

**3.MeansOfControl**

properties: type[DebtBondage,TakesEarnings,Threats,PsychologicalAbuse,PhysicalAbuse,SexualAbuse,FalsePromises,PsychoactiveSubstances,RestrictsMovement,RestrictsMedicalCare,ExcessiveWorkingHours,ThreatOfLawEnforce,WithholdsNecessities,WithholdsDocuments,Other]

**4.typeOfLabour**

properties: type{Agriculture,Construction,DomesticWork,Hospitality,Other}

**5.typeOfSex**

properties:  type{Prostitution,Pornography,Other}

**6.recruiterRelation**

properties:  type{IntimatePartner,Friend,Family,Other}

**7.ContinentalRegion**

properties:  name{Africa, Americas, Oceania, Asia, Europe}

**8.Perpetrator**

properties:  yearOfRegistration,gender,ageBroad

## **Relationships**

- **`FROM_COUNTRY`: `(v:Victim)-[:FROM_COUNTRY]->(c:Country)`**
- **`EXPLOITED_IN`: `(v:Victim)-[:EXPLOITED_IN]->(c:Country)`**
- **`SUBJECTED_TO`: `(v:Victim)-[:SUBJECTED_TO]->(m:MeansOfControl)`**
- **`FORCED_INTO` :`(v:Victim)-[:FORCED_INTO]->(l:typeOfLabour)`**
- `**EXPLOITED_AS` :`(v:Victim)-[:EXPLOITED_AS]->(s:typeOfSex)`**
- `**RECRUITED_BY`:`(v:Victim)-[:RECRUITED_BY]->(r:recruiterRelation)`**
- `**LOCATED_AT`:`(c:Country)-[:LOCATED_AT]->(ct:ContinentalRegion)`**
- **`CITIZEN_OF`:`(p:Perpetrator)-[:CITIZEN_OF]→(ct:ContinentalRegion)`**
- **`IDENTIFIED_AS`**:**`(p:Perpetrator)-[:IDENTIFIED_AS]→(r:recruiterRelation)`**

Query Examples:

MATCH (v:Victim)-[:FROM_COUNTRY]->(vc:Country)-[:LOCATED_AT]->(ct:ContinentalRegion),
      (p:Perpetrator)-[:CITIZEN_OF]->(ct)
where v.yearOfRegistration='2020' and p.yearOfRegistration='2020'
RETURN v, vc, ct, p
LIMIT 500

In this sample query, we can identify that in the registration year of 2020, there is one group of perpetrator at age of 48+ at the continent of Europe and has lot of victims in the country of Ukraine.
