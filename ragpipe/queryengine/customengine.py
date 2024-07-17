# Custom Chatengine for the chatbot

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.prompts import PromptTemplate
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.llms.openai import OpenAI

def get_custom_synthesizer():
    return get_response_synthesizer(
        response_mode="tree_summarize",
        verbose=True
    )

def test_custom_synthesizer():
    from utils.envloader import load_api_key
    load_api_key(toml_file_path='secrets.toml')
    chunk_size=256
    
    # Load your documents and create the index
    documents = SimpleDirectoryReader('../test_data/documents_to_add').load_data()
    parser = SimpleNodeParser.from_defaults(chunk_size=chunk_size, chunk_overlap=100)
    nodes = parser.get_nodes_from_documents(documents)
    index = VectorStoreIndex(nodes)

    # Create a chat engine with the custom synthesizer and GPT-4 model
    llm = OpenAI(model="gpt-4")
    chat_engine = index.as_chat_engine(
        llm=llm,
        response_synthesizer=get_custom_synthesizer(),
        include_text=True,
        text_qa_template=PromptTemplate(
            "Context information is below.\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Given the context information and not prior knowledge, "
            "answer the query.\n"
            "Query: {query_str}\n"
            "Answer: "
        ),
        node_postprocessors=[
            lambda nodes: sorted(nodes, key=lambda x: x.score or 0, reverse=True)[:10]
        ],
        structured_answer_filtering=True
    )

    # return the response with inline citations, along with the references and snippets
    response = chat_engine.chat("What are the research priorities in health for Australia? Provide list in bullets with inline reference to context and list of references at the end.")
    
    # Process the response to ensure inline references
    processed_response = response.response
    for i, source_node in enumerate(response.source_nodes):
        processed_response = processed_response.replace(f"[{i+1}]", f"[{i+1}]")
    
    print("Response with inline references:")
    print(processed_response)
    
    print("\nSource Nodes:")
    for i, source_node in enumerate(response.source_nodes):
        print(f"[{i+1}] Node ID: {source_node.node.node_id}")
        print(f"Score: {source_node.score}")
        print(f"Text: {source_node.node.text[:200]}...")  # Print first 200 characters
        print("---")
    
    # Generate a response with links and node IDs
    linked_response = processed_response
    for i, source_node in enumerate(response.source_nodes):
        linked_response = linked_response.replace(
            f"[{i+1}]", 
            f"[[{i+1}]](#{source_node.node.node_id})"
        )
    
    print("\nResponse with links and node IDs:")
    print(linked_response)
    
    assert response is not None
