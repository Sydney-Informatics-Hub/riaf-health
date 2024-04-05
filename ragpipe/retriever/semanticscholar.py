# Functions for searching publications with SemantiScholar API
# for more info about API see https://api.semanticscholar.org/api-docs/#tag/Paper-Data/operation/post_graph_get_papers

import logging
import requests
from llama_index.readers.semanticscholar import SemanticScholarReader


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
                if year_start is not None:
                    if year < year_start:
                        continue                
                if year_end is not None:
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
    