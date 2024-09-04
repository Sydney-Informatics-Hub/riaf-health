# AI Generator for Research Impact Assessment Studies
<img width="1003" alt="Architecture" src="https://media.github.sydney.edu.au/user/291/files/a12249da-0c72-4f9d-a8a5-1e9677a6de18">

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

2) To install dependencies, ensure you have Mamba or Conda installed. Then install dependencies with the following command:

```shell

conda env update --file environment.yaml 
conda activate riaf
```

If the installation fails, please try to install the dependencies with environment_all.yaml or use the `--prune` flag to remove unused packages.


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

Add your `azure_sih_bing_key.txt` to the top level directory.
Add your `openai_sih_key.txt` to the top level directory.

### Quick start

Modify `ragpipe/tests/use_case_studies.py` then launch the script.

```shell
cd ragpipe
python tests/use_case_studies.py run1
```

### Run from Frontend App

Launch the frontend app

```shell
cd ragpipe
streamlit run app.py
```

Modify options and execute. Check `app.py` for any hardcoded configuration options.

### All options

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
- `--additional_context`: Additional context for the use case study

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

## Deployment with Docker

Config nginx:
```bash
sudo apt install nginx
sudo systemctl start nginx
sudo systemctl enable nginx
sudo nano /etc/nginx/sites-available/default
```
and paste the settings as shown in `nginx_settings.config`. 
Feel free to edit or add more.

The Dockerfile is located in the folder `ragpipe`. To build the Dockerimage run:
```bash
sudo docker build -t streamlit-app . 
```

Run docker image and restart nginx:
```bash
docker run -d -p 8501:8501  streamlit-app
sudo systemctl restart nginx
```
This will make the streamlit ap available on the IP and port (here 8501) as configured in Dockerfile, nginx and instance network url.

- If you want to stop the container:
```bash
docker ps
docker container stop <CONTAINER ID>
```
- To start the the Docker service automatically:
```bash
sudo systemctl enable docker
```



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
