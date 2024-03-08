# AI Generator for Research Impact Assessment Studies

## Introduction

To measure health and medical research impact, a new Research Impact Assessment Framework (RIAF) has been developed. The RIAF evaluates the research environment and the alignment and influence of research, with the goal of providing funders a holistic analysis of NSW’s health and medical research ecosystem for making informed investment decisions.

The current design of the case study template includes four questions and gives researchers the freedom to use a set of indicators that are 
relevant to their research program. Use of AI-powered LLM solutions would improve the scalability of the framework and reduce the burden on participants.

This project aims to develop software and AI solutions to generate use-case studies and their research impact.

## RAG Pipeline

The software pipeline `ragpipe` automatically generates a research impact use-case study for a given topic and author. The pipeline includes the following steps:

1. Templates: context instructions and question prompts (see folder 'ragpipe/templates')
2. User input: via CLI or config file (see main.py)
    - Topic
    - Author
    - Organisation
    - Research period
    - Research impact period.
3. Data search engines (see folder ragpipe/retriever): Retrieving relevant publications (arXiv, SemanticScholar, GoogleScholar).
4. Data reader: Reading data from these sources and text conversion
5. Data index generator: Index data, extract metadata and store content as vector database (see 'ragpipe/indexengine/process.py')
6. RAG engine (see 'ragpipe/rag.py'): Retrieving context based on:
    - query
    - instructions
    - publication content vector embeddings
    - publication metadata
7. LLM multi-stage prompt engine: Iterate over questions and check answers
8. Reference engine: retrieve corresponding publication references and convert to readable format  (see 'ragpipe/utils/pubprocess.py')
9. Report generator: produce, format, and save the final use case study report (see 'ragpipe/rag.py')
10. Report conversion (Optional): Converting the report into different formats (Markdown, HTML, PDF, DOCX).

## Installation
```
conda create -n riaf python=3.11
conda activate riaf
pip install semanticscholar==0.7.0 arxiv==2.1.0 llama-index==0.9.30 llama-hub==0.0.71 llama-index-core==0.10.3 llama-index-readers-web==0.1.2 pypdf2==3.0.1
pip install  llama-index-core==0.10.3
```

## Project Partners

- Janine Richards <janine.richards@sydney.edu.au>
- Mona Shamshiri <mona.shamshiri@sydney.edu.au>


## Attribution and Acknowledgement

Acknowledgments are an important way for us to demonstrate the value we bring to your research. Your research outcomes are vital for ongoing funding of the Sydney Informatics Hub.

If you make use of this software for your research project, please include the following acknowledgment:

“This research was supported by the Sydney Informatics Hub, a Core Research Facility of the University of Sydney."