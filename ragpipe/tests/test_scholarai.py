# test for ScholarAI

from retriever.scholarai import ScholarAI
import os
import logging
logging.basicConfig(level=logging.DEBUG)
logging.debug("test")

if "OPENAI_API_KEY" not in os.environ:
    #os.environ["OPENAI_API_KEY"] = "SET AZURE API KEY HERE"
    print("OPENAI_API_KEY not set, skipping test")
    exit()

def test_scholarai():
    topic = 'Elastin'
    authors = ['Anthony Weiss', 'S. Roberts']
    scholar = ScholarAI(topic, authors, year_start=2010, year_end = 2023)
    papers = scholar.get_papers_from_authors(max_papers = 10)
    assert len(papers) > 0
    documents = scholar.load_data(papers)
    assert len(documents) > 0


