from rag import RAGscholar

def test_RAGscholar_run1():
    
    rag = RAGscholar(path_templates = './templates/',
                    fname_system_prompt = 'Prompt_context.md',
                    fname_report_template = 'Report.md',
                    outpath = '../../results/',
                    path_index = '../../index_store', 
                    path_openai_key = '../../openai_sih_key.txt')
    query_author="Anthony Weiss"
    query_topic="Elastin"
    research_period = "2013-2021"
    impact_period = "2013-2023"
    organisation = "University of Sydney"
    rag.run(query_topic, 
            query_author,
            research_period,
            impact_period,
            organisation)
    
def test_RAGscholar_run2():
    
    rag = RAGscholar(path_templates = './templates/',
                    fname_system_prompt = 'Prompt_context.md',
                    fname_report_template = 'Report.md',
                    outpath = '../../results/',
                    path_index = '../../index_store', 
                    path_openai_key = '../../openai_sih_key.txt')
    query_author="Kate Curtis"
    query_topic="Improving emergency nursing care"
    research_period = "2017-2018"
    impact_period = "2017-2023"
    organisation = "University of Sydney"
    rag.run(query_topic, 
            query_author,
            research_period,
            impact_period,
            organisation)
    
def test_RAGscholar_run3():
    
    rag = RAGscholar(path_templates = './templates/',
                    fname_system_prompt = 'Prompt_context.md',
                    fname_report_template = 'Report.md',
                    outpath = '../../results/',
                    path_index = '../../index_store', 
                    path_openai_key = '../../openai_sih_key.txt')
    query_author="Cath Chapman, Steph Kershaw"
    query_topic="Online resources to reduce the impact of crystal methamphetamine harms in the community"
    research_period = "2017-2023"
    impact_period = "2017-2023"
    organisation = "Matilda Centre"
    rag.run(query_topic, 
            query_author,
            research_period,
            impact_period,
            organisation)