
This project is a Python program that retrieves survey information from the American Gut Project using the NCBI BioSample database.

The program accepts a text file containing BioSample accession numbers, retrieves the associated survey attributes, filters the results by a selected survey question, and exports the matching responses into a CSV file.

## Requirements

The program uses:
- Python
- pandas
- requests
- xml.etree.ElementTree
- argparse

## Installation

Install the required Python packages:

```bash
pip install pandas requests
```

## How to Use

1. Create a text file containing NCBI BioSample accessions, with one accession per line.
2. Open a terminal in the project folder.
3. Run the Python script:

```bash
python american_gut.py example_inputs/sample_list_1.txt
```

By default, the program filters for the survey question `alcohol_frequency`.

To select a different question:

```bash
python american_gut.py example_inputs/sample_list_1.txt --question alcohol_consumption
```

To specify an output filename:

```bash
python american_gut.py example_inputs/sample_list_1.txt --output output/results.csv
```

An optional limit can be used to test the program with a smaller number of accessions:

```bash
python american_gut.py example_inputs/sample_list_1.txt --limit 3
```

## Output

The program exports a CSV file containing three columns:

- `BioSample_ID`: NCBI BioSample accession
- `Question`: Survey question or attribute name
- `Response`: Recorded survey response

The default output location is:

`output/american_gut_results.csv`

## Data Source

NCBI BioSample database: https://www.ncbi.nlm.nih.gov/biosample/

American Gut Project: https://americangut.org/

## Author

Katerina