# test for directoryreader.py

import os
from retriever.directoryreader import MyDirectoryReader

def test_directoryreader():
    path_documents = '../test_data/documents_to_add'
    # check number of documents in the test directory
    ndocs = len(os.listdir(path_documents))
    assert ndocs > 0
    reader = MyDirectoryReader(path_documents)
    mydocuments = reader.load_data()
    assert len(mydocuments) > 0