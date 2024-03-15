# Scopus search
"""
see API documentation at https://dev.elsevier.com/documentation/ScopusSearchAPI.wadl
https://dev.elsevier.com/support.html

seems not to work becauase of authentication fail (scopus uses IP check etc)
"""
import os
import requests
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
    response.status_code
        

    
    return

