from rag import RAGscholar
import time
import os

#os.environ["OPENAI_API_KEY"] = ""
#os.environ["BING_SEARCH_V7_SUBSCRIPTION_KEY"] = ""

def test_RAGscholar_run1():
    
    time_now = time.time()
    rag = RAGscholar(path_templates = './templates/',
                    fname_system_prompt = 'Prompt_context.md',
                    fname_report_template = 'Report.md',
                    outpath = '../../results/',
                    path_index = '../../index_store', 
                    #path_openai_key = '../../openai_sih_key.txt'
                    path_openai_key = '../../azure_openai_techlab_key.txt')
    query_author="Anthony Weiss"
    query_topic="Elastagen"
    keywords = "elastin, tissue engineering"
    research_period_start = 2013
    research_period_end = 2023
    impact_period_start = 2013
    impact_period_end = 2023
    organisation = "University of Sydney"
    rag.run(query_topic, 
            query_author,
            keywords,
            organisation,
            research_period_start,
            research_period_end,
            impact_period_start,
            impact_period_end
            )
    print(f"Time taken: {round(time.time() - time_now, 2)} seconds")
    # typical time with OpenAI API call (gpt-4-1106-preview)): 107.51 seconds
    # typical time with Azure OpenAI API call (gpt-4-1106-preview): 
    # typical time with Azure OpenAI API call (gpt-4-32k): 92.18 seconds
    # time with scholarai and websearch: 531.49 seconds
    
def test_RAGscholar_run2():
    
    time_now = time.time()
    rag = RAGscholar(path_templates = './templates/',
                    fname_system_prompt = 'Prompt_context.md',
                    fname_report_template = 'Report.md',
                    outpath = '../../results/',
                    path_index = '../../index_store', 
                    path_openai_key = '../../openai_sih_key.txt')
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
            impact_period_end
            )
    print(f"Time taken: {round(time.time() - time_now, 2)} seconds")
    # typical time with OpenAI API call: 102.06 seconds
    # typical time with Azure OpenAI API call: 87.75 seconds
    
def test_RAGscholar_run3():
    
    time_now = time.time()
    rag = RAGscholar(path_templates = './templates/',
                    fname_system_prompt = 'Prompt_context.md',
                    fname_report_template = 'Report.md',
                    outpath = '../../results/',
                    path_index = '../../index_store', 
                    path_openai_key = '../../openai_sih_key.txt')
    query_author="Cath Chapman, Steph Kershaw"
    query_topic="Online resources to reduce the impact of crystal methamphetamine harms in the community"
    keywords = "methamphetamine, ice"
    research_period_start = 2017
    research_period_end = 2023
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
            impact_period_end
            )
    print(f"Time taken: {round(time.time() - time_now, 2)} seconds")
    # typical time with OpenAI API call: 119.57 seconds
    # typical time with Azure OpenAI API call: 103.24 seconds