import sys
sys.path.append('/Users/nbut3013/PROJECTS/PIPE-4668-RIAF_NSWHEALTH/ragpipe/')
from rag import RAGscholar
import time

def test_RAGscholar():
    time_now = time.time()
    rag = RAGscholar(path_templates = './templates/',
                    fname_system_prompt = 'Prompt_context.md',
                    fname_report_template = 'Report.md',
                    outpath = '../../results/',
                    path_index = '../../index_store', 
                    path_openai_key = '../openai_techlab_key.txt')
    query_author="Kate Curtis"
    query_topic="Improving the safety and quality of emergency nursing care"
    keywords = "HIRAID, emergency nursing care"
    research_period_start = 2017
    research_period_end = 2018
    impact_period_start = 2017
    impact_period_end = 2023
    organisation = "University of Sydney"
    rag.run(query_topic, 
            query_author,
            keywords,
            organisation,
            research_period_start,
            research_period_end,
            impact_period_start,
            impact_period_end,
            local_document_path = '../local_documents/'
            )
    print(f"Time taken: {round(time.time() - time_now, 2)} seconds")
    
    #query_space = "Emergency nursing care, Kate Curtis, University of Sydney"
    #rag.generate_index(query_space)
    query = "Find publication sources related to 'emergency nursing care' by Kate Curtis from the University of Sydney"
    response_publications = rag.query_index_from_docs(query, top_k = 5)

    query = """
    Write about research impact for 'Improving the safety and quality of emergency nursing care' 
    by Kate Curtis from the University of Sydney"
    """
    response_query = rag.query_llm_index(query, top_k = 5)
    print(response_query)

test_RAGscholar()