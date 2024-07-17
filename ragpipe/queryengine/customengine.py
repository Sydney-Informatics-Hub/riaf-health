# Custom Chatengine for the chatbot

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.prompts import PromptTemplate
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.llms.openai import OpenAI
from llama_index.core.retrievers import RecursiveRetriever
from llama_index.core.schema import IndexNode
from llama_index.core.extractors import SummaryExtractor, QuestionsAnsweredExtractor

def generate_chatengine_context(system_prompt, index, model_llm):
    # Condense Plus Context Chat Engine (WIP)
    system_prompt = self.generate_system_prompt()

    memory = ChatMemoryBuffer.from_defaults(token_limit=8000)
    chat_engine = index.as_chat_engine(
        chat_mode="context",
        memory=memory,
        system_prompt=system_prompt,
        llm = OpenAI(model = model_llm),
        verbose=True,
        )
    return chat_engine
    
def query_chatengine(chat_engine, query):
    """
    Query chat engine for content and sources.

    :param query: str, query to chat engine

    :return: content, sources
    """
    response = chat_engine.chat(query)
    content = response.response
    try:
        sources  = [response.source_nodes[i].metadata for i in range(len(response.source_nodes))]
    except:
        sources = []
    return content, sources

def test_custom_synthesizer():
    from utils.envloader import load_api_key
    load_api_key(toml_file_path='secrets.toml')
    chunk_size=512
    
    # Load your documents and create the index
    documents = SimpleDirectoryReader('../test_data/documents_to_add').load_data()
    index = VectorStoreIndex.from_documents(documents, chunk_size=chunk_size)


    # Add here system prompt generate chatenegine and query chatengine


    print("Response with inline references:")
    print(response.response)
    
    print("\nSource Nodes:")
    for i, source_node in enumerate(response.source_nodes):
        print(f"[{i+1}] Node ID: {source_node.node.node_id}")
        print(f"Score: {source_node.score}")
        print(f"Text: {source_node.node.text[:200]}...")  # Print first 200 characters
        print("---")
    
    # Generate a response with links and node IDs
    linked_response = response.response
    for i, source_node in enumerate(response.source_nodes):
        linked_response = linked_response.replace(
            f"[{i+1}]", 
            f"[[{i+1}]](#{source_node.node.node_id})"
        )
    
    print("\nResponse with links and node IDs:")
    print(linked_response)
    
    assert response is not None
