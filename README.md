# AI Generator for Research Impact Assessment Studies

## Introduction

To measure health and medical research impact, a new Research Impact Assessment Framework (RIAF) has been developed. The RIAF evaluates the research environment and the alignment and influence of research, with the goal of providing funders a holistic analysis of NSW’s health and medical research ecosystem for making informed investment decisions.

To improve the scalability of this framework, an AI powered software has been developed that allows researchers and funding organisations to generate assessment reports about the research impact for a given research group and topic. Research impact is evaluated along distinct criteria such as overall problem addressed, research impact-to-date, and potential future applications. The current design of the case study template includes four assessment criteria and provides researchers the freedom to use a set of indicators that are relevant to their research program (e.g. research/impact period). 

The AI generator combines Large Language Models (LLM) with factual knowledge retrievers such as scholar publications and web content. For a complete overview of retrievers see modules in directory ragpipe/retrievers.

## Installation

Please follow the installations steps as outlined below

1) Clone github repo:
```shell
git clone git@github.sydney.edu.au:informatics/PIPE-4668-RIAF_NSWHEALTH.git
cd PIPE-4668-RIAF_NSWHEALTH/ragpipe
```

To install dependencies, ensure you have Mamba or Conda installed. Then install dependencies:

```shell
conda install -f environment.yaml
```

Activate environment:

```shell
conda activate azure_ai
```


## Use-case examples

Example how to generate assessment report can be found in the file `tests/use_case_studies`.


## RAG Pipeline

The software pipeline `ragpipe` automatically generates a research impact use-case study for a given topic and author. The pipeline includes the following steps:

1. Templates: context instructions and question prompts (see folder 'ragpipe/templates')
2. User input: via CLI or config file (see main.py)
    - Topic
    - Author
    - Keywords
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


## Project Partners

- Janine Richards <janine.richards@sydney.edu.au>
- Mona Shamshiri <mona.shamshiri@sydney.edu.au>


## Attribution and Acknowledgement

Acknowledgments are an important way for us to demonstrate the value we bring to your research. Your research outcomes are vital for ongoing funding of the Sydney Informatics Hub.

If you make use of this software for your research project, please include the following acknowledgment:

“This research was supported by the Sydney Informatics Hub, a Core Research Facility of the University of Sydney."