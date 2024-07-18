# Custom Chatengine for the chatbot
"""
ToDo:
- check Semantic Chunker: https://docs.llamaindex.ai/en/latest/examples/node_parsers/semantic_chunking/ 
"""

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.prompts import PromptTemplate
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.llms.openai import OpenAI
from llama_index.core.retrievers import RecursiveRetriever
from llama_index.core.schema import IndexNode
from llama_index.core.extractors import SummaryExtractor, QuestionsAnsweredExtractor
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.response.pprint_utils import pprint_response

def generate_chatengine_context(system_prompt, index, model_llm):
    # Condense Plus Context Chat Engine (WIP)
    # see https://docs.llamaindex.ai/en/latest/module_guides/deploying/chat_engines/usage_pattern/
    memory = ChatMemoryBuffer.from_defaults(token_limit=10000)
    chat_engine = index.as_chat_engine(
        chat_mode="context",
        memory=memory,
        system_prompt=system_prompt,
        llm = OpenAI(model = model_llm),
        similarity_top_k=10,
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
        sources_meta  = [response.source_nodes[i].metadata for i in range(len(response.source_nodes))]
        sources_snippet = [response.source_nodes[i].text for i in range(len(response.source_nodes))]
    except:
        sources_meta = []
        sources_snippet = []

    pprint_response(response, show_source=True)
    return content, sources_meta, sources_snippet

def test_custom_synthesizer():
    from utils.envloader import load_api_key
    load_api_key(toml_file_path='secrets.toml')
    chunk_size=512
    
    # Load your documents and create the index
    documents = SimpleDirectoryReader('../test_data/documents_to_add').load_data()
    index = VectorStoreIndex.from_documents(documents, chunk_size=chunk_size)

    # Generate system prompt and create chat engine
    system_prompt = "You are a helpful AI assistant. Always provide source references for your answers."
    chat_engine = generate_chatengine_context(system_prompt, index, "gpt-4o")

    # Query the chat engine
    query = ("What are the main research priorities in NSW and Australia? Back up each statement with a reference to the document in the format:\n"
             "{'Reference': ..., 'file_name': ..., 'reference_snippet': ...}\n"
             "The output should be in mardown format.\n")
    # query = ("What are the main research priorities in NSW and Australia? Back up each point with a reference to the document.\n"
    #          "The output should include the node id and reference snippet and be in the format:\n"
    #          "Research priorities in NSW and Australia:\n"
    #          "- text ..... [1]\n"
    #          "- text ..... [2]\n"
    #          "...\n\n"
    #          "References:\n"
    #          "1. Title: ..., metadata: ... , id_: .., reference-snippet: ...:\n"
    #          "2. Title: ..., metadata: ... , id_: .., reference-snippet: ...:\n"
    #          "...\n")
             

    content, sources = query_chatengine(chat_engine, query)

    print("Response with inline references:")
    print(content)
    
    print("\nSource Nodes:")
    for i, source in enumerate(sources):
        print(f"[{i+1}] File: {source.get('file_name', 'Unknown')}")
        print(f"Text: {source.get('text', '')}...")  
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
