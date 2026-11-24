
"""
American Gut Project - Survey Data Extractor
Author: Katerina Georgiopoulos 
Date: November 2026

This program reads a text file containing NCBI BioSample
accessions, retrieves their records using NCBI E-utilities,
extracts survey attributes, filters by a selected question,
and exports the results to a CSV file using pandas.
"""

import argparse
import time
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path

# NCBI settings
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
HEADERS = {
    "User-Agent": "AmericanGutPythonProject/1.0"
}


# Send requests to NCBI with automatic retries
def ncbi_request(url, parameters):
    for attempt in range(6):
        try:
            response = requests.get(
                url,
                params=parameters,
                headers=HEADERS,
                timeout=30
            )

            if response.status_code == 429:
                wait_time = 15 * (attempt + 1)
                print(f"NCBI rate limit reached. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue

            response.raise_for_status()
            time.sleep(1)
            return response

        except requests.RequestException:
            if attempt == 5:
                raise

            wait_time = 10 * (attempt + 1)
            print(f"Request failed. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

    raise requests.RequestException("Unable to contact NCBI after multiple attempts.")


# Read BioSample accessions from a text file
def read_accessions(filename):
    accessions = []

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            accession = line.strip()

            if accession and accession not in accessions:
                accessions.append(accession)

    return accessions


# Find the NCBI BioSample ID for an accession
def find_biosample_id(accession):
    url = BASE_URL + "esearch.fcgi"

    parameters = {
        "db": "biosample",
        "term": accession + "[Accession]",
        "retmode": "json"
    }

    response = ncbi_request(url, parameters)
    data = response.json()

    id_list = data.get("esearchresult", {}).get("idlist", [])

    if not id_list:
        return None

    return id_list[0]


# Retrieve survey attributes from a BioSample record
def get_survey_data(accession):
    biosample_id = find_biosample_id(accession)

    if biosample_id is None:
        print(f"BioSample not found: {accession}")
        return []

    url = BASE_URL + "efetch.fcgi"

    parameters = {
        "db": "biosample",
        "id": biosample_id,
        "retmode": "xml"
    }

    response = ncbi_request(url, parameters)
    root = ET.fromstring(response.content)

    results = []

    for attribute in root.findall(".//Attribute"):
        question = (
            attribute.get("attribute_name")
            or attribute.get("harmonized_name")
            or attribute.get("display_name")
            or "Unknown"
        )

        answer = "".join(attribute.itertext()).strip()

        if answer:
            results.append({
                "BioSample_ID": accession,
                "Question": question,
                "Response": answer
            })

    return results


# Process all accessions in the input file
def process_accessions(accessions):
    all_results = []

    for number, accession in enumerate(accessions, start=1):
        print(f"Processing {number}/{len(accessions)}: {accession}")

        try:
            results = get_survey_data(accession)
            all_results.extend(results)

            if not results:
                print(f"No survey attributes found for {accession}")

        except requests.RequestException as error:
            print(f"Connection error for {accession}: {error}")

        except ET.ParseError as error:
            print(f"XML error for {accession}: {error}")

    return all_results


# Filter survey results by the selected question
def filter_results(results, question):
    df = pd.DataFrame(
        results,
        columns=["BioSample_ID", "Question", "Response"]
    )

    if df.empty:
        return df

    filtered_df = df[
        df["Question"].str.contains(
            question,
            case=False,
            na=False,
            regex=False
        )
    ]

    return filtered_df


# Export filtered results to a CSV file
def export_csv(df, output_file):
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False)

    print("\nExport complete!")
    print(f"Saved file: {output_path}")
    print(f"Number of responses: {len(df)}")


# Main program
def main():
    parser = argparse.ArgumentParser(
        description="Extract American Gut survey responses from NCBI."
    )

    parser.add_argument(
        "input_file",
        help="Text file containing BioSample accessions"
    )

    parser.add_argument(
        "--question",
        default="alcohol_frequency",
        help="Survey question to filter"
    )

    parser.add_argument(
        "--output",
        default="output/american_gut_results.csv",
        help="Output CSV filename"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional number of accessions to process for testing"
    )

    args = parser.parse_args()

    print("Starting American Gut data extraction...\n")

    accessions = read_accessions(args.input_file)

    if args.limit is not None:
        accessions = accessions[:args.limit]

    if not accessions:
        print("No BioSample accessions found in the input file.")
        return

    print(f"Found {len(accessions)} BioSample accession(s).\n")

    results = process_accessions(accessions)
    filtered_df = filter_results(results, args.question)

    export_csv(filtered_df, args.output)


if __name__ == "__main__":
    main()