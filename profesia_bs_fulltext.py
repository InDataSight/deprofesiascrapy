import requests
from bs4 import BeautifulSoup
import sys

def extract_text_from_url(url, output_file):
    try:
        # Send a GET request to the URL
        response = requests.get(url) # Send a GET request to the URL
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser') # Use the 'html.parser' parser

        # Get the entire text content of the page
        text_content = soup.get_text(separator='\n', strip=True) # Get the text content with newlines as separators

        # Save the extracted text content to a file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text_content)
    except requests.exceptions.RequestException as e:
        print(f'Failed to retrieve the page: {url}. Error: {e}')
    except Exception as e:
        print(f'An error occurred while processing the page: {url}. Error: {e}')

if __name__ == "__main__":
    if len(sys.argv) != 3: # Check if the correct number of arguments is provided
        print("Usage: python profesia_bs_fulltext.py <url> <output_file>") # Print usage information
        sys.exit(1) # Exit the script with an error code

    url = sys.argv[1] # Get the URL from the command line arguments
    output_file = sys.argv[2] # Get the output file name from the command line arguments
    extract_text_from_url(input_url, output_file_path) # Call the function to extract text from the URL and save it to a file