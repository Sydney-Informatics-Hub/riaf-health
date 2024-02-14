# Test bing search and web query

from retriever.bingsearch import bing_custom_search, get_urls_from_bing, get_titles_from_bing
from retriever.webcontent import web2docs
from llama_index import VectorStoreIndex
import os
import logging

# check if openai key is set in environment
def test_openai_key():
    if "OPENAI_API_KEY" not in os.environ:
        try:
            with open("../../openai_sih_key.txt", "r") as f:
                os.environ["OPENAI_API_KEY"] = f.read().strip()
        except:
            logging.error("OpenAI key not found in environment or file")
    assert "OPENAI_API_KEY" in os.environ   


def test_bingsearch():
    test_openai_key()
    query = "Sydney Informatics Hub"
    bing_results = bing_custom_search(query, count=5)
    urls = get_urls_from_bing(bing_results)
    titles = get_titles_from_bing(bing_results)
    assert len(urls) == 5
    assert len(titles) == 5
    # print titles and urls
    print("Pages found:")
    for title, url in zip(titles, urls):
        print(f"{title}: {url}")
    

def test_query():
    test_openai_key()
    query = "Sydney Informatics Hub"
    print('Query:', query)
    bing_results = bing_custom_search(query, count=5)
    urls = get_urls_from_bing(bing_results)
    titles = get_titles_from_bing(bing_results)
    # print titles and urls
    print("Pages found:")
    for title, url in zip(titles, urls):
        print(f"{title}: {url}")
    documents = web2docs(urls)
    index = VectorStoreIndex.from_documents(documents)
    queryengine = index.as_query_engine()
    result = queryengine.query('Summarise what is the Sydney Informatics Hub and what services it provides.')
    assert result is not None
    print(result.response)
