"""
Scholar AI class to retrieve papers from authors and topic and filter by publication period and topic.

This class add the following functionality to Semantic Scholar API:
- Filter papers by topic using LLM (GPT-3.5-turbo)
- custom filter and ranking of papers by publication period and citations
- Download open-access PDFs and retrieve full text from papers
- Store metadata and content of papers in Document objects for further LLM processing

How to use:

set environment variable OPENAI_API_KEY  with your Azure OpenAI key (default) or OpenAI key.

Python:
------ 
from retriever.scholarai import ScholarAI
scholar = ScholarAI(topic = ..., authors = [..., ...], year_start=..., year_end = ...)
papers, citations = scholar.get_papers_from_authors(max_papers = 20)
documents = scholar.load_data(papers)
------

see for example: tests/test_scholarai.py

Author: Sebastian Haan
"""

import os
import sys
import time
import requests
import logging
from semanticscholar import SemanticScholar
import arxiv
import shutil
from llama_index.llms.openai import OpenAI
# from llama_index.embeddings.azure_openai import AzureOpenAI

from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core.llms import ChatMessage
from llama_index.core.readers.base import BaseReader
from llama_index.core import Document
from PyPDF2 import PdfReader
# local imports
#sys.path.append('../')
from utils.envloader import load_api_key
from retriever.pdfdownloader import download_pdf, download_pdf_from_arxiv


#AZURE_ENDPOINT = "https://techlab-copilots-aiservices.openai.azure.com/" 
#AZURE_API_VERSION = "2023-12-01-preview" 
AZURE_ENGINE = "gpt-35-turbo"

# Outdated:
#techlab_endpoint = 'https://apim-techlab-usydtechlabgenai.azure-api.net/'
#techlab_deployment = 'GPT35shopfront'
#techlab_api_version = '2023-12-01-preview'

class ScholarAI:
    """
    ScholarAI class to retrieve papers from authors and topic and filter by publication period and topic.

    :param topic: str, topic to search for
    :param authors: list of authors
    :param year_start: int, start year of publication period
    :param year_end: int, end year of publication period
    :param outpath_pdfs: str, directory to store pdfs
    :param delete_pdfs: bool, if True, delete pdfs after processing
    :param keywords: list of keywords to filter papers
    """
    def __init__(self, 
                 topic, 
                 authors, 
                 year_start = None, 
                 year_end = None, 
                 outpath_pdfs = 'pdfs', 
                 delete_pdfs = False,
                 keywords = []):
        self.topic = topic
        self.authors = authors
        self.year_start = year_start
        self.year_end = year_end
        self.llm = None
        self.outpath_pdfs = outpath_pdfs
        self.delete_pdfs = delete_pdfs
        self.keywords = keywords

        if os.getenv("OPENAI_API_TYPE") is None:
            load_api_key('secrets.toml')
        self.llmservice = os.getenv("OPENAI_API_TYPE")
    


    def init_llm(self):
        if self.llmservice == 'openai':
            llm = OpenAI(
                temperature=0,
                model='gpt-3.5-turbo',
                max_tokens=1)
        elif self.llmservice == 'azure':
            llm = AzureOpenAI(
                engine=AZURE_ENGINE,
                model='gpt-3.5-turbo',
                temperature=0,
                azure_endpoint=os.environ['AZURE_API_BASE'],
                api_key=os.environ["OPENAI_API_KEY"],
                api_version=os.environ['AZURE_API_VERSION'],
            )
        elif self.llmservice == 'techlab':
            llm = AzureOpenAI(
                engine=techlab_deployment,
                model='gpt-3.5-turbo', 
                temperature=0,
                azure_endpoint=techlab_endpoint,
                api_key=os.environ["OPENAI_API_KEY"],
                api_version=techlab_api_version,
                api_base=os.getenv("OPENAI_API_BASE", ""),
            )
        else:
            logging.error(f"LLM service {self.llmservice} not supported")
            return None
        return llm
        

    def llmfilter(self, title, abstract):
        """
        LLM (GPT-3.5-turbo) filter to check if paper is related to topic.

        :param title: str, paper title
        :param abstract: str, paper abstract
        :param topic: str, topic to match
        """
        system_prompt = ("You are given a paper summary and a topic. Your task is to determine if the paper is related to the topic and keywords."
                        + "If the paper is related to the topic or one of the keywords, say 'yes'. Otherwise say 'no'. You must only output 'yes' or 'no'.")
        prompt = (f"Is the following paper related to the topic {self.topic} or at least one keyword in the list {self.keywords}. Please say 'yes'. Otherwise say 'no'."
                + f"\n\nPaper title: {title}\nabstract: {abstract}\n\n")
        messages = [
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=prompt),
            ]
        if self.llm is None:
            llm = self.init_llm()
        max_try = 0
        result = None
        while result is None and max_try < 3:
            try:
                response = llm.chat(messages)
                result = response.message.content.strip().lower()
            except:
                logging.error(f"LLM not responding")
                max_try += 1
                # sleep for 5 seconds to avoid rate limit
                time.sleep(5)
        logging.info(f"LLM relevant response for paper {title}: {result}")
        if result == 'yes':
            return True
        elif result == 'no':
            return False
        else:
            logging.error(f"LLM response not understood: {result}")
            return None
        
    def get_papers_from_authors(self, max_authornames = 3, max_papers = 100):
        """
        Retrieve papers from authors and filter by topic and publication period.

        :param max_authors: int, maximum number of top author names to consider that are retrieved from Semantic Scholar for each author
        :param max_papers: int, maximum number of papers to retrieve

        :return: list of papers, list of citation counts
        """
        sch = SemanticScholar()
        paper_list = []
        citations = []
        for author in self.authors:
            logging.info(f"Searching papers for author: {author}")
            results = sch.search_author(author)
            if len(results) > max_authornames:
                results = results[0:max_authornames]
            for result in results:
                papers = result.papers
                papers, citationcounts = self.filter_papers(papers)
                paper_list.extend(papers)
                citations.extend(citationcounts)
            # add delay to avoid rate limit
            time.sleep(1)
        # sort lists by citations (descending) and select top max
        idx_sorted = sorted(range(len(citations)), key=lambda k: citations[k], reverse=True)
        paper_list = [paper_list[i] for i in idx_sorted]
        if max_papers:
            paper_list = paper_list[0:max_papers]
        self.citations = citations
        return paper_list, citations

        
    def filter_papers(self, papers, filter_with_llm = True, open_access_only = False):
        """
        process papers and filter by topic and year.

        :param papers: list of papers
        :param filter_with_llm: bool, if True, filter with LLM
        :param open_access_only: bool, if True, only open access papers are returned

        :return: 
            - list of papers
            - list of citation counts
        """
        papers_ok = []
        citationcount = []
        ok = True
        if filter_with_llm:
            print(f"Checking {len(papers)} abstracts with LLM for relevance...")
        for paper in papers:
            try:
                if paper.year < self.year_start:
                    continue
                if paper.year > self.year_end:
                    continue
            except:
                continue
            if open_access_only and not paper.isOpenAccess:
                continue
            # get title
            title = getattr(paper, "title", None)
            # get abstract
            abstract = getattr(paper, "abstract", None)
            # get year
            if filter_with_llm:
                ok = self.llmfilter(title, abstract)
            if ok:
                papers_ok.append(paper)
                citationcount.append(paper.citationCount)
        print(f"Number of relevant papers found for author: {len(papers)}")
        # order by citation count
        idx_sorted = sorted(range(len(citationcount)), key=lambda k: citationcount[k], reverse=True)
        papers_ok = [papers_ok[i] for i in idx_sorted]
        citationcount = [citationcount[i] for i in idx_sorted]
        return papers_ok, citationcount

    def get_papers_from_topic(self, 
                              filter_with_llm = True, 
                              min_citation_count = 0, 
                              limit = 100,
                              open_access_only = False):
        """
        Retrieve papers from topic and filter by publication period.

        :param filter_with_llm: bool, if True, filter with LLM
        :param min_citation_count: int, minimum citation count
        :param limit: int, maximum number of papers to retrieve
        :param open_access_only: bool, if True, only open access papers are returned

        :return: list of papers, list of citation counts

        """
        sch = SemanticScholar()
        papers = sch.search_paper(self.topic, 
                                  publication_date_or_year = f'{self.year_start}:{self.year_end}',
                                  min_citation_count = min_citation_count,
                                  limit = limit,
                                  open_access_pdf = open_access_only)
        papers = papers.items
        if filter_with_llm:
            papers, citationcount = self.filter_papers(papers)
        return papers, citationcount 
    

    def get_full_text_docs(self, metadata, base_dir = 'pdfs'):
        """
        Retrieve full text from papers.

        :param metadata: dict, metadata of paper
        :param base_dir: str, directory to store pdfs

        :return: text
        """
        url = metadata["url_openAccessPdf"]
        externalIds = metadata["externalIds"]
        paper_id = metadata["paperId"]
        file_path = None
        persist_dir = os.path.join(base_dir, f"{paper_id}.pdf")
        # check if pdf exists
        if os.path.exists(persist_dir):
            logging.info(f"PDF already downloaded: {persist_dir}")
            file_path = os.path.join(persist_dir, f"{paper_id}.pdf")

        if url and not os.path.exists(persist_dir):
            # Download the document first
            file_path = download_pdf(metadata["paperId"], url, persist_dir)

        if (not url
            and externalIds
            and "ArXiv" in externalIds
            and not os.path.exists(persist_dir)):
            # download the pdf from arxiv
            file_path = download_pdf_from_arxiv(paper_id, externalIds["ArXiv"], base_dir)

        if not file_path and "ArXiv" in externalIds:
            file_path = download_pdf_from_arxiv(paper_id, externalIds["ArXiv"], base_dir)

        if file_path:
            try:
                pdf = PdfReader(open(file_path, "rb"))
            except Exception as e:
                logging.error(f"Failed to read pdf with exception: {e}. Skipping document...")
                return None

            text = ""
            for page in pdf.pages:
                text += page.extract_text()
        else:
            logging.error(f"Failed to download pdf from {url} or arxiv")
            return None

        return text


    def load_data(self, papers, full_text=True):
            """
            Loads metadata from Semantic Scholar, retrieve full text and return as list of Document objects.
            Automatically sorts papers by citation count and returns the top max_documents.

            Parameters
            ----------
            papers: list of papers
                The list of papers to retrieve full text from
            full_text: bool
                If True, retrieve full text

            Returns
            -------
            list
                The list of Document object that contains the search results
            list
                The list of missing documents
            """
            documents = []
            documents_missing = []
            if full_text:
                sch = SemanticScholar()

            for item in papers:
                openAccessPdf = getattr(item, "openAccessPdf", None)
                abstract = getattr(item, "abstract", None)
                title = getattr(item, "title", None)
                authors = [author["name"] for author in getattr(item, "authors", [])]
                year = getattr(item, "year", None)
                paper_id = getattr(item, "paperId", None)
                url_openAccessPdf = openAccessPdf.get("url") if openAccessPdf else None
                url_semanticscholar = getattr(item, "url", None)
                reference = getattr(item, "citationStyles", None)
                if reference:
                    try:
                        reference = reference['bibtex'] + "\n url_openAccessPdf"
                    except:
                        reference = None

                text = None
                # concat title and abstract
                if abstract and title:
                    text = title + "\n abstract:" + abstract
                elif not abstract:
                    text = title

                metadata = {
                    "title": title,
                    "authors": authors,
                    "venue": getattr(item, "venue", None),
                    "year": year,
                    "reference": reference,
                    "paperId": paper_id,
                    "citationCount": getattr(item, "citationCount", None),
                    "influentialCitationCount": getattr(item, "influentialCitationCount", None),
                    "url_openAccessPdf": url_openAccessPdf,
                    "href_semanticscholar": url_semanticscholar,
                    "externalIds": getattr(item, "externalIds", None),
                    "fieldsOfStudy": getattr(item, "fieldsOfStudy", None),
                }
                # if full text and open access pdf, try to retrieve full text, otherwise title/abstract text is used
                if full_text and url_openAccessPdf:
                    text_content = self.get_full_text_docs(metadata, base_dir = self.outpath_pdfs)
                    if text_content:
                        text = text_content
                    else:
                        documents_missing.append({'title': title, 'url': url_openAccessPdf})
                else:
                    if url_semanticscholar is None:
                        url_semanticscholar = "No URL available"
                    documents_missing.append({'title': title + ' [No Open Access]', 'url': url_semanticscholar})
     
                documents.append(Document(text=text, extra_info=metadata))

            if self.delete_pdfs:
                shutil.rmtree(self.outpath_pdfs)

            return documents, documents_missing
    
    def get_documents(self, filter_with_llm = True, open_access_only = True):
        """
        Retrieve documents from papers given authors and filter by publication period and topic.

        :param filter_with_llm: bool, if True, filter with LLM
        :param open_access_only: bool, if True, only open access papers are returned
        """
        logging.info("Searching and processing papers...")
        papers, citations = self.get_papers_from_authors()
        if papers:
            logging.info(f"Number of papers found from authors: {len(papers)}")
            logging.info("Extracting content and metadata from papers...")
            documents = self.load_data(papers, full_text = True)
            return documents
        else:
            logging.error("No papers found from authors")    
            return None
    