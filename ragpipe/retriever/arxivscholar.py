# Functions for creating, loading and adding documents to index

import logging
from llama_index.core import download_loader

def read_arxivscholar(author, topic = None, limit =20, full_text = False):
    """
    Search and read scholar online documents using arXiv
    :param author: str, author name to search for
    :param topic: str, query space to search. Currently can't search both, author and topic
    :param limit: int, number of documents to return
    :param fulltext: bool, if True, full text is returned

    :return: documents
    """
from llama_index.readers.papers import ArxivReader

    loader = ArxivReader()
    #query = f"ti:{topic} AND au:{author}"
    query_author = f"au:{author}"
    documents = loader.load_data(search_query=query_author)
    """
    author_last_name = author.split()[-1]
    documents = loader.load_data(search_query=topic)
    docs_sel = []
    for doc in documents:
        # split author names and select last na
        # check if doc.metadata has Authors
        if 'Authors' in doc.metadata:
            print('yes')
            au_docs = doc.metadata['Authors'].split(',')
            au_last_names = [au.split()[-1] for au in au_docs]
            if author_last_name in au_last_names:
                docs_sel.append(doc)
    """

    logging.info(f"Number of arXiv documents found: {len(documents)}")
    return documents
