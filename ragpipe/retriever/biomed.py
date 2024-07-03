# Tool for searching and full-text retrieval of bio-medical publications

from Bio import Entrez
import xml.etree.ElementTree as ET

# Set your email
#Entrez.email = "[your-email@example.com]"

# Search for articles by title in PubMed Central
def search_pmc(title):
    handle = Entrez.esearch(db="pmc", term=title, retmax=10)
    record = Entrez.read(handle)
    handle.close()
    return record['IdList']

# Fetch full-text articles from PubMed Central
def fetch_full_text(pmc_ids):
    handle = Entrez.efetch(db="pmc", id=pmc_ids, rettype="full", retmode="xml")
    articles = handle.read()
    handle.close()
    return articles

# Parse the full-text XML and extract article content
def parse_full_text(xml_data):
    root = ET.fromstring(xml_data)
    articles_content = []
    for article in root.findall(".//body"):
        paragraphs = [p.text for p in article.findall(".//p") if p.text is not None]
        articles_content.append("\n".join(paragraphs))
    return articles_content

def test_search_pmc(print_content=False):
    title = 'The perception of air pollution and its health risk: a scoping review of measures and methods'
    pmc_ids = search_pmc(title)
    assert pmc_ids, "No articles found."
    full_text_xml = fetch_full_text(pmc_ids[0])
    articles_content = parse_full_text(full_text_xml)
    assert articles_content, "No content found."
    if print_content:
        for i, content in enumerate(articles_content):
            print(f"Article {i+1} content:\n{content}\n")

