# Custom Chatengine for the chatbot

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.prompts import PromptTemplate
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.llms.openai import OpenAI
from llama_index.core.retrievers import RecursiveRetriever
from llama_index.core.schema import IndexNode
from llama_index.core.extractors import SummaryExtractor, QuestionsAnsweredExtractor
from llama_index.memory import ChatMemoryBuffer

def generate_chatengine_context(system_prompt, index, model_llm):
    # Condense Plus Context Chat Engine (WIP)
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

    # Generate system prompt and create chat engine
    system_prompt = "You are a helpful AI assistant. Always provide source references for your answers."
    chat_engine = generate_chatengine_context(system_prompt, index, "gpt-3.5-turbo")

    # Query the chat engine
    query = "What are the main topics covered in the documents?"
    content, sources = query_chatengine(chat_engine, query)

    print("Response with inline references:")
    print(content)
    
    print("\nSource Nodes:")
    for i, source in enumerate(sources):
        print(f"[{i+1}] File: {source.get('file_name', 'Unknown')}")
        print(f"Text: {source.get('text', '')[:200]}...")  # Print first 200 characters
        print("---")
    
    # Generate a response with links and node IDs
    linked_response = content
    for i, source in enumerate(sources):
        linked_response = linked_response.replace(
            f"[{i+1}]", 
            f"[[{i+1}]](#{source.get('file_name', 'Unknown')})"
        )
    
    print("\nResponse with links and file names:")
    print(linked_response)
    
    assert content is not None and sources is not None
