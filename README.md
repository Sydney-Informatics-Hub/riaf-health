# AI Generator for Research Impact Assessment Studies (ResearchPulse)

> [!WARNING]
> **This repository is not actively maintained and has been archived.**
> 
> Please note:
> - Some functions may not work as expected
> - Dependencies are outdated and may have security vulnerabilities
> - No updates or bug fixes will be provided
> - Issues and pull requests will not be reviewed
> - Consider forking if you need an actively maintained version

---

## Introduction

This AI software generates research impact assessment studies for health and medical research, in accordance with the Research Impact Assessment Framework (RIAF). The RIAF evaluates the research environment and the alignment and influence of research, with the goal of providing funders a holistic analysis of NSW's health and medical research ecosystem for making informed investment decisions.

To improve the scalability of this framework, an AI powered software has been developed that allows researchers and funding organisations to generate assessment reports about the research impact for a given research group and topic. Research impact is evaluated along distinct criteria such as overall problem addressed, research impact-to-date, and potential future applications. The current design of the case study template includes four assessment criteria and provides researchers the freedom to use a set of indicators that are relevant to their research program (e.g. research/impact period).

The AI generator combines Large Language Models (LLM) with factual knowledge retrievers such as scholar publications and web content. 


## Output Results

- Research impact report (word docx and markdown)
- Context analysis (text file)
- Input settings (text file)
- Table of relevant document for manual download (automatic download restricted)
- Source documents (documents that are included in analysis)
- Log file
- Files of individual answers for each questions, before and after review

## Comprehensive Impact Analysis

Our intelligent system combines four powerful components:

1. **Smart Publication Analysis**
   - Multi-source academic database integration (ArXiv, PubMed Central, Semantic Scholar)
   - Intelligent publication filtering and citation-based ranking
   - Automated PDF processing and metadata extraction

2. **Web Intelligence**
   - Real-time web content analysis
   - Multi-format content processing
   - Automated relevance assessment

3. **Data Catalogue Integration**
   - Automated processing of health and medical data catalogues
   - Evidence-based impact metrics
   - Intelligent data relevance ranking

4. **Local Document Processing**
   - Seamless integration of your research documents
   - Multi-format support (PDF, DOCX)
   - Automated metadata extraction

## Local Installation

Please follow the installations steps as outlined below

1) Clone github repo:
```shell
# Using HTTPS
git clone https://github.com/Sydney-Informatics-Hub/riaf-health.git
cd riaf-health/ragpipe

# OR using SSH
git clone git@github.com:Sydney-Informatics-Hub/riaf-health.git
cd riaf-health/ragpipe
```

2) To install dependencies, ensure you have Mamba or Conda installed. Then install dependencies with the following command:

```shell
# Create and activate the environment
conda env create -f environment.yaml
conda activate riaf
```

If the installation fails, please try to install the dependencies with `environment_all.yaml` or use the `--prune` flag to remove unused packages:

```shell
conda env update --file environment.yaml --prune
```


3) Set up OpenAI API and the Bing search API key. Create a file `secrets.toml` under the root directory (directory where you run the code from) and add the following content:

```toml
# Required: OpenAI API Key
OPENAI_API_KEY="your_openai_api_key"

# Required: Choose ONE of the following API types

# Option 1: If you are using the API service provided by OpenAI:
OPENAI_API_TYPE="openai"

# Option 2: If you are using the API service provided by Microsoft Azure:
# OPENAI_API_TYPE="azure"
# AZURE_API_BASE="your_azure_api_base_url"
# AZURE_API_VERSION="your_azure_api_version"

# Required: Bing Search API Key
BING_SEARCH_API_KEY="your_bing_api_key"

# Required: Email for NCBI database access via biopython
NCBI_EMAIL="your_ncbi_email"

# Optional: Langfuse for LLM monitoring and tracing
LANGFUSE_SECRET_KEY="langfuse_secret_key"
LANGFUSE_PUBLIC_KEY="langfuse_public_key"
```

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


## Deployment with Docker

**Prerequisites:**
- Docker installed and running
- nginx installed
- Appropriate network permissions

Config nginx:
```bash
sudo apt install nginx
sudo systemctl start nginx
sudo systemctl enable nginx
sudo nano /etc/nginx/sites-available/default
```
and paste the settings as shown in `nginx_settings.config`. 
Feel free to edit or add more.

The Dockerfile is located in the folder `ragpipe`. To build the Docker image run:
```bash
sudo docker build -t streamlit-app . 
```

Run docker image and restart nginx:
```bash
docker run -d -p 8501:8501 streamlit-app
sudo systemctl restart nginx
```
This will make the streamlit app available on the IP and port (here 8501) as configured in Dockerfile, nginx and instance network url.

**Common Docker commands:**

- If you want to stop the container:
```bash
docker ps
docker container stop <CONTAINER ID>
```
- To start the Docker service automatically:
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
2. Data search engines (see folder ragpipe/retriever): Retrieving relevant publications (arXiv, SemanticScholar, Pubmed Central, Bing).
3. Data reader: Reading data from these sources and text conversion
4. Data index generator: Index data, extract metadata and store content as vector database (see 'ragpipe/indexengine/process.py')
5. General context generation: problem and context analyser, find missing information online, add to context memory.
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
    - author background check
    - find missing information online
    - generate context memory
- Data-source search and retrieval agents:
    1. Publications: search, filter, relevance ranking, content extraction, metadata generation
    2. Web Content: online search (via Bing API), filter, content retrieval, metadata generation
    3. Directory Reader: read all documents from a local directory, add to LLM database
    4. Data extractor from Health data catalogue such as burden of disease catalogues
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

## FAQ

<details>
<summary>What is ResearchPulse?</summary>

ResearchPulse is an AI-powered tool designed to automate the generation of research impact assessment use case studies, specifically for health and medical research. It applies the Research Impact Assessment Framework (RIAF) to evaluate research environments and their influence within a specific research ecosystem. The tool generates detailed use cases documenting research impact, aiding funding organizations in assessing specific research programs and their outcomes.
</details>

<details>
<summary>How does ResearchPulse work?</summary>

ResearchPulse employs a Retrieval-Augmented Generation (RAG) pipeline. It retrieves data from various sources like academic databases (PubMed, arXiv, Semantic Scholar), web content via Bing Search API, local documents, and structured health data catalogs. It then processes this information through a context engine, vector index, query engine, and review system. Finally, it generates a comprehensive research impact assessment report with references.
</details>

<details>
<summary>What are the key features and benefits of using ResearchPulse?</summary>

ResearchPulse offers a range of features including automated generation of use case studies, data processing from multiple sources, customisable research indicators, multi-format report generation, and a user-friendly web interface. The benefits include a systematic and structured approach to research impact assessment, saving time and resources, and providing evidence-based analysis to support funding decisions.

</details>

<details>
<summary>How can I get started with ResearchPulse?</summary>

You can access ResearchPulse through a hosted web interface or by installing it locally. Currently the web app requires a university network connection and login. Local installation requires a Python environment, API keys, and university network access. Detailed instructions for both methods are available in the documentation.
</details>

<details>
<summary>What kind of output does ResearchPulse generate?</summary>

ResearchPulse generates a downloadable zip file containing multiple outputs designed to ensure complete documentation and transparency. At its core, you'll receive a detailed research impact report available in both Word and Markdown formats, accompanied by context analysis documentation that details the research environment. The system also preserves individual answers for each assessment question, including both draft and final versions, allowing you to track the development of the assessment.

To support transparency and verification, the package includes all source documents used in the analysis, along with a structured table of any documents that couldn't be automatically accessed (tracked in missing_documents.xlsx).

For process validation and reproducibility, the system provides detailed logs tracking all system operations and AI process steps. All documents are exported in accessible formats, and a record of input settings ensures the assessment process can be reviewed or repeated if needed.
</details>

<details>
<summary>Can I customise the research impact assessment criteria?</summary>

Yes, ResearchPulse offers multiple customisation options to ensure your impact assessment aligns with your specific research context. Users can define custom time periods for both research activity and impact measurement, allowing for precise temporal analysis. The system's flexible framework enables you to select and prioritise relevant research indicators, whether you're focusing on academic impact, societal benefits, or economic outcomes.

You can tailor the assessment criteria to align with your research goals and funding requirements, including specific institutional or grant body frameworks. This customisation extends to language style preferences, helping you generate reports that match your intended audience's expectations. The system also allows you to incorporate additional context through supplementary documentation and custom indicators, ensuring your unique research narrative is accurately captured.
</details>


<details>
<summary>How does ResearchPulse ensure responsible AI practices and ethical use?</summary>

ResearchPulse implements several key measures to ensure responsible AI use and ethical data handling. At its core, the system uses Retrieval-Augmented Generation (RAG) to ground all outputs in verifiable sources, ensuring that generated content is consistently backed by evidence. This approach is reinforced by a multi-stage review process that validates the accuracy of all assessments.

To address potential biases, ResearchPulse integrates multiple diverse data sources and employs intelligent filtering mechanisms. The system maintains a human-in-the-loop review process, allowing researchers to validate and customise assessment criteria based on their specific field and requirements.

Transparency and accountability are maintained through extensive process documentation and logging. Data sources are clearly attributed, ensuring users can trace any claim to its origin.

Regarding security and user control, ResearchPulse operates within strict network security restrictions and processes only publicly available research data. Users maintain control over input parameters and can observe how outputs are generated, ensuring transparency throughout the assessment process.

We continuously evaluate and improve these measures through user feedback and systematic monitoring, ensuring that responsible AI principles remain central to ResearchPulse's development and operation.
</details>

<details>
<summary>What are the future development plans?</summary>

Future development plans include enhanced security features like SSO integration and private cloud deployment options, integration of international health data catalogs and media impact scoring, and expansion to other research domains beyond health and medical research.
</details>

<details>
<summary>How can I contribute to development or report issues?</summary>

All development activities and issue reporting are managed through a GitHub repository at the University of Sydney. Users with access can contribute to the project and report issues or feature requests through the repository's issue tracker.
</details>


## Main Software Contributors

- Sebastian Haan
- Nathanial Butterworth

## Project Partners

This project has been developed in collaboration with the Faculty of Medicine and Health and the Sydney Informatics Hub at the University of Sydney.

## Attribution and Acknowledgement

Acknowledgments are an important way for us to demonstrate the value we bring to your research. Your research outcomes are vital for ongoing funding of the Sydney Informatics Hub.

If you make use of this software for your research project, please include the following acknowledgment:

"This research was supported by the Sydney Informatics Hub, a Core Research Facility of the University of Sydney."