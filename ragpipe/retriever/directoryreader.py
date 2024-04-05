# Load documents from a directory and get metadata

import os
from llama_index.core import SimpleDirectoryReader
from llama_index.core.extractors import TitleExtractor


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

    def get_metadata(self):
        try:
            self.metadata = TitleExtractor().extract(self.documents)
        except Exception as e:
            raise ValueError(f"Error extracting metadata from documents: {e}")
        return self.metadata
        
    def load_data(self):
        try:
            self.documents = SimpleDirectoryReader(self.path,
                                                   recursive = True, 
                                                   filename_as_id = True).load_data()
        except Exception as e:
            raise ValueError(f"Error loading documents from {self.path}: {e}")
        #self.get_metadata()
        return self.documents
