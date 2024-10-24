""" Tool for searching, metadata retrieval and and full-text extraction of bio-medical publications

This tool accesses the Entrez query and database system at the National Center for Biotechnology Information (NCBI).

The Entrez database includes PubMed, PubMed Central, GenBank, GEO, and many other databases.

Note API is limited to 3 requests per second.
API key registration is required for higher usage limits.

Keep in mind that not all articles are allowed downloading of the full text in XML form.

See documentation for biopython: https://biopython.org/docs/dev/index.html
See documentation for Entrez: https://biopython.org/docs/dev/Tutorial/chapter_entrez.html

Author: Sebastian Haan
"""

import os
import time
import logging
import re
import requests
from Bio import Entrez
import xml.etree.ElementTree as ET
from llama_index.core import Document


class biomedAI:
    def __init__(self):
        if 'NCBI_EMAIL' in os.environ:
            Entrez.email = os.environ.get('NCBI_EMAIL')
        else:
            raise ValueError("Please set the NCBI_EMAIL environment variable.")
        
        self.pdf_download_path = os.path.join(os.getcwd(), 'downloaded_pdfs')
        os.makedirs(self.pdf_download_path, exist_ok=True)

    def search_pmc_by_title(self, title):
        """
        Search for articles by title in PubMed Central

        Args:
            title (str): Article title

        Returns:
            pmc_ids: List of PubMed Central IDs for the articles
        """
        handle = Entrez.esearch(db="pmc", term=title, retmax=10)
        record = Entrez.read(handle)
        handle.close()
        return record['IdList']

    def search_pubmed_by_author(self, author_name):
        """
        Search for articles by author in PubMed

        Args:
            author_name (str): Author name

        Returns:
            pubmed_ids: List of PubMed IDs for the articles
        """
        handle = Entrez.esearch(db="pubmed", term=author_name + "[Author]", retmax=10)
        record = Entrez.read(handle)
        handle.close()
        return record['IdList']

    def fetch_article_details(self, pubmed_ids):
        """
        Fetch article details from PubMed

        Args:
            pubmed_ids: List of PubMed IDs for the articles

        Returns:
            articles: XML of the articles
        """
        handle = Entrez.efetch(db="pubmed", id=pubmed_ids, rettype="xml", retmode="text")
        articles = handle.read()
        handle.close()
        return articles

    def fetch_full_text(self, pmc_ids):
        """
        Fetch full-text articles from PubMed Central

        Args:
            pmc_ids: List of PubMed Central IDs for the articles

        Returns:
            articles: Full-text XML of the articles
        """
        handle = Entrez.efetch(db="pmc", id=pmc_ids, rettype="full", retmode="xml")
        articles = handle.read()
        handle.close()
        return articles


    def parse_full_text(self, xml_data):
        """
        Parse the full-text XML and extract article content

        Args:
            xml_data: Full-text XML of the articles

        Returns:
            articles_content: List of full-text content of the articles
        """
        root = ET.fromstring(xml_data)
        articles_content = []
        for article in root.findall(".//body"):
            paragraphs = [p.text for p in article.findall(".//p") if p.text is not None]
            articles_content.append("\n".join(paragraphs))
        if len(articles_content) == 0:
            # Check if no content was found. Some publishers doe not allow XML extractions. In his case extract abstract
            logging.warning("No full-text content found in XML. Extracting abstract instead.")
            abstract_element = root.find('.//abstract')
            articles_content = [" ".join(["".join(p.itertext()) for p in abstract_element.findall('p')])]
        return articles_content
    

    def parse_metadata(self, xml_data):
        """
        Parse the full-text XML and extract article metadata

        Args:
            xml_data: Full-text XML of the articles
    
        Returns:
            articles_metadata: List of metadata of the articles
        """
        root = ET.fromstring(xml_data)
        articles_metadata = []
        for article in root.findall(".//article"):
            metadata = {}
            metadata['title'] = article.findtext(".//article-title")
            metadata['journal'] = article.findtext(".//journal-title")
            metadata['pub_date'] = article.findtext(".//pub-date/year")
        
            authors = []
            for author in article.findall(".//contrib[@contrib-type='author']"):
                name = author.findtext(".//surname") + ", " + author.findtext(".//given-names")
                authors.append(name)
            metadata['authors'] = authors
        
            metadata['abstract'] = article.findtext(".//abstract/p")
            metadata['doi'] = article.findtext(".//article-id[@pub-id-type='doi']")
        
            articles_metadata.append(metadata)
        return articles_metadata
    
    def check_for_pubmed_in_missing_documents(self, missing_results):
        """
        Check PubMedCentral for missing documents and add them to the list of documents.
        update the list of missing documents with the documents that could not be retrieved.  

        Args:
            missing_results: List of missing documents: [{'title': title, 'url': url, 'description': desc}, ...]
        """
        # check if missing_results has key 'url' and 'title'
        if not all('url' in missing_result and 'title' in missing_result for missing_result in missing_results):
            raise ValueError("Missing documents must have 'url' and 'title' keys.")
        # Check if missing_results has key 'description'
        if not all('description' in missing_result for missing_result in missing_results):
            logging.warning("Missing documents do not have 'description' key.")
            missing_results = [{**missing_result, 'description': ''} for missing_result in missing_results]
        missing_results_updated = []
        docs = []
        for missing_result in missing_results:
            url = missing_result['url']
            if "nih.gov/pmc/articles/PMC" in url:
                pmc_id = re.search(r'PMC\d+', url).group()
                try:
                    full_text_xml = self.fetch_full_text(pmc_id)
                    articles_content = self.parse_full_text(full_text_xml)
                except Exception as e:
                    logging.error(f"Failed to download full text from PubMedCentral with exception: {e}. Skipping document...")
                    articles_content = []
                if len(articles_content) > 0:
                    text = articles_content[0]
                    # wait 0.35 seconds to avoid rate limit
                    time.sleep(0.35)
                    metadata = {'href': url, 'title':  missing_result['title'], 'description': missing_result['description']}
                    doc = Document(text=text, doc_id = url, extra_info = metadata)
                    docs.append(doc)
                    logging.info(f"Added document from PubMedCentral with title: {missing_result['title']}")
                else:
                    missing_results_updated.append(missing_result)
            else:
                missing_results_updated.append(missing_result)
        missing_results = missing_results_updated                   
        return docs, missing_results


### Test functions

def test_search_pmc(print_content=False):
    biomedai = biomedAI()
    title = 'The perception of air pollution and its health risk: a scoping review of measures and methods'
    pmc_ids = biomedai.search_pmc_by_title(title)
    assert pmc_ids, "No articles found."
    full_text_xml = biomedai.fetch_full_text(pmc_ids[0])
    articles_content = biomedai.parse_full_text(full_text_xml)
    metadata = biomedai.parse_metadata(full_text_xml)
    assert articles_content, "No content found."
    if print_content:
        for i, content in enumerate(articles_content):
            print(f"Article {i+1} content:\n{content}\n")

def test_search_by_author():
    biomedai = biomedAI()
    author_name = "Anthony Weiss"
    pubmed_ids = biomedai.search_pubmed_by_author(author_name)
    assert pubmed_ids, "No articles found."
    article_details_xml = biomedai.fetch_article_details(pubmed_ids[0])
    assert article_details_xml, "No article details found."
