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


