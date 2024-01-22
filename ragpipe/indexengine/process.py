# Functions for creating, loading and adding documents to index

# Azure OpenAI setup, only needed if using Azure OpenAI
_azure_endpoint = "https://techlab-copilots-aiservices.openai.azure.com/" 
_azure_engine_name = "gpt-4-32k"
_azure_api_version = "2023-12-01-preview" 
_azure_engine_name_embeddings = "text-embedding-ada-002"
# see for latest https://learn.microsoft.com/en-us/azure/ai-services/openai/api-version-deprecation

import os
import logging
from llama_index.llms import OpenAI, AzureOpenAI
from llama_index import (
                        ServiceContext,
                         VectorStoreIndex,
                         SimpleDirectoryReader,
                         StorageContext,
                         StorageContext, 
                        load_index_from_storage)
from llama_index.query_engine import CitationQueryEngine, RetrieverQueryEngine
from llama_index.embeddings import AzureOpenAIEmbedding

def create_index(docstore, 
                 outpath_index = None, 
                 model_llm = "gpt-4-1106-preview",
                 temperature = 0.1, 
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
    else:
        logging.error(f"LLM service {llm_service} not supported")
        return None

    # Create service context
    service_context = ServiceContext.from_defaults(
        llm=llm,
        embed_model = embed_model,
        context_window=context_window,
        num_output=num_output,
        )
    # Create index
    index = VectorStoreIndex.from_documents(docstore, service_context=service_context)
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
    docs = SimpleDirectoryReader(path_docs)
    index.add_documents(docs)
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
    
def query_publication_index(query, index, top_k = 5):
    """
    Query index for relevant publications to question.

    :param query: str, question to publication index
    :param index: publication index to query
    :param top_k: int, number of top publications to return

    :return: response
    """
    query_engine = CitationQueryEngine.from_args(
        index,
        similarity_top_k=top_k,
        citation_chunk_size=512,
    )
    # query the index for relevant publications to question
    response = query_engine.query(query)
    print("Answer: ", response)
    print("Source nodes: ")
    for node in response.source_nodes:
        print(node.node.metadata)
    return response
    

