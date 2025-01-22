# Functions for creating, loading and adding documents to index

# Azure OpenAI setup, only needed if using Azure OpenAI
_azure_endpoint = "https://techlab-copilots-aiservices.openai.azure.com/" 
# choose Azure AI model, currently deployed: 'gpt-4-32k' (2021), 'gpt-4-1106-preview' (Sep 2023), 'gpt-35-turbo', 'gpt-35-turbo-16k'
_azure_engine_name = "gpt-4-1106-preview" #"gpt-4-1106-preview" # 'gpt-4-32k'""
_azure_api_version = "2023-12-01-preview" 
_azure_engine_name_embeddings = "text-embedding-ada-002"

techlab_endpoint = 'https://apim-techlab-usydtechlabgenai.azure-api.net/'
techlab_deployment = 'GPT35shopfront'
techlab_embedding = 'text-embedding-ada-002'
techlab_api_version = '2023-12-01-preview'

_chunksize = 1024

# see for latest https://learn.microsoft.com/en-us/azure/ai-services/openai/api-version-deprecation

import os
import logging
from llama_index.llms.openai import OpenAI
# from llama_index.embeddings.azure_openai import AzureOpenAI
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core import VectorStoreIndex
from llama_index.core import ServiceContext, SimpleDirectoryReader, StorageContext, StorageContext, load_index_from_storage
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding

def create_index(docstore, 
                 outpath_index = None, 
                 model_llm = "gpt-4o",
                 temperature = 0.0, 
                 context_window = 4096, 
                 num_output = 600,
                 llm_service = 'openai'):
    """
    Create index from docstore and store index in outpath_index

    :param docstore: database with documents to index
    :param outpath_index: path to store index, if None index is not stored
    :param model_llm: str, model to use for index
    :param temperature: float, temperature for LLM model
    :param context_window: int, context window size in number of tokens
    :param num_output: int, number of output tokens
    :param llm_service: str, LLM service to use: 'openai' or 'azure'

    :return: index
    """
    if llm_service == 'openai':
        llm = OpenAI(
            temperature=temperature,
            model=model_llm,
            max_tokens=num_output)
        embed_model = 'default'
    elif llm_service == 'azure':
        llm = AzureOpenAI(
            engine=_azure_engine_name,
            model=model_llm,
            temperature=temperature,
            azure_endpoint=_azure_endpoint,
            api_key=os.environ["OPENAI_API_KEY"],
            api_version=_azure_api_version,
        )
        embed_model = AzureOpenAIEmbedding(
            model="text-embedding-ada-002",
            deployment_name=_azure_engine_name_embeddings,
            api_key=os.environ["OPENAI_API_KEY"],
            azure_endpoint=_azure_endpoint,
            api_version=_azure_api_version,
        )
    elif llm_service == 'techlab':
        llm = AzureOpenAI(
            engine=techlab_deployment,
            model=model_llm,
            temperature=temperature,
            azure_endpoint=techlab_endpoint,
            api_key=os.environ["OPENAI_API_KEY"],
            api_version=_azure_api_version,
        )
        print(llm)
        embed_model = AzureOpenAIEmbedding(
            model="text-embedding-ada-002",
            deployment_name=techlab_embedding,
            api_key=os.environ["OPENAI_TECHLAB_API_KEY"],
            azure_endpoint=techlab_endpoint,
            api_version=techlab_api_version,
        )
        print(embed_model)
    else:
        logging.error(f"LLM service {llm_service} not supported")
        return None

    # Create service context
    service_context = ServiceContext.from_defaults(
        llm=llm,
        embed_model = embed_model,
        context_window=context_window,
        num_output=num_output,
        chunk_size=_chunksize
        )
    # Create index
    try:
        index = VectorStoreIndex.from_documents(docstore, service_context=service_context)
    except Exception as e:
        logging.error(f"Failed to create index with exception: {e}")
        return None
    # store index
    if outpath_index is not None:
        os.makedirs(outpath_index, exist_ok=True)
        index.storage_context.persist(persist_dir=outpath_index)
    return index

def add_docs_to_index(path_docs, index):
    """
    Add all data in path_docs to index.
    Data can incl Markdown, PDFs, Word documents, PowerPoint decks, images, audio and video.
    
    :param path_docs: path to documents. 
    :param index: index to add documents to

    :return: index
    """
    print("Loading new documents...")
    new_documents = SimpleDirectoryReader(path_docs).load_data()

    for doc in new_documents:
        # check if doc is empty or None
        if doc is None or doc.text is None or len(doc.text) == 0:
            logging.warning(f"Document with ID {doc.doc_id} is empty")
            continue
        try:
            index.insert(doc)
        except Exception as e:
            logging.error(f"Failed to insert document with ID {doc.doc_id} with exception: {e}")
            continue

    return index

def load_index(path_index):
    """
    Load index from storage path

    :param path_index: path to index

    :return: index

    """
    if os.path.exists(path_index) and len(os.listdir(path_index)) > 0:
        # rebuild storage context
        storage_context = StorageContext.from_defaults(persist_dir=path_index)
        # load index
        index = load_index_from_storage(storage_context)
        return index
    else:
        logging.error("Index not found")
        return None
    

    

