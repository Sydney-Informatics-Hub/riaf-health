# AI powered publication retrieval

import os
import time
import requests
import logging
from semanticscholar import SemanticScholar
import arxiv
import shutil
from llama_index.llms.openai import OpenAI
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core.llms import ChatMessage
from llama_index.readers.base import BaseReader
from llama_index.readers.schema.base import Document
from PyPDF2 import PdfReader
# local imports
from retriever.pdfdownloader import download_pdf, download_pdf_from_arxiv


LLMSERVICE = 'azure' # 'openai' or 'azure'
AZURE_ENDPOINT = "https://techlab-copilots-aiservices.openai.azure.com/" 
AZURE_API_VERSION = "2023-12-01-preview" 
AZURE_ENGINE = "gpt-35-turbo"

class ScholarAI:
    def __init__(self, 
                 topic, 
                 authors, 
                 year_start = None, 
                 year_end = None, 
                 outpath_pdfs = 'pdfs', 
                 delete_pdfs = False):
        self.topic = topic
        self.authors = authors
        self.year_start = year_start
        self.year_end = year_end
        self.llm = None
        self.outpath_pdfs = outpath_pdfs
        self.delete_pdfs = delete_pdfs

    def init_llm(self):
        if LLMSERVICE == 'openai':
            llm = OpenAI(
                temperature=0,
                model='gpt-3.5-turbo',
                max_tokens=1)
        elif LLMSERVICE == 'azure':
            llm = AzureOpenAI(
                engine=AZURE_ENGINE,
                model='gpt-3.5-turbo',
                temperature=0,
                azure_endpoint=AZURE_ENDPOINT,
                api_key=os.environ["OPENAI_API_KEY"],
                api_version=AZURE_API_VERSION,
            )
        else:
            logging.error(f"LLM service {LLMSERVICE} not supported")
            return None
        return llm
        

    def llmfilter(self, title, abstract):
        """
        LLM (GPT-3.5-turbo) filter to check if paper is related to topic.

        :param title: str, paper title
        :param abstract: str, paper abstract
        :param topic: str, topic to match
        """
        system_prompt = ("You are given a paper summary and a topic. Your task is to determine if the paper is related to the topic."
                        + "If the paper is related to the topic, say 'yes'. Otherwise say 'no'. You must only output 'yes' or 'no'.")
        prompt = (f"Is the following paper related to the topic {self.topic}, please say 'yes'. Otherwise say 'no'."
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
        """
        sch = SemanticScholar()
        paper_list = []
        citations = []
        for author in self.authors:
            results = sch.search_author(author)
            if len(results) > max_authornames:
                results = results[0:max_authornames]
            #author_names = [results[i].name for i in range(min(len(results), max_authors))]
            #author_ids = [results[i].authorId for i in range(min(len(results), max_authors))]
            for result in results:
                papers = result.papers
                papers, citationcounts = self.filter_papers(papers)
                paper_list.extend(papers)
                citations.extend(citationcounts)
        # sort lists by citations (descending) and select top max
        idx_sorted = sorted(range(len(citations)), key=lambda k: citations[k], reverse=True)
        paper_list = [paper_list[i] for i in idx_sorted]
        if max_papers:
            paper_list = paper_list[0:max_papers]
        return paper_list

        
    def filter_papers(self, papers, filter_with_llm = True, open_access_only = True):
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
        for paper in papers:
            if paper.year < self.year_start:
                continue
            if paper.year > self.year_end:
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
        return papers_ok, citationcount

    def get_papers_from_topic(self, 
                              filter_with_llm = True, 
                              min_citation_count = 0, 
                              limit = 100,
                              open_access_only = False):
        """
        Retrieve papers from topic and filter by publication period.
        """
        sch = SemanticScholar()
        papers = sch.search_paper(self.topic, 
                                  publication_date_or_year = f'{self.year_start}:{self.year_end}',
                                  min_citation_count = min_citation_count,
                                  limit = limit,
                                  open_access_pdf = open_access_only)
        papers = papers.items
        if filter_with_llm:
            papers = self.filter_papers(papers)
        return papers 
    

    def get_full_text_docs(self, metadata, base_dir = 'pdfs'):
        url = metadata["url_openAccessPdf"]
        externalIds = metadata["externalIds"]
        paper_id = metadata["paperId"]
        file_path = None
        persist_dir = os.path.join(base_dir, f"{paper_id}.pdf")
        if url and not os.path.exists(persist_dir):
            # Download the document first
            file_path = download_pdf(metadata["paperId"], url, persist_dir)

        if (not url
            and externalIds
            and "ArXiv" in externalIds
            and not os.path.exists(persist_dir)):
            # download the pdf from arxiv
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


    def load_data(self, papers, full_text=True, delete_pdfs = False):
            """
            Loads metadata from Semantic Scholar, retrieve full text and return as list of Document objects.
            Automatically sorts papers by citation count and returns the top max_documents.

            Parameters
            ----------
            papers: list of papers
                The list of papers to retrieve full text from
            full_text: bool
                If True, retrieve full text
            delete_pdfs: bool
                If True, delete pdfs after retrieving full text

            Returns
            -------
            list
                The list of Document object that contains the search results
            """
            documents = []
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
                    text = title + " " + abstract
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
                if full_text and url_openAccessPdf:
                    text_content = self.get_full_text_docs(metadata, base_dir = self.outpath_pdfs)
                    if text_content:
                        text = text_content
                    
                documents.append(Document(text=text, extra_info=metadata))

            if delete_pdfs:
                shutil.rmtree(self.outpath_pdfs)

            return documents
    
    def get_documents(self, filter_with_llm = True, open_access_only = True):
        """
        Retrieve documents from papers given authors and filter by publication period and topic.

        :param filter_with_llm: bool, if True, filter with LLM
        :param open_access_only: bool, if True, only open access papers are returned
        """
        logging.info("Searching and processing papers...")
        papers = self.get_papers_from_authors()
        if papers:
            logging.info(f"Number of papers found from authors: {len(papers)}")
            logging.info("Extracting content and metadata from papers...")
            documents = self.load_data(papers, full_text = True, delete_pdfs = self.delete_pdfs)
            return documents
        else:
            logging.error("No papers found from authors")    
            return None
    