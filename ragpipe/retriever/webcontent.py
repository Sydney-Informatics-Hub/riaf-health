""" 
This module contains functions to extract text content and metadata from webpages given a list of urls.
It also creates an index database from the extracted content.
The module contains the following functions:
    - custom_webextract(url)
    - web2docs_simple(urls)
    - web2docs_async(urls, titles)
    - docs2index(documents)

See for example usage and tests in test_webquery.py

Author: Sebastian Haan
"""

import requests
import logging
from bs4 import BeautifulSoup
from llama_index.core import download_loader, VectorStoreIndex
from llama_index.core import Document
import logging
import aiohttp
import asyncio
import io
from PyPDF2 import PdfReader


async def fetch(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                content_type = response.headers.get('Content-Type', '')
                # Check if the response is likely a PDF
                if 'application/pdf' in content_type or url.lower().endswith('.pdf'):
                    # Read the PDF content
                    pdf_data = await response.read()
                    reader = PdfReader(io.BytesIO(pdf_data))
                    text = ''
                    for page in reader.pages:
                        text += page.extract_text() if page.extract_text() else ''
                    return text.encode('utf-8')
                else:
                    # Handle as HTML or other text-based formats
                    content = await response.text()
                    return BeautifulSoup(content, 'html.parser').get_text().encode('utf-8')
            else:
                logging.info(f"Error fetching {url}: Status {response.status}")
                return None
    except aiohttp.ClientError as e:
        logging.info(f"Request failed for {url}: {e}")
        return None
    except Exception as e:
        logging.info(f"Unexpected error for {url}: {e}")
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
        logging.info(f"HTTP Error fetching content from {url}: {e}")
    except requests.exceptions.ConnectionError as e:
        logging.info(f"Connection Error fetching content from {url}: {e}")
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

def web2docs_async(urls, titles):
    """
    Extracts main text content from a list of webpages using asyncio and bs4.
    
    Args:
        urls (list of str): List of URLs of the webpages to extract content from.
        titles (list of str): List of titles of the webpages to extract content from.
        
    Returns:
        documents: List of documents with main text content of the webpages.
        documents_missing: List of dict of title and URLs for which no content could be extracted.
    """
    contents = asyncio.run(fetch_all(urls))
    # filter for contents that are not None
    contents_ok = []
    urls_ok = []
    titles_ok = []
    documents_missing = []
    for i in range(len(contents)):
        if contents[i]:
            contents_ok.append(contents[i])
            urls_ok.append(urls[i])
            titles_ok.append(titles[i])
        else:
            documents_missing.append({'title': titles[i],'url': urls[i]})

    metadata = [{'href': url, 'title': title} for url, title in zip(urls_ok,titles_ok)]
    documents = [Document(text=content, doc_id = url, extra_info = metadata) for content, url, metadata in zip(contents_ok, urls_ok, metadata)]
    return documents, documents_missing

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
