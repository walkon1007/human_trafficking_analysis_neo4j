import csv
import re


country_name_short = ['AFG', 'ALB', 'ARE', 'ARG', 'ARM', 'AUS', 'AUT', 'AZE', 'BDI', 'BEL', 'BEN', 'BFA', 'BGD', 'BGR',
                      'BHR', 'BHS', 'BIH', 'BLR', 'BLZ', 'BOL', 'BRA', 'BRN', 'BTN', 'CAN', 'CHE', 'CHL', 'CHN', 'CIV',
                      'CMR', 'COD', 'COG', 'COL', 'CRI', 'CUB', 'CUW', 'CYP', 'CZE', 'DEU', 'DJI', 'DNK', 'DOM', 'DZA',
                      'ECU', 'EGY', 'ERI', 'ESP', 'EST', 'ETH', 'FIN', 'FRA', 'FSM', 'GAB', 'GBR', 'GEO', 'GHA', 'GIN',
                      'GMB', 'GNB', 'GRC', 'GTM', 'GUY', 'HKG', 'HND', 'HRV', 'HTI', 'HUN', 'IDN', 'IND', 'IRL', 'IRN',
                      'IRQ', 'ISR', 'ITA', 'JAM', 'JOR', 'JPN', 'KAZ', 'KEN', 'KGZ', 'KHM', 'KOR', 'KWT', 'LAO', 'LBN',
                      'LBR', 'LBY', 'LKA', 'LSO', 'LTU', 'LVA', 'MAR', 'MDA', 'MDG', 'MEX', 'MKD', 'MLI', 'MMR', 'MNE',
                      'MNG', 'MOZ', 'MRT', 'MUS', 'MWI', 'MYS', 'NER', 'NGA', 'NIC', 'NLD', 'NOR', 'NPL', 'OMN', 'PAK',
                      'PAN', 'PER', 'PHL', 'PNG', 'POL', 'PRK', 'PRT', 'PRY', 'QAT', 'ROU', 'RUS', 'RWA', 'SAU', 'SDN',
                      'SEN', 'SGP', 'SLE', 'SLV', 'SOM', 'SRB', 'SSD', 'SVK', 'SVN', 'SWE', 'SYR', 'TCD', 'TGO', 'THA',
                      'TJK', 'TKL', 'TKM', 'TLS', 'TTO', 'TUN', 'TUR', 'TWN', 'TZA', 'UGA', 'UKR', 'URY', 'USA', 'UZB',
                      'VEN', 'VNM', 'VUT', 'YEM', 'ZAF', 'ZMB', 'ZWE']


means_of_control_types = [
            "DebtBondage", "TakesEarnings", "Threats", "PsychologicalAbuse",
            "PhysicalAbuse", "SexualAbuse", "FalsePromises", "PsychoactiveSubstances",
            "RestrictsMovement", "RestrictsMedicalCare", "ExcessiveWorkingHours",
            "ThreatOfLawEnforce", "WithholdsNecessities", "WithholdsDocuments", "Other"
        ]

forced_labour_types = ["Agriculture", "Construction", "DomesticWork", "Hospitality", "Other"]
sexual_exploit_types = ["Prostitution", "Pornography", "Other"]
recruiter_relation_types = ["IntimatePartner", "Friend", "Family", "Other"]

def read_and_deduplicate_tsv(file_path, column_name):
    unique_values = set()

    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')

        for row in reader:
            value = row[column_name]
            unique_values.add(value)

    return unique_values


# Usage example
file_path = 'CTDC_synthetic_20210825.tsv'
column_name = 'CountryOfExploitation'  # Replace with the name of your column
column_name1 = 'citizenship'
unique_values = read_and_deduplicate_tsv(file_path, column_name)
citizenship = read_and_deduplicate_tsv(file_path, column_name1)
value_list = []
citizenship_list = []
# Printing unique values
for value in unique_values:
    value_list.append(value)
for value in citizenship:
    citizenship_list.append(value)
value_list = sorted(value_list)
citizenship_list = sorted(citizenship_list)
print(len(value_list))
print(value_list)
print(len(citizenship_list))
print(citizenship_list)
combined_list = citizenship_list+value_list
combined_list = sorted(combined_list)
print(len(combined_list))
print(combined_list)
combined_list_deduplicated = sorted(set(combined_list))
print(len(combined_list_deduplicated))
print(combined_list_deduplicated)

x1 = "Africa;Asia"
x2 = "Americas/Oceania"
x3 = "Americas/Oceania;Asia"
# continents = x3.split(';')
continents = re.split(';|/', x3)
print(continents)
for continent in continents:
    print(continent)
    continent = continent.strip()  # Remove any leading/trailing whitespace
    print(continent)
