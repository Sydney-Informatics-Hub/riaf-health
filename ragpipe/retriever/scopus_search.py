# Scopus search
"""
see API documentation at https://dev.elsevier.com/documentation/ScopusSearchAPI.wadl
https://dev.elsevier.com/support.html

https://dev.elsevier.com/sc_search_tips.html
"""
import os
import requests
from pybliometrics.scopus import AuthorSearch, ScopusSearch
#from pybliometrics.scopus import AuthorSearch, ScopusSearch, AbstractRetrieval, AuthorRetrieval, AffiliationSearch, CitationOverview


def init_scopus():
    """
    Initialize Scopus API
    """
    if "SCOPUS_API_KEY" not in os.environ:
        fname_key = '../../elsevier_scopus_key.txt'
        with open(fname_key) as f:
            scopus_key = f.read().strip()
            os.environ["SCOPUS_API_KEY"] = scopus_key
    else:
        scopus_key = os.environ["SCOPUS_API_KEY"]
    return scopus_key

def search_author(author):
    """
    Search for author

    API params:
        apiKey
        AUTHFIRST
        AUTHLAST
        AFFIL

    Input:
    ------
    author : str
        Author name

    Returns:
    --------
    json
        JSON response from Scopus API
    """
    endpoint = 'http://api.elsevier.com/content/search/author' #?query=AFFIL%28university%29
    # split author name in first and last name
    author = author.split()
    if len(author) == 1:
        author_last = author[0]
    elif len(author) == 2:
        author_last = author[1]
        author_first = author[0]
    else:
        author_last = author[-1]
        author_first = ' '.join(author[:-1])

    scopus_key = init_scopus()
    search_url = endpoint
    params = {
        'apiKey': scopus_key,
        'query': author,
        #'AUTHLAST': author_last,
        #'AUTHFIRST': author_first
    }
    response = requests.get(search_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    

def search_paper(title):
    """
    Search for paper

    API params:
        apiKey
        query
        count
        start
        sort
        content
        view

    Input:      
    ------
    title : str
        Title of the paper
    """
    endpoint = 'http://api.elsevier.com/content/search/scopus'
    scopus_key = init_scopus()
    search_url = endpoint
    params = {
        'apiKey': scopus_key,
        'query': title,
        'count': 1,
        'sort': 'relevance',
        'content': 'all',
        'view': 'complete'
    }
    response = requests.get(search_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    

def search_docs_by_author(authorname):
    author = authorname.split()
    if len(author) == 1:
        author_last = author[0]
    elif len(author) == 2:
        author_last = author[1]
        author_first = author[0]
    else:
        author_last = author[-1]
        author_first = ' '.join(author[:-1])
    search_query = f"AUTHLASTNAME({author_last}) and AUTHFIRST({author_first})"
    author_search = AuthorSearch(search_query)

    # Check if any authors were found
    if author_search.authors:
        # Assuming the first result is the correct author
        # You might need to refine how you pick the correct author from the results
        author_id = author_search.authors[0][0]
        # get last part after "-"
        author_id = author_id.split('-')[-1]

        # Search for documents by this author using their Scopus Author ID
        doc_search = ScopusSearch(f"AU-ID({author_id})")
        #doc_search = ScopusSearch(f"REF({author_id})", verbose = True)

        # Print the titles of the papers
        print(f"Found {len(doc_search.results)} documents for author ID {author_id}:")
        for result in doc_search.results:
            print(result.title)

        titles = [result.title for result in doc_search.results]
        doc_ids = [result.eid for result in doc_search.results]
    else:
        print(f"No authors found with the name {firstname} {lastname}")
    return doc_ids, titles


