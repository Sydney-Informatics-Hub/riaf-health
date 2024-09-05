"""
This module contains test examples for the RAGscholar class using the use case studies.

To run the tests, configure secrets.toml in the current working directory (cwd),
or alternatively setup your environment with the following keys:
os.environ["OPENAI_API_KEY"] = "xxx"
os.environ["BING_SEARCH_V7_SUBSCRIPTION_KEY"] = "xxx"


add export PYTHONPATH="/Users/nbut3013/PROJECTS/PIPE-4668-RIAF/PIPE-4668-RIAF_NSWHEALTH/ragpipe:$PYTHONPATH"
Alternatively the path to the keys is needed (by default in the tests the keys are read from the files).

Conda env: fmm

cd ragpipe
python tests/use_case_studies.py run1
"""

from rag import RAGscholar
from utils.envloader import load_api_key
import time
import os,sys
# Imports for Langfuse tracing and eval
from llama_index.core import Settings
from llama_index.core.callbacks import CallbackManager
from langfuse.llama_index import LlamaIndexCallbackHandler
#from langfuse.decorators import langfuse_context, observe

ENABLE_LANGFUSE_CALLBACKS = True
PATH_LOCAL_DOCS = './templates/docs'
PATH_LOCAL_DATA = './templates/data'



def test_RAGscholar_run1():

    time_now = time.time()
    rag = RAGscholar(path_templates = './templates/',
                    fname_system_prompt = 'Prompt_context.md',
                    fname_report_template = 'Report.md',
                    outpath = '../../results/',
                    path_index = '../../index_store',
                    path_documents = None, #'../test_data/Weiss_docs',
                    language_style = "analytical",
                    load_index_from_storage = False)
    query_author="Anthony Weiss"
    query_topic="Elastagen"
    keywords = "elastin, tissue engineering, elastagen"
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
            impact_period_end,
            scholarai_delete_pdfs = False,
            local_document_path = PATH_LOCAL_DOCS,
            local_data_path = PATH_LOCAL_DATA
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
                    path_documents = '../test_data/Nursing_docs',
                    language_style = "analytical",
                    load_index_from_storage = False,
)
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
            scholarai_delete_pdfs = False,
            local_document_path = PATH_LOCAL_DOCS,
            local_data_path = PATH_LOCAL_DATA,
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
                    path_documents = None) #'../test_data/Ice_docs')
    query_author="Cath Chapman, Steph Kershaw" #"Cath Chapman" #Steph Kershaw
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
            impact_period_end,
            local_document_path = PATH_LOCAL_DOCS,
            local_data_path = PATH_LOCAL_DATA,
            )
    print(f"Time taken: {round(time.time() - time_now, 2)} seconds")
    # typical time with OpenAI API call: 119.57 seconds
    # typical time with Azure OpenAI API call: 103.24 seconds


def test_RAGscholar_run4():

    time_now = time.time()
    rag = RAGscholar(path_templates = './templates/',
                    fname_system_prompt = 'Prompt_context.md',
                    fname_report_template = 'Report.md',
                    outpath = '../../results/',
                    path_index = '../../index_store',
                    path_documents = None) #'../test_data/Ice_docs')
    query_author="Martin Pule"
    query_topic="Next-generation programmed T cell therapies for cancer treatment: innovation, validation and development through the spin-out company, Autolus Ltd"
    keywords = "cancer, Autolus"
    research_period_start = 2005
    research_period_end = 2024
    impact_period_start = 2005
    impact_period_end = 2024
    organisation = "University College London"
    rag.run(query_topic,
            query_author,
            keywords,
            organisation,
            research_period_start,
            research_period_end,
            impact_period_start,
            impact_period_end,
            local_document_path = PATH_LOCAL_DOCS,
            local_data_path = PATH_LOCAL_DATA,
            )
    print(f"Time taken: {round(time.time() - time_now, 2)} seconds")

def test_RAGscholar_run5():
    time_now = time.time()
    rag = RAGscholar(path_templates = './templates/',
                    fname_system_prompt = 'Prompt_context.md',
                    fname_report_template = 'Report.md',
                    outpath = '../../results/',
                    path_index = '../../index_store',
                    path_documents = None) #'../test_data/Ice_docs')
    query_author="Steve Goodacre, Praveen Thokala"
    query_topic="Reducing hospital admissions for suspected heart attack"
    keywords = "heart attack, hospital admissions"
    research_period_start = 2010
    research_period_end = 2013
    impact_period_start = 2014
    impact_period_end = 2020
    organisation = "University of Sheffield"
    rag.run(query_topic,
            query_author,
            keywords,
            organisation,
            research_period_start,
            research_period_end,
            impact_period_start,
            impact_period_end,
            local_document_path = PATH_LOCAL_DOCS,
            local_data_path = PATH_LOCAL_DATA,
            )
    print(f"Time taken: {round(time.time() - time_now, 2)} seconds")

def test_RAGscholar_run6():
    time_now = time.time()
    rag = RAGscholar(path_templates = './templates/',
                    fname_system_prompt = 'Prompt_context.md',
                    fname_report_template = 'Report.md',
                    outpath = '../../results/',
                    path_index = '../../index_store',
                    path_documents = None) #'../test_data/Ice_docs')
    query_author="Bryan Williams"
    query_topic="Transforming national and international clinical practice in the treatment of resistant hypertension"
    keywords = "hypertension"
    research_period_start = 2009
    research_period_end = 2019
    impact_period_start = 2013
    impact_period_end = 2020
    organisation = "University College London"
    rag.run(query_topic,
            query_author,
            keywords,
            organisation,
            research_period_start,
            research_period_end,
            impact_period_start,
            impact_period_end,
            local_document_path = PATH_LOCAL_DOCS,
            local_data_path = PATH_LOCAL_DATA,
            )
    print(f"Time taken: {round(time.time() - time_now, 2)} seconds")


def test_RAGscholar_run7():
    time_now = time.time()
    rag = RAGscholar(path_templates = './templates/',
                    fname_system_prompt = 'Prompt_context.md',
                    fname_report_template = 'Report.md',
                    outpath = '../../results/',
                    path_index = '../../index_store',
                    path_documents = None) #'../test_data/Ice_docs')
    query_author="Jane Lewis"
    query_topic="Saving lives and limbs: Mauritius first systematic Peripheral Arterialisease screening programme for people with Diabetes."
    keywords = "Arterialisease, Diabetes"
    research_period_start = 2014
    research_period_end = 2020
    impact_period_start = 2014
    impact_period_end = 2020
    organisation = "Cardiff Metropolitan University"
    rag.run(query_topic,
            query_author,
            keywords,
            organisation,
            research_period_start,
            research_period_end,
            impact_period_start,
            impact_period_end,
            local_document_path = PATH_LOCAL_DOCS,
            local_data_path = PATH_LOCAL_DATA,
            )
    print(f"Time taken: {round(time.time() - time_now, 2)} seconds")


def test_RAGscholar_run8():
    time_now = time.time()
    rag = RAGscholar(path_templates = './templates/',
                    fname_system_prompt = 'Prompt_context.md',
                    fname_report_template = 'Report.md',
                    outpath = '../../results/',
                    path_index = '../../index_store',
                    path_documents = None) #'../test_data/Ice_docs')
    query_author="Mark Achtman"
    query_topic="EnteroBase, a platform for analysis of bacterial genomes to trace foodborne bacterial disease outbreaks"
    keywords = "EnteroBase, foodborne bacterial disease, bacterial genomes, disease outbreaks"
    research_period_start = 2014
    research_period_end = 2020
    impact_period_start = 2017
    impact_period_end = 2020
    organisation = "University of Warwick"
    rag.run(query_topic,
            query_author,
            keywords,
            organisation,
            research_period_start,
            research_period_end,
            impact_period_start,
            impact_period_end,
            local_document_path = PATH_LOCAL_DOCS,
            local_data_path = PATH_LOCAL_DATA,
            )
    print(f"Time taken: {round(time.time() - time_now, 2)} seconds")


def test_RAGscholar_run9():
    time_now = time.time()
    rag = RAGscholar(path_templates = './templates/',
                    fname_system_prompt = 'Prompt_context.md',
                    fname_report_template = 'Report.md',
                    outpath = '../../results/',
                    path_index = '../../index_store',
                    path_documents = None)
    query_author="Ioan Humphreys, Tessa Watts, Ruth Davies, Deborah Fitzsimmons"
    query_topic="Enabling cost savings and improved prevention and management of chronic oedema through the assessment of the health and economic benefits of lymphoedema care"
    keywords = "oedema, lymphoedema care"
    research_period_start = 2014
    research_period_end = 2020
    impact_period_start = 2017
    impact_period_end = 2020
    organisation = "Swansea University"
    rag.run(query_topic,
            query_author,
            keywords,
            organisation,
            research_period_start,
            research_period_end,
            impact_period_start,
            impact_period_end,
            local_document_path = PATH_LOCAL_DOCS,
            local_data_path = PATH_LOCAL_DATA,
            )
    print(f"Time taken: {round(time.time() - time_now, 2)} seconds")

def test_RAGscholar_run10():
    time_now = time.time()
    rag = RAGscholar(path_templates = './templates/',
                    fname_system_prompt = 'Prompt_context.md',
                    fname_report_template = 'Report.md',
                    outpath = '../../results/',
                    path_index = '../../index_store',
                    path_documents = None)
    query_author="Trish Houghton, Jane Howarth, Bimpi Kuti"
    query_topic="Supplying the demand: increasing the nursing workforce and addressing NHS patient needs with the design, and implementation of the Bolton Model in Nurse Education."
    keywords = "nursing, Bolton Model, Nurse Education"
    research_period_start = 2013
    research_period_end = 2015
    impact_period_start = 2015
    impact_period_end = 2024
    organisation = "University of Bolton"
    rag.run(query_topic,
            query_author,
            keywords,
            organisation,
            research_period_start,
            research_period_end,
            impact_period_start,
            impact_period_end,
            local_document_path = PATH_LOCAL_DOCS,
            local_data_path = PATH_LOCAL_DATA,
            )
    print(f"Time taken: {round(time.time() - time_now, 2)} seconds")


if __name__ == '__main__':

    if ENABLE_LANGFUSE_CALLBACKS:
        load_api_key(toml_file_path='secrets.toml')
        langfuse_callback_handler = LlamaIndexCallbackHandler(
        secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
        public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
        host="https://cloud.langfuse.com"
        )
        Settings.callback_manager = CallbackManager([langfuse_callback_handler]) 
    if 'run1' in sys.argv:
        test_RAGscholar_run1()
    elif 'run2' in sys.argv:
        test_RAGscholar_run2()
    elif 'run3' in sys.argv:
        test_RAGscholar_run3()
    if ENABLE_LANGFUSE_CALLBACKS:
        langfuse_callback_handler.flush()
