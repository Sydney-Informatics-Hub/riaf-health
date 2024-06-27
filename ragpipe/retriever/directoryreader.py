# Load documents from a directory and get metadata

import os
import logging
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import TitleExtractor, SummaryExtractor, QuestionsAnsweredExtractor
from PyPDF2 import PdfReader
from docx import Document


def get_pdf_title(pdf_file_path):
    with open(pdf_file_path, 'rb') as f:
        pdf_reader = PdfReader(f) 
        metadata = pdf_reader.metadata
        return metadata.get('/Title', 'No title found')
    
def get_pdf_metadata(pdf_file_path):
    """
    Extract metadata from a pdf file
    """
    with open(pdf_file_path, 'rb') as f:
        pdf_reader = PdfReader(f) 
        metadata = pdf_reader.metadata
        # convert all metadata keys that start with / to strings without / and in lower case
        metadata = {key[1:].lower(): value for key, value in metadata.items() if key.startswith('/')}
        return metadata
    
def get_docx_metadata(docx_file_path):
    """
    Extract metadata from a docx file
    """
    doc = Document(docx_file_path)
    core_properties = doc.core_properties

    metadata = {
        'title': core_properties.title,
        'author': core_properties.author,
        'subject': core_properties.subject,
        'keywords': core_properties.keywords,
        'last_modified_by': core_properties.last_modified_by,
        'created': core_properties.created,
        'modified': core_properties.modified,
        'category': core_properties.category,
        'comments': core_properties.comments,
        'content_status': core_properties.content_status,
        'identifier': core_properties.identifier,
        'language': core_properties.language,
        'revision': core_properties.revision,
        'version': core_properties.version
    }
    return metadata


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
    elif file_path.lower().endswith('.docx'):
        try:
            metadata = get_docx_metadata(file_path)
        except Exception as e:
            logging.error(f"Error extracting metadata from docx: {e}")
            metadata['/Title'] = None
    else:
        metadata['Filename'] = os.path.basename(file_path)
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
                                                   file_metadata = get_meta).load_data()
        except Exception as e:
            raise ValueError(f"Error loading documents from {self.path}: {e}")
        #self.get_metadata()
        return self.documents
