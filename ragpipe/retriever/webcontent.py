# webpage content retrieval

import requests
from bs4 import BeautifulSoup


def extract_content(url):
    """
    Extracts main text content from a webpage.
    
    Args:
        url (str): URL of the webpage to extract content from.
        
    Returns:
        str: Main text content of the webpage.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        content = soup.find('body').get_text(strip=True, separator=' ') 
        # find links in response.content
        links = soup.find_all('a', href=True)
        return content, links

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error fetching content from {url}: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error fetching content from {url}: {e}")
        return None