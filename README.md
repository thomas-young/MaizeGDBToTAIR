# **README**

---

## **Maize to Arabidopsis Gene Mapper with Descriptions**

This script processes a list of maize gene IDs (ZM IDs), fetches the corresponding Arabidopsis gene IDs (AT IDs) from MaizeGDB, retrieves gene descriptions from NCBI, and compiles all the information into a single CSV file.

---

### **Table of Contents**

- [Description](#description)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage Instructions](#usage-instructions)
- [Script Workflow](#script-workflow)
- [Error Handling](#error-handling)
- [Output](#output)
- [Notes and Considerations](#notes-and-considerations)
- [License](#license)
- [Contact Information](#contact-information)

---

## **Description**

This Python script automates the process of mapping maize gene IDs to their orthologous Arabidopsis gene IDs and fetching their descriptions. It performs the following tasks:

1. Reads a CSV file containing maize gene IDs (ZM IDs).
2. For each ZM ID:
   - Fetches the corresponding Arabidopsis links from MaizeGDB.
   - Extracts Arabidopsis gene IDs (AT IDs) from those links.
   - Fetches gene descriptions for each AT ID from NCBI using the E-utilities API.
3. Handles errors such as server issues and missing data.
4. Compiles all data into a single CSV file with columns:
   - **ZM ID**: Maize gene ID.
   - **AT ID**: Arabidopsis gene ID.
   - **TAIR Link**: Link to the Arabidopsis gene page.
   - **Description**: Gene description from NCBI.

---

## **Prerequisites**

- **Python Version**: The script requires Python 3.6 or higher.
- **Libraries**:
  - `requests`
  - `beautifulsoup4`
  - `PyQt5`
  - `re` (Regular Expressions, part of Python's standard library)
  - `csv` (part of Python's standard library)
  - `sys` (part of Python's standard library)
  - `time` (part of Python's standard library)

---

## **Installation**

1. **Clone or Download the Script**:

   Save the script as `maize_to_arabidopsis_with_retries.py`.

2. **Install Required Python Libraries**:

   Open a terminal or command prompt and run:

   ```bash
   pip install requests beautifulsoup4 PyQt5
   ```

   If you encounter permissions issues, you may need to use:

   ```bash
   pip install --user requests beautifulsoup4 PyQt5
   ```

   Alternatively, if you are using a virtual environment, ensure it is activated before installing the packages.

---

## **Usage Instructions**

1. **Prepare Your CSV File**:

   - Ensure you have a CSV file containing your maize gene IDs (ZM IDs) in the first column.
   - The CSV file should have a header row. Example:

     ```csv
     ZM ID
     Zm00001eb234430
     Zm00001eb235200
     Zm00001eb234690
     ```

2. **Run the Script**:

   - Navigate to the directory containing the script in your terminal or command prompt.
   - Run the script using Python:

     ```bash
     python maize_to_arabidopsis_with_retries.py
     ```

3. **Select Your CSV File**:

   - A file dialog window will appear.
   - Navigate to and select your CSV file containing the ZM IDs.

4. **Wait for Processing**:

   - The script will process each ZM ID.
   - Progress messages will be printed to the console.
   - The script handles errors and retries automatically.

5. **Check the Output File**:

   - After processing, the script saves the results to `gene_mappings_with_descriptions.csv` in the same directory.
   - Open this file to view the compiled data.

---

## **Script Workflow**

1. **Reading ZM IDs**:

   - The script reads ZM IDs from the selected CSV file.
   - It skips the header row and extracts IDs from the first column.

2. **Fetching Arabidopsis Links**:

   - For each ZM ID, it constructs a URL to fetch data from MaizeGDB.
   - Parses the HTML content using `BeautifulSoup`.
   - Extracts links that contain `arabidopsis.org`.

3. **Extracting AT IDs**:

   - Uses regular expressions to extract AT IDs from the links.
   - The pattern matches standard Arabidopsis gene IDs (e.g., `AT5G11260`).

4. **Fetching Gene Descriptions**:

   - For each AT ID, the script fetches the gene description from NCBI using the E-utilities API.
   - Implements retries with exponential backoff for HTTP 500 errors.

5. **Handling Errors and Missing Data**:

   - If no AT IDs are found for a ZM ID, it records `'No AT ID found'`.
   - If data fetching fails, it records appropriate error messages.
   - All ZM IDs are included in the final output.

6. **Compiling Results**:

   - The script compiles all data into a list of dictionaries.
   - Each dictionary corresponds to a row in the output CSV file.

7. **Saving the Output**:

   - Writes the compiled data to `gene_mappings_with_descriptions.csv`.
   - The CSV file includes the following columns:
     - **ZM ID**
     - **AT ID**
     - **TAIR Link**
     - **Description**

---

## **Error Handling**

- **HTTP 500 Errors**:

  - The script retries failed API calls up to 3 times with exponential backoff.
  - Delays between retries increase exponentially (1s, 2s, 4s).

- **No AT IDs Found**:

  - If no Arabidopsis links are found for a ZM ID, the script records `'No AT ID found'` for that ID.

- **Exceptions**:

  - Any exceptions during processing are caught, and an error message is printed.
  - The ZM ID is included in the output with `'Error occurred'` in the AT ID column.

- **Logging**:

  - Errors and status messages are printed to the console.
  - For extensive logging, consider modifying the script to write logs to a file.

---

## **Output**

- **Output File**: `gene_mappings_with_descriptions.csv`

- **Columns**:

  - **ZM ID**: Maize gene ID from the input file.
  - **AT ID**: Corresponding Arabidopsis gene ID or an error message.
  - **TAIR Link**: Link to the Arabidopsis gene page (if available).
  - **Description**: Gene description fetched from NCBI (if available).

- **Example Output**:

  ```csv
  ZM ID,AT ID,TAIR Link,Description
  Zm00001eb235510,AT5G11260,https://www.arabidopsis.org/locus?name=AT5G11260,GDSL esterase/lipase At5g11260
  Zm00001eb234690,AT2G23290,https://www.arabidopsis.org/locus?name=AT2G23290,Cysteine-rich RLK (RECEPTOR-like protein kinase) 2
  Zm00001eb235470,No AT ID found,,
  ```

---

## **Notes and Considerations**

- **NCBI E-utilities Usage Policies**:

  - The script complies with NCBI's policies by limiting the frequency of requests and handling errors appropriately.
  - Delays between requests are implemented to avoid overloading NCBI's servers.

- **Dependencies**:

  - Ensure all required Python libraries are installed before running the script.
  - The script uses `PyQt5` for the file dialog interface.

- **Data Verification**:

  - After running the script, review the output CSV file to verify data accuracy.
  - Check for any error messages in the output and address them if necessary.

- **Customization**:

  - You can modify the script to fetch additional data fields or to change the output format.
  - Adjust the `max_retries` parameter and delay times as needed.

- **Logging**:

  - For better error tracking, consider implementing logging to a file.
  - Use Python's `logging` module to record errors and statuses.

- **Large Datasets**:

  - For processing large numbers of IDs, be mindful of API usage limits.
  - Consider implementing progress indicators or batching mechanisms.

---

## **License**

This script is provided "as is" without any warranty. You are free to modify and distribute it for personal or educational purposes.

---

## **Contact Information**

For questions, suggestions, or assistance with the script, please contact:

- **Name**: Thomas Young
- **Email**: tomyoung@iastate.edu

---

**Disclaimer**: This script is intended for research and educational purposes. Ensure compliance with all relevant terms of service and usage policies of the data sources used (MaizeGDB, NCBI).

---
