# Tool for searching, metadata retrieval and and full-text exatraction of bio-medical publications

from Bio import Entrez
import xml.etree.ElementTree as ET

# Set your email
#Entrez.email = "[your-email@example.com]"

# Search for articles by title in PubMed Central
def search_pmc(title):
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

# Fetch full-text articles from PubMed Central
def fetch_full_text(pmc_ids):
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


def parse_full_text(xml_data):
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
    return articles_content


def parse_metadata(xml_data):
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

def test_search_pmc(print_content=False):
    title = 'The perception of air pollution and its health risk: a scoping review of measures and methods'
    pmc_ids = search_pmc(title)
    assert pmc_ids, "No articles found."
    full_text_xml = fetch_full_text(pmc_ids[0])
    articles_content = parse_full_text(full_text_xml)
    metadata = parse_metadata(full_text_xml)
    assert articles_content, "No content found."
    if print_content:
        for i, content in enumerate(articles_content):
            print(f"Article {i+1} content:\n{content}\n")