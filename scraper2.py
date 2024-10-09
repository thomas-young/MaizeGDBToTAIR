import sys
import csv
import time
from PyQt5.QtWidgets import QApplication, QFileDialog
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def extract_links(driver):
    """
    Extract all the links from the current page.
    Returns a list of links.
    """
    links = []
    elements = driver.find_elements_by_tag_name('a')
    for elem in elements:
        href = elem.get_attribute('href')
        if href:
            links.append(href)
    return links

def main():
    # Create the application object
    app = QApplication(sys.argv)

    # Open a file dialog to select a CSV file
    options_qt = QFileDialog.Options()
    options_qt |= QFileDialog.ReadOnly
    fileName, _ = QFileDialog.getOpenFileName(
        None,
        "Select CSV File",
        "",
        "CSV Files (*.csv);;All Files (*)",
        options=options_qt
    )

    # Check if a file was selected
    if fileName:
        # Open the CSV file and read the first column, skipping the header
        with open(fileName, 'r', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            # Skip the header row
            next(csvreader, None)
            first_column = [row[0].strip() for row in csvreader if row and row[0].strip()]  # Ensure the row is not empty and strip whitespace

        # Set up Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode if you don't need to see the browser
        driver = webdriver.Chrome(options=chrome_options)  # Or specify the path: webdriver.Chrome(executable_path='path/to/chromedriver', options=chrome_options)

        # Process each maizeGDB gene ID
        for gene_id in first_column:
            url = f"https://www.maizegdb.org/gene_center/gene/{gene_id}"
            print(f"\nFetching data for Gene ID: {gene_id}")
            print(f"URL: {url}")
            try:
                driver.get(url)

                # Wait for the dynamic content to load
                wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds
                # Example: Wait until an element with class 'gene-description' is present
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'gene-description')))

                # Extract desired information from the page
                # Gene Symbol
                gene_symbol_elem = driver.find_element_by_css_selector('h1.page-header')
                gene_symbol = gene_symbol_elem.text.strip() if gene_symbol_elem else "No gene symbol found"

                # Description
                description_elem = driver.find_element_by_class_name('gene-description')
                description = description_elem.text.strip() if description_elem else "No description available"

                # Extract all links
                links = extract_links(driver)

                # Write results to CSV
                output_file = f"{gene_id}_results.csv"
                with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                    csvwriter = csv.writer(outfile)
                    # Write headers
                    csvwriter.writerow(['Gene ID', 'Gene Symbol', 'Description'])
                    # Write the gene data
                    csvwriter.writerow([gene_id, gene_symbol, description])
                    csvwriter.writerow([])  # Blank row between gene data and links
                    csvwriter.writerow(['Links'])  # Links header
                    for link in links:
                        csvwriter.writerow([link])

                print(f"Results saved to {output_file}")

            except Exception as e:
                print(f"An error occurred while fetching data for Gene ID {gene_id}: {e}")
        # Close the driver after processing
        driver.quit()
    else:
        print("No file was selected.")

    # Exit the application
    sys.exit()

if __name__ == '__main__':
    main()
