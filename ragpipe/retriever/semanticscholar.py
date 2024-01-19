# Functions for creating, loading and adding documents to index

import logging
from llama_hub.semanticscholar import SemanticScholarReader

def read_semanticscholar(query_space, author, keywords, limit =20, full_text = False):
    """
    Search and read scholar online documents using Semantic Scholar API

    :param query_space: str, query space to search. This is the name of the area of research
    :param author: str, author name
    :param keywords: list of str, keywords to search for (only used if query_space and author return no results)
    :param limit: int, number of documents to return
    :param fulltext: bool, if True, full text is returned

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
            if paper_id not in unique_paper_ids:
                docstore_new.append(doc)
                unique_paper_ids.append(paper_id)
        logging.info(f"Number of SemanticScholar documents found: {len(docstore)}")
        return docstore_new
    else:
        logging.info(f"No SemanticScholar documents found for topic nor any keyword")
        return None
