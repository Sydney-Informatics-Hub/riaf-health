# Load documents from a directory and get metadata

import os
import logging
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import TitleExtractor, SummaryExtractor, QuestionsAnsweredExtractor
from PyPDF2 import PdfReader
from llama_index.core.extractors import BaseExtractor


# class CustomExtractor(BaseExtractor):
#     async def aextract(self, nodes) -> List[Dict]:
#         metadata_list = [
#             {
#                 "custom": node.metadata["document_title"]
#                 + "\n"
#                 + node.metadata["excerpt_keywords"]
#             }
#             for node in nodes
#         ]
#         return metadata_list

def get_pdf_title(pdf_file_path):
    with open(pdf_file_path, 'rb') as f:
        pdf_reader = PdfReader(f) 
        metadata = pdf_reader.metadata
        return metadata.get('/Title', 'No title found')
    
def get_pdf_metadata(pdf_file_path):
    with open(pdf_file_path, 'rb') as f:
        pdf_reader = PdfReader(f) 
        return pdf_reader.metadata
    
def get_docx_title(docx_file_path):
    # convert docx to pdf first?
    pass


def get_meta(file_path):
    metadata = {}
    # check if document is pdf
    if file_path.lower().endswith('.pdf'):
        try:
            #metadata['title'] = get_pdf_title(file_path)
            metadata = get_pdf_metadata(file_path)
        except Exception as e:
            logging.error(f"Error extracting metadata title from pdf: {e}")
            metadata['/Title'] = None
    else:
        metadata['/Title'] = os.path.basename(file_path)
        # try:
        #     metadata['/Title'] = TitleExtractor().extract(file_path)
        #     # this will extract the title from the document or make one up if it can't?
        # except Exception as e:
        #     logging.error(f"Error extracting metadata title from documents: {e}")
        #     metadata['/Title'] = None
    return metadata


class MyDirectoryReader():

    def __init__(self, path):
        # Check that path exists and that it contains files
        if not os.path.exists(path):
            raise ValueError(f"Path {path} does not exist")
        if not os.path.isdir(path):
            raise ValueError(f"Path {path} is not a directory")
        if not os.listdir(path):
            raise ValueError(f"Path {path} is empty")
        self.path = path
        self.documents = None
        
    def load_data(self):
        try:
            self.documents = SimpleDirectoryReader(self.path,
                                                   recursive = True, 
                                                   filename_as_id = True,
                                                   file_metadata = self.get_meta).load_data()
        except Exception as e:
            raise ValueError(f"Error loading documents from {self.path}: {e}")
        #self.get_metadata()
        return self.documents
