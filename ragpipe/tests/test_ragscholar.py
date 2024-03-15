from rag import RAGscholar

def test_RAGscholar():
    rag = RAGscholar(path_index = '../../index_store', 
                     path_openai_key = '../../openai_sih_key.txt', 
                     load_index_from_storage = True)
    
    #query_space = "Emergency nursing care, Kate Curtis, University of Sydney"
    #rag.generate_index(query_space)
    query = "Find publication sources related to 'emergency nursing care' by Kate Curtis from the University of Sydney"
    response_publications = rag.query_index_from_docs(query, top_k = 5)

    query = """
    Write about research impact for 'Improving the safety and quality of emergency nursing care' 
    by Kate Curtis from the University of Sydney"
    """
    response_query = rag.query_llm_index(query, top_k = 5)
