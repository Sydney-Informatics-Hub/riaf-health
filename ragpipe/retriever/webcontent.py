# webpage content retrieval

import requests
from bs4 import BeautifulSoup
from llama_index import download_loader, VectorStoreIndex
#from llama_index.readers.web import SimpleWebPageReader # --> not working
from llama_index import Document
import logging
import aiohttp
import asyncio


async def fetch(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.text()
                return BeautifulSoup(content, 'html.parser').get_text().encode('utf-8')
            else:
                print(f"Error fetching {url}: Status {response.status}")
                return None
    except aiohttp.ClientError as e:
        print(f"Request failed for {url}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error for {url}: {e}")
        return None
    

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)


def custom_webextract(url):
    """
    Extracts main text content from a webpage using bs4 and custom filters.
    
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
    
def web2docs_simple(urls):
    """
    Extracts main text content from  a list of webpages.
    
    Args:
        urls (list of str): List of URLs of the webpages to extract content from.
        
    Returns:
        documents: List of documents with main text content of the webpages.
    """
    SimpleWebPageReader = download_loader('SimpleWebPageReader')
    loader = SimpleWebPageReader(html_to_text=True)
    documents = loader.load_data(urls=urls)
    return documents

def web2docs_async(urls):
    """
    Extracts main text content from a list of webpages using asyncio and bs4.
    
    Args:
        urls (list of str): List of URLs of the webpages to extract content from.
        
    Returns:
        documents: List of documents with main text content of the webpages.
    """
    contents = asyncio.run(fetch_all(urls))
    documents = [Document(text=content, doc_id = url) for content, url in zip(contents, urls)]
    return documents

def docs2index(documents):
    """
    Create index from list of documents.
    
    Args:
        documents: List of documents to create index from.
        
    Returns:
        index: Index created from the list of documents.
    """
    index = VectorStoreIndex.from_documents(documents)
    return index
