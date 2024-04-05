# Query engine functions

import logging
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import get_response_synthesizer
from llama_index.core.query_engine import CitationQueryEngine

class QueryEngine:
    """
    Query engine class
    """

    def generate_query_engine(self, index,top_k=10):
            if index is None:
                logging.error("Index not found")
                return None
            
            # Define index retriever
            retriever = VectorIndexRetriever(
                index=index,
                similarity_top_k=top_k,
            )

            # configure response synthesizer
            response_synthesizer = get_response_synthesizer()

            # assemble query engine
            query_engine = RetrieverQueryEngine(
                retriever=retriever,
                response_synthesizer=response_synthesizer,
                node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)],
            )
            return query_engine
        
    def query_llm_index(self, query, top_k = 10):
        """
        Query index for relevant publications to question.
        """
        # assemble query engine
        query_engine = self.generate_query_engine(top_k = top_k)

        # query
        response = query_engine.query(query)
        return response
    
    def query_publication_index(self, query, index, top_k = 5):
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

    def query_index_from_docs(self, query, index, top_k = 5):
        """
        Query index for relevant publications to question.
        """
        if index is None:
            logging.error("Index not found")
            return None
        else:
            return self.query_publication_index(query, index, top_k = top_k)