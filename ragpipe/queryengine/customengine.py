# Custom Chatengine for the chatbot

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.prompts import PromptTemplate
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.llms.openai import OpenAI
from llama_index.core.retrievers import RecursiveRetriever
from llama_index.core.schema import IndexNode
from llama_index.core.extractors import SummaryExtractor, QuestionsAnsweredExtractor

def test_custom_synthesizer():
    from utils.envloader import load_api_key
    load_api_key(toml_file_path='secrets.toml')
    chunk_size=256
    
    # Load your documents and create the index
    documents = SimpleDirectoryReader('../test_data/documents_to_add').load_data()
    parser = SimpleNodeParser.from_defaults(chunk_size=chunk_size, chunk_overlap=100)
    base_nodes = parser.get_nodes_from_documents(documents)
    
    # Create metadata references
    extractors = [
        SummaryExtractor(summaries=["self"], show_progress=True),
        QuestionsAnsweredExtractor(questions=5, show_progress=True),
    ]
    
    node_to_metadata = {}
    for extractor in extractors:
        metadata_dicts = extractor.extract(base_nodes)
        for node, metadata in zip(base_nodes, metadata_dicts):
            if node.node_id not in node_to_metadata:
                node_to_metadata[node.node_id] = metadata
            else:
                node_to_metadata[node.node_id].update(metadata)
    
    # Create all nodes with metadata references
    all_nodes = base_nodes.copy()
    for node_id, metadata in node_to_metadata.items():
        for val in metadata.values():
            all_nodes.append(IndexNode(text=val, index_id=node_id))
    
    all_nodes_dict = {n.node_id: n for n in all_nodes}
    
    # Create vector index and retriever
    vector_index = VectorStoreIndex(all_nodes)
    vector_retriever = vector_index.as_retriever(similarity_top_k=2)
    
    # Create recursive retriever
    recursive_retriever = RecursiveRetriever(
        "vector",
        retriever_dict={"vector": vector_retriever},
        node_dict=all_nodes_dict,
        verbose=True
    )

    # Create a chat engine with the custom synthesizer and GPT-4 model
    llm = OpenAI(model="gpt-4")
    chat_engine = vector_index.as_chat_engine(
        llm=llm,
        retriever=recursive_retriever,
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
