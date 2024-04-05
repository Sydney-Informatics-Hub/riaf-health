# Functions for searching publications with SemantiScholar API
# for more info about API see https://api.semanticscholar.org/api-docs/#tag/Paper-Data/operation/post_graph_get_papers

"""
metadata example:
{'title': 'Tropoelastin and Elastin Assembly',
 'venue': 'Frontiers in Bioengineering and Biotechnology',
 'year': 2021,
 'paperId': 'c450bf38350269cd8be8bbdcd39ccf598da403bf',
 'citationCount': 58,
 'openAccessPdf': 'https://www.frontiersin.org/articles/10.3389/fbioe.2021.643110/pdf',
 'authors': ['J. Ozsvar',
  'Chengeng Yang',
  'S. Cain',
  'C. Baldock',
  'A. Tarakanova',
  'A. Weiss'],
 'externalIds': {'PubMedCentral': '7947355',
  'DOI': '10.3389/fbioe.2021.643110',
  'CorpusId': 232041511,
  'PubMed': '33718344'}}
"""

import os
import requests
import logging
from llama_index.readers.semanticscholar import SemanticScholarReader
# https://github.com/run-llama/llama-hub/tree/main/llama_hub/semanticscholar
# https://github.com/run-llama/llama_index/tree/main/llama-index-integrations/readers/llama-index-readers-semanticscholar
#from semanticscholar import SemanticScholar
from openai import OpenAI

def read_semanticscholar(query_space, author, keywords, limit =20, full_text = False, year_start = None, year_end = None):
    """
    Search and read scholar online documents using Semantic Scholar API

    :param query_space: str, query space to search. This is the name of the area of research
    :param author: str, author name
    :param keywords: list of str, keywords to search for (only used if query_space and author return no results)
    :param limit: int, number of documents to return
    :param fulltext: bool, if True, full text is returned
    :param year_start: int, start year of publication
    :param year_end: int, end year of publication

    :return: documents
    """
    # use last name of author for search
    author = author.split(' ')[-1]
    s2reader = SemanticScholarReader(timeout=30)
    #query = f"ti:{query_space} AND au:{author}"
    query = query = f"{query_space}, {author}"
    docstore = s2reader.load_data(query=query_space, limit=limit, full_text=full_text)
    if len(docstore) > 0:
        logging.info(f"Number of SemanticScholar documents found: {len(docstore)}")
        return docstore
    
    # run query with keywords
    docstore = []
    keywords = keywords.split(',')
    for keyword in keywords:
        query = f"{keyword}, {author}"
        docs = s2reader.load_data(query=query, limit=limit, full_text=full_text)
        docstore.extend(docs)
    if len(docstore) > 0:
        # remove duplicates
        docstore_new = []
        unique_paper_ids = []
        for doc in docstore:
            paper_id = doc.metadata['paperId']
            if 'year' in doc.metadata:
                year = doc.metadata['year']
                if 'year_start' is not None:
                    if year < year_start:
                        continue                
                if 'year_end' is not None:
                    if year > year_end:
                        continue   
            if paper_id not in unique_paper_ids:
                docstore_new.append(doc)
                unique_paper_ids.append(paper_id)
        logging.info(f"Number of SemanticScholar documents found: {len(docstore)}")
        return docstore_new
    else:
        logging.info(f"No SemanticScholar documents found for topic nor any keyword")
        return None
    








    
def get_datacite_metadata(doi):
    """
    for testing
    Get metadata from DataCite for a publication with a given DOI

    :param doi: str, DOI of publication

    :return: metadata
    """
    #email = 'crossref.flakily508@passmail.net'
    #url = f"https://api.datacite.org/dois/{doi}"
    #url = f"https://doi.org/api/handles/{doi}?pretty"
    #url = f"https://doi.org/api/handles/{doi}?type=URL&callback=processResponse" # --> not enough info
    url = f"https://doi.crossref.org/search/doi?pid={email}&format=info&doi={doi}" # --> not enough info
    #url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}/authors?fields=affiliations" # --> affiliations typically empty
    
    """
    response = requests.get(url)
    if response.status_code == 200:
        metadata = response.json()
        return metadata
    else:
        logging.error(f"Error getting DataCite metadata for DOI: {doi}")
        return None
    """
    
    metadata = crossref_commons.retrieval.get_publication_as_json(doi)
    # only sometimes affilitations are included, otherwise empyt []
    # however, it may include ORCID, which can be subsequently used to get affiliations 
    #(https://info.orcid.org/documentation/api-tutorials/api-tutorial-read-data-on-a-record/)
    # https://github.com/ORCID/python-orcid
