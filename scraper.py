import sys
import csv
import requests
import time
import re
from PyQt5.QtWidgets import QApplication, QFileDialog
from bs4 import BeautifulSoup

def fetch_ncbi_gene_description(at_id, max_retries=3):
    """
    Fetches the gene description from NCBI for a given Arabidopsis gene ID (AT ID).
    Implements retries with exponential backoff in case of server errors (HTTP 500).
    Returns the description as a string, or 'No description found' if not available.
    """
    retries = 0
    delay = 1  # Start with 1 second delay
    while retries < max_retries:
        try:
            # Use ESearch to get the NCBI Gene ID
            esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            params = {
                'db': 'gene',
                'term': f'{at_id}[Gene Name] AND 3702[TaxID]',  # 3702 is the TaxID for Arabidopsis thaliana
                'retmode': 'json'
            }
            esearch_response = requests.get(esearch_url, params=params)
            if esearch_response.status_code == 200:
                esearch_data = esearch_response.json()
                id_list = esearch_data.get('esearchresult', {}).get('idlist', [])
                if id_list:
                    ncbi_gene_id = id_list[0]
                    # Use ESummary to get the gene description
                    esummary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                    params = {
                        'db': 'gene',
                        'id': ncbi_gene_id,
                        'retmode': 'json'
                    }
                    esummary_response = requests.get(esummary_url, params=params)
                    if esummary_response.status_code == 200:
                        esummary_data = esummary_response.json()
                        result = esummary_data.get('result', {})
                        gene_info = result.get(ncbi_gene_id, {})
                        summary = gene_info.get('summary', '')
                        description_field = gene_info.get('description', '')
                        if summary and description_field:
                            description = f"{summary} {description_field}"
                        elif summary:
                            description = summary
                        elif description_field:
                            description = description_field
                        else:
                            description = 'No description found'
                        return description
                    elif esummary_response.status_code == 500:
                        print(f"Server error (500) when fetching description for AT ID {at_id}. Retrying...")
                    else:
                        print(f"ESummary request failed for AT ID {at_id} with status code {esummary_response.status_code}")
                        return 'No description found'
                else:
                    print(f"No NCBI Gene ID found for AT ID {at_id}")
                    return 'No description found'
            elif esearch_response.status_code == 500:
                print(f"Server error (500) when searching for AT ID {at_id}. Retrying...")
            else:
                print(f"ESearch request failed for AT ID {at_id} with status code {esearch_response.status_code}")
                return 'No description found'
        except Exception as e:
            print(f"An error occurred: {e}")
            return 'No description found'

        # Increment retries and delay
        retries += 1
        time.sleep(delay)
        delay *= 2  # Exponential backoff

    print(f"Failed to fetch description for AT ID {at_id} after {max_retries} retries.")
    return 'No description found'

def main():
    # Create the application object
    app = QApplication(sys.argv)

    # Open a file dialog to select a CSV file containing ZM IDs
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    file_name, _ = QFileDialog.getOpenFileName(
        None,
        "Select CSV File with ZM IDs",
        "",
        "CSV Files (*.csv);;All Files (*)",
        options=options
    )

    # Initialize a list to hold the data rows
    results = []

    # Check if a file was selected
    if file_name:
        # Open the CSV file and read the first column, skipping the header
        with open(file_name, 'r', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            # Skip the header row
            next(csvreader, None)
            gene_ids = [row[0].strip() for row in csvreader if row and row[0].strip()]

        # Process each ZM gene ID
        for gene_id in gene_ids:
            url = f"https://www.maizegdb.org/record_data/gene_data.php?id={gene_id}&type=overview"
            print(f"\nFetching data for Gene ID: {gene_id}")
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    # Parse the response content
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Extract all links containing 'arabidopsis.org'
                    all_links = [a['href'] for a in soup.find_all('a', href=True)]
                    filtered_links = [link for link in all_links if 'arabidopsis.org' in link]

                    if filtered_links:
                        # For each link, extract the AT ID and fetch the description
                        for link in filtered_links:
                            # Use regular expressions to extract the AT ID
                            at_id_match = re.search(r'AT[1-5MC]G\d{5}', link, re.IGNORECASE)
                            if at_id_match:
                                at_id = at_id_match.group(0).upper()
                                print(f"Processing AT ID: {at_id}")
                                # Fetch the gene description using NCBI E-utilities API
                                description = fetch_ncbi_gene_description(at_id)
                                # Append the data to the results
                                results.append({
                                    'ZM ID': gene_id,
                                    'AT ID': at_id,
                                    'TAIR Link': link,
                                    'Description': description
                                })
                                # Delay to comply with NCBI usage policies
                                time.sleep(0.4)
                            else:
                                print(f"Could not extract AT ID from link: {link}")
                    else:
                        # No AT IDs found; include ZM ID with 'No AT ID found'
                        results.append({
                            'ZM ID': gene_id,
                            'AT ID': 'No Arabidopsis orthologs found',
                            'TAIR Link': '',
                            'Description': ''
                        })
                        print(f"No 'arabidopsis.org' links found for Gene ID {gene_id}.")
                else:
                    print(f"Failed to fetch data for Gene ID {gene_id}. HTTP Status Code: {response.status_code}")
                    # Include ZM ID with error message
                    results.append({
                        'ZM ID': gene_id,
                        'AT ID': 'Error fetching data',
                        'TAIR Link': '',
                        'Description': ''
                    })
            except Exception as e:
                print(f"An error occurred while fetching data for Gene ID {gene_id}: {e}")
                results.append({
                    'ZM ID': gene_id,
                    'AT ID': 'Error occurred',
                    'TAIR Link': '',
                    'Description': ''
                })
        # Save all results to a single CSV file
        if results:
            output_file = 'gene_mappings_with_descriptions.csv'
            with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                fieldnames = ['ZM ID', 'AT ID', 'TAIR Link', 'Description']
                csvwriter = csv.DictWriter(outfile, fieldnames=fieldnames)
                csvwriter.writeheader()
                csvwriter.writerows(results)
            print(f"\nAll results saved to {output_file}")
        else:
            print("\nNo data to save.")

    else:
        print("No file was selected.")
        sys.exit()

    # Exit the application
    sys.exit()

if __name__ == '__main__':
    main()
