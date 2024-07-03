# AI Generator for Research Impact Assessment Studies

## Introduction

This AI software generates research impact assessment studies for health and medical research, in accordance with the Research Impact Assessment Framework (RIAF). The RIAF evaluates the research environment and the alignment and influence of research, with the goal of providing funders a holistic analysis of NSW’s health and medical research ecosystem for making informed investment decisions.

To improve the scalability of this framework, an AI powered software has been developed that allows researchers and funding organisations to generate assessment reports about the research impact for a given research group and topic. Research impact is evaluated along distinct criteria such as overall problem addressed, research impact-to-date, and potential future applications. The current design of the case study template includes four assessment criteria and provides researchers the freedom to use a set of indicators that are relevant to their research program (e.g. research/impact period).

The AI generator combines Large Language Models (LLM) with factual knowledge retrievers such as scholar publications and web content. For a complete overview of retrievers see modules in directory ragpipe/retrievers.

## Installation

Please follow the installations steps as outlined below

1) Clone github repo:
```shell
git clone git@github.sydney.edu.au:informatics/PIPE-4668-RIAF_NSWHEALTH.git
cd PIPE-4668-RIAF_NSWHEALTH/ragpipe
```

2) To install dependencies, ensure you have Mamba or Conda installed. Then install dependencies in the following order:

```shell

conda create -n riaf python=3.11
conda activate riaf
pip install semanticscholar arxiv==1.4.8 llama-index==0.10.27 pypdf2==3.0.1 pypdf==4.1.0 llama-index-readers-web==0.1.8 llama-index-readers-semanticscholar==0.1.3 llama-index-embeddings-azure-openai==0.1.6 docxtpl==0.16.8 trafilatura==1.10.0
docx2txt biopython==1.84

```

3) Set up OpenAI API and the Bing search API key. Create a file `secrets.toml` under the root directory (directory where you run the code from) and add the following content:

```shell

# Set up OpenAI API key.
OPENAI_API_KEY="your_openai_api_key"
# If you are using the API service provided by OpenAI, include the following line:
OPENAI_API_TYPE="openai"
# If you are using the API service provided by Microsoft Azure, include the following lines:
OPENAI_API_TYPE="azure"
AZURE_API_BASE="your_azure_api_base_url"
AZURE_API_VERSION="your_azure_api_version"
# Set up Bing search API key.
BING_SEARCH_API_KEY="your_bing_api_key"

```

## How-to and examples

To generate a research report run

```shell
cd ragpipe
python main.py
```
The following command line arguments are available:

- `--query_author`: Author name to search for
- `--query_topic`: Topic for Use-case Study
- `--query_keywords`: Keywords for query
- `--research_period_start`: Research period start (year)
- `--research_period_end`: Research period end (year)
- `--impact_period_start`: Impact period start (year)
- `--impact_period_end`: Impact period end (year)
- `--organisation`: Organisation
- `--language_style`: Language style for report, default='analytical'
- `--path_documents`: Path to directory with your documents, default=None
- `--path_templates`: Path to templates, default='./templates/'
- `--fname_system_prompt`: Filename for system prompt, default='Prompt_system.md'
- `--fname_report_template`: Filename for report template, default='Report.md'
- `--outpath`: Output path, default='../../results/'
- `--path_index`: Path to index, default='../../index_store'

To integrate RAGscholar in your code, add the following lines and add arguments to RAGscholar() and rag.run()
```python
from rag import RAGscholar
rag = RAGscholar(outpath = '...')
rag.run(query_topic = '...',
        query_author = [...,],
        keywords =[...,],
        organisation = '...',
        research_period_start = YEAR,
        research_period_end = YEAR,
        impact_period_start = YEAR,
        impact_period_end = YEAR
        )
```

For more details about the class arguments, see code documentation. Three examples how to generate an assessment report can be found in the file `tests/use_case_studies`.

## RAG Pipeline

A graph overview of the RAG pipeline is shown [here](./ragpipe/pipeline_overview.png).

The software pipeline `RAGscholar` (see ragpipe/rag.py) automatically generates a research impact use-case study for a given topic and author.
The pipeline includes the following steps:

1. User input: via CLI or functional arguments (see main.py)
    - Topic name
    - Author(s)
    - Keywords
    - Organisation
    - Output Directory name to store files for index database (optional)
    - Directory name that contains local files to include for analysis (optional)
    - Research period
    - Research impact period
2. Data search engines (see folder ragpipe/retriever): Retrieving relevant publications (arXiv, SemanticScholar, GoogleScholar).
3. Data reader: Reading data from these sources and text conversion
4. Data index generator: Index data, extract metadata and store content as vector database (see 'ragpipe/indexengine/process.py')
5. General context generation: define problem and context, find missing information online, add to context memory.
6. RAG engine (see 'ragpipe/rag.py'): Retrieving context based on:
    - query
    - instructions
    - data content and vector embeddings
    - metadata
    - context memory
7. LLM multi-stage prompt engine: Iterate over questions (see Prompt files in folder 'ragpipe/templates').
8. Multi-stage review. Check each answer and suggest improvements (for review criteria see Review files in folder 'ragpipe/templates').
9. Reference engine: retrieve corresponding publication references and convert to readable format  (see 'ragpipe/utils/pubprocess.py').
10. Report generator: produce, format, and save the final use case study report (see 'ragpipe/rag.py'), convert report into different formats (Markdown, HTML, PDF, DOCX).

## Features

### AI agents

- Context agent:
    - defining general problem and context information
    - find missing information online
    - generate context memory
- Data-source search and retrieval agents:
    1. Publications: search, filter, relevance ranking, content extraction, metadata generation
    2. Web Content: online search (via Bing API), filter, content retrieval, metadata generation
    3. Directory Reader: read all documents from a local directory, add to LLM database
- Database tool: index content and metadata, generate vector embeddings, query database with LLM
- Writer agent: generating impact assessment report including references
- Review agent:
    - analyse output from writer agent
    - suggest improvements
    - curate report


### Supported data source integrations:

- Scholar publications (e.g., SemanticScholar, Pubmed, ArXiv)
- Bing search and web content retrieval 
- Documents in local document folder (pdf, docx, ...)

### Other features

- citation analysis
- language style options for report
- user interface

## Main Software Contributors

- Sebastian Haan
- Nathanial Butterworth

## Project Partners

This project has been developed in collaboration with the Faculty of Medicine and Health at the UNiversity of Sydney, in particular:
- Janine Richards <janine.richards@sydney.edu.au>
- Mona Shamshiri <mona.shamshiri@sydney.edu.au>

## Attribution and Acknowledgement

Acknowledgments are an important way for us to demonstrate the value we bring to your research. Your research outcomes are vital for ongoing funding of the Sydney Informatics Hub.

If you make use of this software for your research project, please include the following acknowledgment:

“This research was supported by the Sydney Informatics Hub, a Core Research Facility of the University of Sydney."
