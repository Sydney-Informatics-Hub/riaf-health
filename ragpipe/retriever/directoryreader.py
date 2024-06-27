# Load documents from a directory and get metadata

import os
import logging
from llama_index.core import SimpleDirectoryReader
from llama_index.core.extractors import TitleExtractor, SummaryExtractor, QuestionsAnsweredExtractor
from PyPDF2 import PdfFileReader

def get_pdf_title(pdf_file_path):
    with open(pdf_file_path) as f:
        pdf_reader = PdfFileReader(f) 
        return pdf_reader.getDocumentInfo().title
    
def get_docx_title(docx_file_path):
    pass


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

    def get_metadata(self, file_path):
        metadata = {}
        try:
            # this will extract the title from the document or make one up if it can't?
            metadata['title'] = TitleExtractor().extract(file_path)
        except Exception as e:
            logging.error(f"Error extracting metadata title from documents: {e}")
            metadata['title'] = None
        # get metadata reference from document name (exclude path)
        if metadata['title'] is None:
            metadata['Reference'] = os.path.basename(file_path)
        else:
            metadata['Reference'] = metadata['title'] + ' (' + os.path.basename(file_path) + ')'
        return metadata
        
    def load_data(self):
        try:
            self.documents = SimpleDirectoryReader(self.path,
                                                   recursive = True, 
                                                   filename_as_id = True,
                                                   file_metadata = self.get_metadata).load_data()
        except Exception as e:
            raise ValueError(f"Error loading documents from {self.path}: {e}")
        #self.get_metadata()
        return self.documents
