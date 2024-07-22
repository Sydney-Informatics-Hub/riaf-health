# Custom Chatengine for the chatbot
"""
ToDo:
- check Semantic Chunker: https://docs.llamaindex.ai/en/latest/examples/node_parsers/semantic_chunking/ 
"""
import os
from llama_index.core import ServiceContext, VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.prompts import PromptTemplate
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.llms.openai import OpenAI
from llama_index.core.retrievers import RecursiveRetriever
from llama_index.core.schema import IndexNode
from llama_index.core.extractors import SummaryExtractor, QuestionsAnsweredExtractor
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.response.pprint_utils import pprint_response
# Imports for Langfuse tracing and eval
from llama_index.core import Settings
from llama_index.core.callbacks import CallbackManager
from langfuse.llama_index import LlamaIndexCallbackHandler

from typing import List, Optional
from llama_index.core.chat_engine import ContextChatEngine
from llama_index.core.response_synthesizers import BaseSynthesizer
from llama_index.core.schema import  NodeWithScore
from llama_index.core.response import Response



ENABLE_LANGFUSE_CALLBACKS = True



class NodeIDTrackingSynthesizer(BaseSynthesizer):
    def __init__(self, **kwargs):
        super().__init__(llm=OpenAI(model = 'gpt-4o'), **kwargs)
        self.node_id_map = {}

    def _get_prompts(self):
        return {}

    def _update_prompts(self, prompts):
        pass

    async def aget_response(self, query_str: str, text_chunks: List[str], **kwargs) -> Response:
        # This is just a placeholder. In practice, you'd implement the async version here.
        return await self.get_response(query_str, text_chunks, **kwargs)

    def get_response(
        self,
        query_str: str,
        text_chunks: List[str],
        **kwargs
    ) -> Response:
        # Create a mapping of placeholder IDs to actual node IDs
        self.node_id_map = {f"NODE_{i}": f"node_{i}" for i in range(len(text_chunks))}
        
        # Modify the context input to include placeholder node IDs
        context_str = "\n\n".join([
            f"NODE_{i}: {chunk}"
            for i, chunk in enumerate(text_chunks)
        ])

        # Create a prompt that includes instructions to use node IDs
        prompt_template = PromptTemplate(
            "Answer the question based on the context below. "
            "After each statement in your response, include the node ID "
            "in parentheses like this: (NODE_X), where X is the number "
            "of the node you used for that information.\n"
            "Context: {context_str}\n"
            "Question: {query_str}\n"
            "Answer: "
        )

        # Generate the response using the LLM
        response = self._llm.complete(
            prompt_template.format(context_str=context_str, query_str=query_str)
        )

        # Replace placeholder node IDs with actual node IDs
        final_response = response.text
        for placeholder, actual_id in self.node_id_map.items():
            final_response = final_response.replace(placeholder, actual_id)

        return Response(final_response)

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

    if ENABLE_LANGFUSE_CALLBACKS:
        load_api_key(toml_file_path='secrets.toml')
        langfuse_callback_handler = LlamaIndexCallbackHandler(
        secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
        public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
        host="https://cloud.langfuse.com"
        )
        Settings.callback_manager = CallbackManager([langfuse_callback_handler]) 

    chunk_size=512
    
    # Load your documents and create the index
    documents = SimpleDirectoryReader('../test_data/documents_to_add').load_data()
    index = VectorStoreIndex.from_documents(documents, chunk_size=chunk_size)

    # Generate system prompt and create chat engine
    system_prompt = "You are a helpful AI assistant. Always provide source references for your answers."
    chat_engine = generate_chatengine_context(system_prompt, index, "gpt-4o")

    # Query the chat engine
    query = ("What are the main research priorities in NSW and Australia? Back up statements with a reference to the document in the format:\n"
             "text ... [Reference: {'source': ..., 'n0de_id': ..., 'reference_snippet': ...}]\n"
             "The reference should include relevant metadata and the node_id: X, where X is the number of the node you used for that information.\n"
             "The output must be in markdown format.\n")
    # --> node_id is not referenceing the actual node but just a number of the reference
             

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

    if ENABLE_LANGFUSE_CALLBACKS:
        langfuse_callback_handler.flush()
    
    assert content is not None and sources is not None


test_custom_synthesizer():

    if ENABLE_LANGFUSE_CALLBACKS:
        load_api_key(toml_file_path='secrets.toml')
        langfuse_callback_handler = LlamaIndexCallbackHandler(
        secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
        public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
        host="https://cloud.langfuse.com"
        )
        Settings.callback_manager = CallbackManager([langfuse_callback_handler]) 

    chunk_size=512

    # Load your documents and create the index
    documents = SimpleDirectoryReader('../test_data/documents_to_add').load_data()
    index = VectorStoreIndex.from_documents(documents, chunk_size=chunk_size)

    # Generate system prompt and create chat engine
    system_prompt = "You are a helpful AI assistant. Always provide source references for your answers."

    custom_synthesizer = NodeIDTrackingSynthesizer()

    # Create the chat engine with the custom synthesiz
    memory = ChatMemoryBuffer.from_defaults(token_limit=10000)

    chat_engine = index.as_chat_engine(
        system_prompt=system_prompt,
        memory=memory,
        llm = OpenAI(model = "gpt-4o"),
        similarity_top_k=10,
        verbose=True,
        response_synthesizer=custom_synthesizer
        )




    # Query the chat engine
    query = ("What are the main research priorities in NSW and Australia? Back up statements with a reference to the document in the format:\n"
             "text ... [Reference: {'source': ..., 'node_id': ..., 'reference_snippet': ...}]\n"
             "The reference should include relevant metadata and the node_id: X, where X is the number of the node you used for that information.\n"
             "The output must be in markdown format.\n")
    # --> node_id is not referenceing the actual node but just a number of the reference
             

    response = chat_engine.chat(query)

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

    if ENABLE_LANGFUSE_CALLBACKS:
        langfuse_callback_handler.flush()
    
    assert content is not None and sources is not None
