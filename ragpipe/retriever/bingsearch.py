# Bing search API functions

import json
import requests
import os
#from azure.cognitiveservices.search.customsearch import CustomSearchClient
#from azure.cognitiveservices.search.websearch import WebSearchClient
#from azure.cognitiveservices.search.websearch.models import SafeSearch
#from msrest.authentication import CognitiveServicesCredentials

fname_key = '../../azure_sih_bing_key.txt'
with open(fname_key) as f:
    SUBSCRIPTION_KEY = f.read().strip()
ENDPOINT = "https://api.bing.microsoft.com/v7.0"



def bing_custom_search(query, count=10, year_start = None, year_end= None):
    """
    Perform a Bing Custom Search with the given search term, subscription key, and custom configuration ID.
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


    search_url = ENDPOINT + "/search" 
    headers = {"Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY}
    params = {"q": query, "count": count, "responseFilter": "Webpages", "freshness": None}
    #params = {"q": query, "customconfig": CUSTOMCONFIGID, "count": count}

    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()

    results = response.json()
    if 'webPages' not in results:
        return None

    return results['webPages']['value']


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
    list of str: List of snippeets from Bing search results
    """
    snippet_list = []
    for result in dict_list:
        snippet_list.append(result['name'])
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
