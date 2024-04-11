import os  
import shutil  

from retriever.directoryreader import MyDirectoryReader

from indexengine.process import (
    create_index, 
    add_docs_to_index, 
    load_index
    )
  
# Setup environment variables required for Azure OpenAI  
with open("../../openai_techlab_key.txt", "r") as file:
    os.environ["OPENAI_API_KEY"]  = file.read().strip()
    os.environ["OPENAI_TECHLAB_API_KEY"]  = file.read().strip()
  
# Set the document store and index storage locations and create a temporary dir for the index
path_documents = '/Users/nbut3013/PROJECTS/PIPE-4668-RIAF/PIPE-4668-RIAF_NSWHEALTH/ragpipe/pdfs/'
docstore_path = '../../test_data/documents_to_add'
index_path = 'temp_index'

reader = MyDirectoryReader(path_documents)
documents = reader.load_data()

  
# Define a test function for create_index  
def test_create_index():  
    # Test for each llm_service type  
    service = 'techlab' #['openai', 'azure', 'techlab']  
    index = create_index(
        docstore=documents, 
        outpath_index=index_path, 
        llm_service=service
        )  
    assert index is not None, f"Failed to create index with {service} service."  
  
# Define a test function for add_docs_to_index  
def test_add_docs_to_index():  
    index = create_index(docstore=documents, outpath_index=index_path, llm_service='techlab')  
    assert index is not None, "Failed to create index for adding documents."  
      
    index_before = len(index)  # Assuming VectorStoreIndex supports len()  
    add_docs_to_index(path_docs=docstore_path, index=index)  
    index_after = len(index)  
      
    assert index_after > index_before, "Documents were not added to the index."  
  
# Define a test function for load_index  
def test_load_index():  
    index = create_index(docstore=docstore_path, outpath_index=index_path, llm_service='openai')  
    assert index is not None, "Failed to create index for loading."  
  
    loaded_index = load_index(path_index=index_path)  
    assert loaded_index is not None, "Failed to load index from storage."  
  
# Run the tests  
test_create_index()  
test_add_docs_to_index()  
test_load_index()  
  
# Cleanup temporary directories  
shutil.rmtree(index_path)  
print("All tests passed successfully.")  
