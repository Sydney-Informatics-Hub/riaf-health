# Functions for creating, loading and adding documents to index

import logging
from llama_hub.semanticscholar import SemanticScholarReader

def read_semanticscholar(query_space, limit =20, full_text = False):
    """
    Search and read scholar online documents using LlamaHub's Semantic Scholar
    :param query_space: str, query space to search. This is the name of the area of research
    :param limit: int, number of documents to return
    :param fulltext: bool, if True, full text is returned

    :return: documents
    """
    s2reader = SemanticScholarReader()
    docstore = s2reader.load_data(query=query_space, limit=limit, full_text=full_text)
    # number of documents
    logging.info(f"Number of SemanticScholar documents found: {len(docstore)}")
    return docstore
