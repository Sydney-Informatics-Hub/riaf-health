"""
Bing search

This module provides functions to perform Bing search and get metadata from the search results.
This module is used in main.py to get search results from Bing and in webcontent.py to get data from the search results.
The Bing search client is initialized with the Bing Search V7 subscription key and the endpoint.
The module contains the following functions:
    - init_bing()
    - bing_custom_search(query, count=10, year_start = None, year_end= None)
    - bing_news_search(query, count=10, year_start = None, year_end= None)
    - get_urls_from_bing(dict_list)
    - get_titles_from_bing(dict_list)
    - get_snippets_from_bing(dict_list)
    - get_metadata(url_list)

See for example usage and tests in test_webquery.py

Author: Sebastian Haan
"""

import json
import requests
import logging
import os
import sys
from typing import Callable, Union, List
from utils.envloader import load_api_key
from retriever.webcontent import WebPageProcessor
from llama_index.core import Document


def init_bing():
    """
    Initialize Bing search client
    """
    # Add your Bing Search subscription key to your environment variables.
    ENDPOINT = "https://api.bing.microsoft.com/v7.0"
    if "BING_SEARCH_API_KEY" not in os.environ:
        load_api_key("secrets.toml")
        SUBSCRIPTION_KEY = os.environ["BING_SEARCH_API_KEY"]
    else:
        SUBSCRIPTION_KEY = os.environ["BING_SEARCH_API_KEY"]
    return SUBSCRIPTION_KEY, ENDPOINT



def bing_custom_search(query, count=10, mkt='en-AU', language='en', year_start = None, year_end= None):
    """
    Perform a Bing Custom Search with the given search term.
    see for search parameters: https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/reference/query-parameters

    Args:
    query (str): The search term for the query.
    count (int): The number of search results to return.
    year_start (int): start of period to search
    year_end (int): end of period to search

    Returns:
    list of dict: The search results returned by the Bing Custom Search API.
    Each dict include 'name', 'url', 'snippet'
    """
    if year_start is not None and year_end is not None:
        timeframe = f"{year_start}-01-01..{year_end}-12-31"
    else:
        timeframe = None

    SUBSCRIPTION_KEY, ENDPOINT = init_bing()
    search_url = ENDPOINT + "/search" 
    headers = {"Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY}
    #params = {"q": query, "count": count, "responseFilter": "Webpages", "freshness": None}
    params = {
            'q': query,
            'mkt': mkt,
            "setLang": language,
            "count": count,
            "freshness": timeframe,
            "responseFilter": "Webpages"
        }
    #params = {"q": query, "customconfig": CUSTOMCONFIGID, "count": count}

    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()

    results = response.json()
    if 'webPages' not in results:
        logging.error(f"No webPages in Bing search results for query: {query}")
        return None

    return results['webPages']['value']


def bing_news_search(query, count=10, year_start = None, year_end= None):
    """
    Perform a Bing News Search with the given search term.
    see for search parameters: https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/reference/query-parameters

    Args:
    query (str): The search term for the query.
    count (int): The number of search results to return.
    year_start (int): start of period to search
    year_end (int): end of period to search

    Returns:
    list of dict: The search results returned by the Bing Custom Search API.
    Each dict include 'name', 'url', 'snippet'
    """
    if year_start is not None and year_end is not None:
        timeframe = f"{year_start}-01-01..{year_end}-12-31"
    else:
        timeframe = None

    SUBSCRIPTION_KEY, ENDPOINT = init_bing()
    search_url = ENDPOINT + "/search" 
    headers = {"Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY}
    params = {"q": query, "count": count, "responseFilter": "News", "freshness": None}

    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()

    results = response.json()
    if 'news' not in results:
        return None

    return results['news']['value']


def get_urls_from_bing(dict_list):
    """
    Get list of URLs from list of Bing search results

    Args:
    dict_list (list of dict): List of Bing search results

    Returns:
    list of str: List of URLs from Bing search results
    """
    url_list = []
    for result in dict_list:
        url_list.append(result['url'])
    return url_list

def get_titles_from_bing(dict_list):
    """
    Get list of titles from list of Bing search results

    Args:
    dict_list (list of dict): List of Bing search results

    Returns:
    list of str: List of titles from Bing search results
    """
    title_list = []
    for result in dict_list:
        title_list.append(result['name'])
    return title_list

def get_snippets_from_bing(dict_list):
    """
    Get list of snippets from list of Bing search results

    Args:
    dict_list (list of dict): List of Bing search results

    Returns:
    list of str: List of snippets from Bing search results
    """
    snippet_list = []
    for result in dict_list:
        snippet_list.append(result['snippets'])
    return snippet_list


def get_metadata(url_list):
    """
    Get metadata description from list of urls. 
    Bing search results do not include metadata, so we need to get it from the URLs.

    Args:
    url_list (list of str): List of URLs to get metadata from

    Returns:
    list of dict: List of metadata for each URL
    """
    metadata_desc = []
    for url in url_list:
        response = requests.get(url)
        response.raise_for_status()
        # search for <meta name="description" content="..."> in response.content
        # extract only the head of the html
        content = response.content.split(b'</head>')[0] + b'</head>'
        content = content.decode('utf-8')
        if '<meta name="description" content="' in content:
            desc = content.split('<meta name="description" content="')[1].split('"')[0]
        elif '<meta property="og:description" content="' in content:
            desc = content.split('<meta property="og:description" content="')[1].split('"')[0]
        else:
            desc = ''
        metadata_desc.append(desc)
    return metadata_desc


class BingSearch():
    def __init__(self, k=3, is_valid_source: Callable = None,
                 min_char_count: int = 150, snippet_chunk_size: int = 1000, webpage_helper_max_threads=10,
                 mkt='en-AU', language='en', year_start = None, year_end= None, **kwargs):
        """
        Initialize BingSearch with specific parameters.

        Params:
            k (int): Number of search results to return.
            is_valid_source: A function that takes a URL and returns a boolean.
            min_char_count: Minimum character count for the article to be considered valid.
            snippet_chunk_size: Maximum character count for each snippet.
            webpage_helper_max_threads: Maximum number of threads to use for webpage helper.
            mkt: Market to use for the Bing search (default is 'en-US').
            language: Language to use for the Bing search (default is 'en').
            year_start (int): start of period to search
            year_end (int): end of period to search
            **kwargs: Additional parameters for the Bing search API.
                - Reference: https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/reference/query-parameters
        """

        if year_start is not None and year_end is not None:
            timeframe = f"{year_start}-01-01..{year_end}-12-31"
        else:
            timeframe = None
        self.bing_api_key, endpoint = init_bing()
        self.endpoint = endpoint + "/search" #"https://api.bing.microsoft.com/v7.0/search"
        self.params = {
            'mkt': mkt,
            "setLang": language,
            "count": k,
            "freshness": timeframe,
            **kwargs
        }
        # setup the webpage helper for getting content from the URLs
        self.webpage_helper = WebPageProcessor(
            min_char_count=min_char_count,
            snippet_chunk_size=snippet_chunk_size,
            max_thread_num=webpage_helper_max_threads
        )
        self.usage = 0

        # If not None, is_valid_source shall be a function that takes a URL and returns a boolean.
        if is_valid_source:
            self.is_valid_source = is_valid_source
        else:
            self.is_valid_source = lambda x: True

    def get_usage_and_reset(self):
        """
        Get the usage count and reset it.

        Returns:
            A dictionary with the usage count for 'BingSearch'.
        """
        usage = self.usage
        self.usage = 0

        return {'BingSearch': usage}

    def search_and_retrieve(self, query_or_queries: Union[str, List[str]], exclude_urls: List[str] = []):
        """Search with Bing for self.k top passages for query or queries

        Args:
            query_or_queries (Union[str, List[str]]): The query or queries to search for.
            exclude_urls (List[str]): A list of urls to exclude from the search results.

        Returns:
            - a list of Dicts, each dict has keys of 'description', 'snippets' (list of strings), 'title', 'url'
            - a list of Dicts for missing results
        """
        queries = (
            [query_or_queries]
            if isinstance(query_or_queries, str)
            else query_or_queries
        )
        self.usage += len(queries)

        url_to_results = {}

        headers = {"Ocp-Apim-Subscription-Key": self.bing_api_key}

        for query in queries:
            try:
                results = requests.get(
                    self.endpoint,
                    headers=headers,
                    params={**self.params, 'q': query}
                ).json()

                for d in results['webPages']['value']:
                    if self.is_valid_source(d['url']) and d['url'] not in exclude_urls:
                        url_to_results[d['url']] = {'url': d['url'], 'title': d['name'], 'description': d['snippet']}
            except Exception as e:
                logging.error(f'Error occurs when searching query {query}: {e}')

        # Get content from the URLs:
        valid_url_to_snippets, urls_invalid = self.webpage_helper.urls_to_snippets(list(url_to_results.keys()))
        collected_results = []
        for url in valid_url_to_snippets:
            r = url_to_results[url]
            r['snippets'] = valid_url_to_snippets[url]['snippets']
            collected_results.append(r)
        # Get the missing results    
        missing_results = []
        for url in urls_invalid:
            r = url_to_results[url]
            missing_results.append(r)

        return collected_results, missing_results
    
    def web2docs(self, webresults : List[dict]):
        """
        Converts a list of websearch results to a list of documents with metadata and text snippets of the webpages.
        Additionally returns a list of dict of title and URLs for which no content could be extracted.

        Args:
            webresults (list of dict): List of Bing search results with keys:
                'description', 'snippets' (list of strings), 'title', 'url'

        Returns:
            documents: List of documents with main text content of the webpages.
            documents_missing: List of dict of title and URLs for which no content could be extracted.
        """
        contents = [result['snippets'] for result in webresults]
        metadata = [{'href': result['url'], 'title': result['title'], 'description': result['description']} for result in webresults]
        doc_ids = [result['url'] for result in webresults]
        # filter metadata for contents that are not None
        contents_ok = []
        urls_ok = []
        metadata_ok = []
        documents_missing = []
        for i in range(len(contents)):
            if contents[i] and len(contents[i]) > 0:
                contents_ok.append(contents[i])
                urls_ok.append(doc_ids[i])
                metadata_ok.append(metadata[i])
            else:
                documents_missing.append({'title': webresults[i]['title'],'url': doc_ids[i]})
        documents = []
        for i in range(len(contents_ok)):
            for snippet in contents_ok[i]:
                if len(snippet) > 0:
                    documents.append(Document(text=snippet, doc_id = urls_ok[i], extra_info = metadata_ok[i]))
        #documents = [Document(text=content, doc_id = url, extra_info = metadata) for content, url, metadata in zip(contents_ok, urls_ok, metadata_ok)]
        return documents, documents_missing
