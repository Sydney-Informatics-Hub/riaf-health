# Bing search API functions

import json
import requests
import os
from azure.cognitiveservices.search.customsearch import CustomSearchClient
from azure.cognitiveservices.search.websearch import WebSearchClient
from azure.cognitiveservices.search.websearch.models import SafeSearch
from msrest.authentication import CognitiveServicesCredentials


SUBSCRIPTION_KEY = os.environ['BING_CUSTOM_SEARCH_SUBSCRIPTION_KEY']
ENDPOINT = os.environ['BING_CUSTOM_SEARCH_ENDPOINT']
CUSTOMCONFIGID = os.environ['BING_CUSTOM_CONFIG_ID']

def bing_custom_search(query):
    """
    Perform a Bing Custom Search with the given search term, subscription key, and custom configuration ID.

    Args:
    query (str): The search term for the query.

    Returns:
    dict: The search results returned by the Bing Custom Search API.
    """
    # Prepare the request URL
    url = f'https://api.bing.microsoft.com/v7.0/custom/search?q={query}&customconfig={CUSTOMCONFIGID}'

    # Perform the request
    response = requests.get(url, headers={'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY})

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        return json.loads(response.text)
    else:
        # Return an error message if something went wrong
        return {"error": "Failed to retrieve search results", "status_code": response.status_code}



def custom_search_web_page_result_lookup(query, answer_count=5):
    """CustomSearch.

    This will look up a single query  and return web search results.

    Args:
    query (str): The query to search for.
    answer_count (int): The number of answers to return.
    """

    client = CustomSearchClient(
        endpoint=ENDPOINT,
        credentials=CognitiveServicesCredentials(SUBSCRIPTION_KEY))

    try:
        web_data = client.custom_instance.search(query=query, custom_config=1, answer_count=answer_count)
        print(f"Searched for Query '{query}'")

        if web_data.web_pages.value:
            first_web_result = web_data.web_pages.value[0]
            print("Web Pages result count: {}".format(
                len(web_data.web_pages.value)))
            print("First Web Page name: {}".format(first_web_result.name))
            print("First Web Page url: {}".format(first_web_result.url))
            return web_data.web_pages.value
        else:
            print("Didn't see any web data..")
            return None

    except Exception as err:
        print("Encountered exception. {}".format(err))
        return None
    
def news_search_with(query):
    """New Search.

    This will search  with response filters to news.
    """

    client = WebSearchClient(CognitiveServicesCredentials(SUBSCRIPTION_KEY))

    try:
        web_data = client.web.search(
            query=query, response_filter=["News"])

        # News attribute since I filtered "News"
        if web_data.news.value:

            print("Webpage Results#{}".format(len(web_data.news.value)))

            #first_web_page = web_data.news.value[0]
            #print("First web page name: {} ".format(first_web_page.name))
            #print("First web page URL: {} ".format(first_web_page.url))
            return web_data.news.value

        else:
            print("Didn't see any Web data..")
            return None

    except Exception as err:
        print("Encountered exception. {}".format(err))
        return None
