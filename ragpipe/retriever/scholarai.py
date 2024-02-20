# AI powered publication retrieval

import os
import time
import requests
import logging
from semanticscholar import SemanticScholar
from llama_index.llms.openai import OpenAI
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core.llms import ChatMessage

LLMSERVICE = 'azure' # 'openai' or 'azure'
AZURE_ENDPOINT = "https://techlab-copilots-aiservices.openai.azure.com/" 
AZURE_API_VERSION = "2023-12-01-preview" 
AZURE_ENGINE = "gpt-35-turbo"

class ScholarAI:
    def __init__(self, topic, authors, year_start = None, year_end = None):
        self.topic = topic
        self.authors = authors
        self.year_start = year_start
        self.year_end = year_end
        self.llm = None

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
        
    def get_papers_from_authors(self, max_authornames = 3):
        """
        Retrieve papers from authors and filter by topic and publication period.

        :param max_authors: int, maximum number of top author names to consider that are retrieved from Semantic Scholar
        """
        sch = SemanticScholar()
        authors_ids = []
        paper_list = []
        for author in self.authors:
            results = sch.search_author(author)
            if len(results) > max_authornames:
                results = results[0:max_authornames]
            #author_names = [results[i].name for i in range(min(len(results), max_authors))]
            #author_ids = [results[i].authorId for i in range(min(len(results), max_authors))]
            for result in results:
                papers = result.papers
                papers = self.filter_papers(papers)
                paper_list.extend(papers)
        return paper_list

        
    def filter_papers(self, papers, filter_with_llm = True):
        """
        process papers and filter by topic and year.

        :param papers: list of papers
        :param topic: str, topic to filter
        :param year_start: int, start year of publication
        :param year_end: int, end year of publication
        :param filter_with_llm: bool, if True, filter with LLM

        :return: list of papers
        """
        papers_ok = []
        citationcount = []
        paperIds = []
        ok = True
        for paper in papers:
            if paper.year < self.year_start:
                continue
            if paper.year > self.year_end:
                continue
            # get title
            title = paper.title
            # get abstract
            abstract = paper.abstract
            # get year
            if filter_with_llm:
                ok = self.llmfilter(title, abstract)
            if ok:
                papers_ok.append(paper)
                citationcount.append(paper.citation_count)
                paperIds.append(paper.paperId)
        return papers_ok   

