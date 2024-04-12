import os
import shutil

from retriever.directoryreader import MyDirectoryReader

from indexengine.process import (
    create_index,
    add_docs_to_index,
    load_index
    )

# Setup environment variables required for Azure OpenAI
with open("../../openai_sih_key.txt", "r") as file:
    os.environ["OPENAI_API_KEY"]  = file.read().strip()
    os.environ["OPENAI_TECHLAB_API_KEY"]  = file.read().strip()

# Set the document store and index storage locations and create a temporary dir for the index
path_documents = '/home/nbutter/PROJECTS/PIPE-4668_FMHchatLLM/PIPE-4668-RIAF_NSWHEALTH/test_data/output_weiss/'
docstore_path = '/home/nbutter/PROJECTS/PIPE-4668_FMHchatLLM/PIPE-4668-RIAF_NSWHEALTH/test_data/documents_to_add'
index_path = 'temp_index'

reader = MyDirectoryReader(path_documents)
documents = reader.load_data()


# Define a test function for create_index
def test_create_index():
    print("Creating index")
    # Test for each llm_service type
    service = 'openai' #['openai', 'azure', 'techlab']
    index = create_index(
        docstore=documents,
        outpath_index=index_path,
        llm_service=service
        )
    assert index is not None, f"Failed to create index with {service} service."
    print("Created index!")

# Define a test function for add_docs_to_index
def test_add_docs_to_index():
    print("Creating index for testing add.")
    index = create_index(docstore=documents, outpath_index=index_path, llm_service='openai')
    assert index is not None, "Failed to create index for adding documents."

    print("Made index",index)

    index_before = len(index.index_struct.nodes_dict)
    print(index_before)
    add_docs_to_index(path_docs=docstore_path, index=index)
    index_after = len(index.index_struct.nodes_dict)
    print(index_after)
    assert index_after > index_before, "Documents were not added to the index."
    print("Added documents to index")

# Define a test function for load_index
def test_load_index():
    # print("Creating index for testing load.")
    # index = create_index(docstore=documents, outpath_index=index_path, llm_service='openai')
    # assert index is not None, "Failed to create index for loading."

    print("Loading new index.")
    loaded_index = load_index(path_index=index_path)
    assert loaded_index is not None, "Failed to load index from storage."

# Run the tests
test_create_index()
test_add_docs_to_index()
test_load_index()

# Cleanup temporary directories
shutil.rmtree(index_path)
print("All tests passed successfully.")
