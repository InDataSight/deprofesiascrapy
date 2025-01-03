import requests
from bs4 import BeautifulSoup
import sys
import logging

# Configure logging
logging.basicConfig(filename='extract_text.log', level=logging.ERROR, format='%(asctime)s %(levelname)s:%(message)s')

def extract_text_from_url(url, output_file):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Get the entire text content of the page
        text_content = soup.get_text(separator='\n', strip=True)

        # Save the extracted text content to a file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text_content)
    except requests.exceptions.RequestException as e:
        logging.error(f'Failed to retrieve the page: {url}. Error: {e}')
        print(f'Failed to retrieve the page: {url}. Error: {e}')
    except Exception as e:
        logging.error(f'An error occurred while processing the page: {url}. Error: {e}')
        print(f'An error occurred while processing the page: {url}. Error: {e}')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python extract_text.py <url> <output_file>")
        sys.exit(1)

    url = sys.argv[1]
    output_file = sys.argv[2]
    extract_text_from_url(url, output_file)