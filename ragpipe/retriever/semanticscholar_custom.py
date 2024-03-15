# Functions for searching publications with SemantiScholar API
# for more info about API see https://api.semanticscholar.org/api-docs/#tag/Paper-Data/operation/post_graph_get_papers
# rewrite using the package https://github.com/danielnsilva/semanticscholar

"""
metadata example:
{'title': 'Tropoelastin and Elastin Assembly',
 'venue': 'Frontiers in Bioengineering and Biotechnology',
 'year': 2021,
 'paperId': 'c450bf38350269cd8be8bbdcd39ccf598da403bf',
 'citationCount': 58,
 'openAccessPdf': 'https://www.frontiersin.org/articles/10.3389/fbioe.2021.643110/pdf',
 'authors': ['J. Ozsvar',
  'Chengeng Yang',
  'S. Cain',
  'C. Baldock',
  'A. Tarakanova',
  'A. Weiss'],
 'externalIds': {'PubMedCentral': '7947355',
  'DOI': '10.3389/fbioe.2021.643110',
  'CorpusId': 232041511,
  'PubMed': '33718344'}}
"""
import os
import requests
import logging
#from llama_hub.semanticscholar import SemanticScholarReader
from semanticscholar import SemanticScholar
from openai import OpenAI


def openai_init(path_openai_key =  '../../openai_sih_key.txt'):
    # Authenticate and read file from file
    #check if "OPENAI_API_KEY" parameter in os.environ:
    if "OPENAI_API_KEY" not in os.environ:
        if path_openai_key is None:
            logging.error("OPENAI_API_KEY not found in os.environ and path_openai_key is None")
        else:
            with open(path_openai_key , "r") as f:
                os.environ["OPENAI_API_KEY"] = f.read()


def get_papers_from_authors(authors, topic, year_start = None, year_end = None, max_authornames = 3):
    """
    Retrieve papers from authors and filter by topic and publication period.

    :param authors: list of str, author names
    :param topic: str, topic to filter
    :param year_start: int, start year of publication
    :param year_end: int, end year of publication
    :param max_authors: int, maximum number of top author names to consider that are retrieved from Semantic Scholar
    """
    sch = SemanticScholar()
    authors_ids = []
    paper_list = []
    for author in authors:
        results = sch.search_author(author)
        if len(results) > max_authornames:
            results = results[0:max_authornames]
        #author_names = [results[i].name for i in range(min(len(results), max_authors))]
        #author_ids = [results[i].authorId for i in range(min(len(results), max_authors))]
        for result in results:
            papers = result.papers
            papers = filter_papers(papers, topic, year_start, year_end)
            paper_list.extend(papers)
    return paper_list

    
def filter_papers(papers, topic, year_start= None, year_end = None, filter_with_llm = False):
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
        if paper.year < year_start:
            continue
        if paper.year > year_end:
            continue
        # get title
        title = paper.title
        # get abstract
        abstract = paper.abstract
        # get year
        if filter_with_llm:
            ok = llmfilter(title, abstract, topic)
        if ok:
            papers_ok.append(paper)
            citationcount.append(paper.citation_count)
            paperIds.append(paper.paperId)
    return papers_ok


# compare two lists and find identifiers of papers that are in both lists
def compare_papers(papers1, papers2):
    """
    compare two lists of papers and find papers that are in both lists
    """
    paperIds1 = [paper.paperId for paper in papers1]
    paperIds2 = [paper.paperId for paper in papers2]
    common_papers = list(set(paperIds1) & set(paperIds2))
    # same for topics
    topics1 = [paper.title for paper in papers1]
    topics2 = [paper.title for paper in papers2]
    common_topics = list(set(topics1) & set(topics2))
    return common_papers


def llmfilter(title, abstract, topic):
    """
    LLM (GPT-3.5-turbo) filter to check if paper is related to topic.

    :param title: str, paper title
    :param abstract: str, paper abstract
    :param topic: str, topic to match
    """
    model = 'gpt-3.5-turbo'
    system_prompt = ("You are given a paper summary and a topic. Your task is to determine if the paper is related to the topic."
                    + "If the paper is related to the topic, say 'yes'. Otherwise say 'no'. You must only output 'yes' or 'no'.")
    prompt = (f"Is the following paper related to the topic {topic}, please say 'yes'. Otherwise say 'no'."
            + f"\n\nPaper title: {title}\nabstract: {abstract}\n\n")

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        max_tokens = 1,
        temperature = 0.0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    result = response.choices[0].message.content.strip().lower()
    if result == 'yes':
        return True
    elif result == 'no':
        return False
    else:
        logging.error(f"LLM response not understood: {result}")
        return None



def read_semanticscholar(query_space, author, keywords, limit =20, full_text = False, year_start = None, year_end = None):
    """
    Search and read scholar online documents using Semantic Scholar API

    :param query_space: str, query space to search. This is the name of the area of research
    :param author: str, author name
    :param keywords: list of str, keywords to search for (only used if query_space and author return no results)
    :param limit: int, number of documents to return
    :param fulltext: bool, if True, full text is returned
    :param year_start: int, start year of publication
    :param year_end: int, end year of publication

    :return: documents
    """
    # use last name of author for search
    author = author.split(' ')[-1]
    s2reader = SemanticScholarReader(timeout=30)
    #query = f"ti:{query_space} AND au:{author}"
    query = query = f"{query_space}, {author}"
    docstore = s2reader.load_data(query=query_space, limit=limit, full_text=full_text)
    if len(docstore) > 0:
        logging.info(f"Number of SemanticScholar documents found: {len(docstore)}")
        return docstore
    
    # run query with keywords
    docstore = []
    keywords = keywords.split(',')
    for keyword in keywords:
        query = f"{keyword}, {author}"
        docs = s2reader.load_data(query=query, limit=limit, full_text=full_text)
        docstore.extend(docs)
    if len(docstore) > 0:
        # remove duplicates
        docstore_new = []
        unique_paper_ids = []
        for doc in docstore:
            paper_id = doc.metadata['paperId']
            if 'year' in doc.metadata:
                year = doc.metadata['year']
                if 'year_start' is not None:
                    if year < year_start:
                        continue                
                if 'year_end' is not None:
                    if year > year_end:
                        continue   
            if paper_id not in unique_paper_ids:
                docstore_new.append(doc)
                unique_paper_ids.append(paper_id)
        logging.info(f"Number of SemanticScholar documents found: {len(docstore)}")
        return docstore_new
    else:
        logging.info(f"No SemanticScholar documents found for topic nor any keyword")
        return None


import requests

def get_metadata_from_semanticscholar(paper_id):
    """
    Get metadata for a paper from Semantic Scholar API

    :param paper_id: str, paper ID
    :return: metadata
    """
    url = f"https://api.semanticscholar.org/v1/paper/{paper_id}"
    response = requests.get(url)
    if response.status_code == 200:
        metadata = response.json()
        return metadata
    else:
        logging.error(f"Error fetching metadata from Semantic Scholar for paper ID {paper_id}")
        return None
    
def keyword_search_semanticscholar(query_topic, 
                                  query_author, 
                                  query_keywords, 
                                  limit = 20, 
                                  full_text = False, 
                                  year_start = None, 
                                  year_end = None,
                                  api_key = None):
    """
    query: Keyword to search


    see https://www.semanticscholar.org/product/api/tutorial
    also check https://api.semanticscholar.org/api-docs/#tag/Paper-Data/operation/get_graph_paper_relevance_search
    """
    url = 'https://api.semanticscholar.org/graph/v1/paper/search'

    # More specific query parameter
    query_params = {'query': query_topic
                    'limit': limit,
                    'year': year_start}

    # Define headers with API key
    headers = {'x-api-key': api_key}

    # Send the API request
    response = requests.get(url, params=query_params, headers=headers)

    # Check response status
    if response.status_code == 200:
        response_data = response.json()
        # Process and print the response data as needed
        return response_data
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")


"""
keys = metadata.keys()
Out[39]: dict_keys(['abstract', 'arxivId', 'authors', 'citationVelocity', 'citations', 'corpusId', 'doi', 
'fieldsOfStudy', 'influentialCitationCount', 'isOpenAccess', 'isPublisherLicensed', 'is_open_access', 'is_publisher_licensed', 
'numCitedBy', 'numCiting', 'paperId', 'references', 's2FieldsOfStudy', 'title', 'topics', 'url', 'venue', 'year'])

Citation Velocity is a weighted average of the publication’s citations for the last 3 years and fewer for publications published in the last year or two, 
which indicates how popular and lasting the publication is.

items = metadata.items()

--> extract fieldsOfStudy, influentialCitationCount, numCitedBy, title, url, year, venue, doi, isOpenAccess, citationVelocity
venue: journal name
url: semanticscholar url

citations = metadata['citations']

need affiliations of authors (not available in semantischolar metadata)

authors = metadata['authors']

doi = metadata['doi']

"""


def author_search_semanticscholar(query_author, 
                                  limit = 20, 
                                  full_text = False, 
                                  year_start = None, 
                                  year_end = None,
                                  api_key = None):
    
    """
    query: Keyword to search


    see https://www.semanticscholar.org/product/api/tutorial
    also check https://api.semanticscholar.org/api-docs/#tag/Paper-Data/operation/get_graph_paper_relevance_search
    """
    # Define the API endpoint URL
    url = "https://api.semanticscholar.org/graph/v1/author/search"

    # Define the required query parameters
    query_params = {
        "query": author,
        "fields": "paperCount,papers.title,papers.fieldsOfStudy"
    }

    # Make the GET request
    response = requests.get(url, params=query_params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse and work with the response data in JSON format
        data = response.json()

        # code to process the data goes here
        return data

    else:
        # Handle the error, e.g., print an error message
        print(f"Request failed with status code {response.status_code}")


"""
Example output for author search:

{'total': 2,
 'offset': 0,
 'data': [{'authorId': '32325565',
   'paperCount': 9,
   'papers': [{'paperId': '8b74d34eae68da35ba5ca2f682d5ebced7454c92',
     'title': 'Fuzzy binding model of molecular interactions between tropoelastin and integrin alphaVbeta3.',
     'fieldsOfStudy': ['Medicine']},
    {'paperId': 'c450bf38350269cd8be8bbdcd39ccf598da403bf',
     'title': 'Tropoelastin and Elastin Assembly',
     'fieldsOfStudy': ['Medicine']},
    {'paperId': '17020109d6fb891be60f7c82f9679bfc7c5dda20',
     'title': 'Allysine modifications perturb tropoelastin structure and mobility on a local and global scale',
     'fieldsOfStudy': ['Medicine', 'Chemistry']},
    {'paperId': '4c8b486c2efa38c3b5fdfe0f791ec37533839e21',
     'title': 'Freestanding hierarchical vascular structures engineered from ice.',
     'fieldsOfStudy': ['Medicine', 'Materials Science']},
    {'paperId': '60f34f2eabb562ac8b97b72796d74fe31a478f9d',
     'title': 'Hierarchical assembly of elastin materials',
     'fieldsOfStudy': ['Chemistry']},
    {'paperId': 'f7243202d230fc1e58f0c0af0b566744fac76780',
     'title': 'Coarse-grained model of tropoelastin self-assembly into nascent fibrils',
     'fieldsOfStudy': ['Materials Science', 'Medicine']},
    {'paperId': '930cce8b6ac8d1db4e0724b0a4850c7f1790750c',
     'title': 'Synthetic-Elastin Systems',
     'fieldsOfStudy': ['Chemistry']},
    {'paperId': '1cc5a995677b7753268f41d75f48016df2c20b98',
     'title': 'Elastin-based biomaterials and mesenchymal stem cells.',
     'fieldsOfStudy': ['Chemistry', 'Medicine']},
    {'paperId': '5fcf00877767065e9b5772261962a736bf46ff22',
     'title': 'SmoXYB1C1Z of Mycobacterium sp. Strain NBB4: a Soluble Methane Monooxygenase (sMMO)-Like Enzyme, Active on C2 to C4 Alkanes and Alkenes',
     'fieldsOfStudy': ['Medicine', 'Chemistry']}]},
  {'authorId': '49364945',
   'paperCount': 2,
   'papers': [{'paperId': '4b3754bedf3bd740a94759eb62a9d2b29de3c844',
     'title': 'Exposures during pregnancy and at birth are associated with the risk of offspring eating disorders.',
     'fieldsOfStudy': ['Medicine']},
    {'paperId': 'b3b35b31f7c1b12bacbee9ce05aa5184533b4dba',
     'title': '[Trachoma screening in Szeged district].',
     'fieldsOfStudy': ['Medicine']}]}]}
"""

"""
Strategy for search:
- first author search
- then use LLM or keyword search to identify which author Id is most likely the one we are looking for
- then filter papers by year and topic

- then query all papers (not author restricted) in topic
- calculate how relevant author is to topic by ...?


for citation map:
need to read papers and extract affiliations of authors during this time-period
https://academia.stackexchange.com/questions/151825/given-a-doi-how-can-i-programmatically-obtain-all-the-author-affiliations

DataCite?
https://support.datacite.org/docs/api-get-doi
"""

def get_datacite_metadata(doi, api_key = None):
    """
    Get metadata for a paper from DataCite API

    https://api.test.datacite.org/dois/{id}

    :param doi: str, paper DOI
    :param api_key: str, DataCite API key
    :return: metadata
    """
    url = f"https://api.datacite.org/dois/{doi}"
    headers = {
        "accept": "application/vnd.api+json",
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        metadata = response.json()
        return metadata
    else:
        logging.error(f"Error fetching metadata from DataCite for DOI {doi}")
        return None
    

def find_publications(api_key, authors, topic):
    #headers = {"x-api-key": api_key}
    # problem: same publicatiions under different authors ids, need to use first author that matches topic
    publications = {}
    
    for author in authors:
        # Search for the author by name
        author_search_url = f"https://api.semanticscholar.org/graph/v1/author/search?query={author}&fields=id,name"
        #author_response = requests.get(author_search_url, headers=headers).json()
        try:
            author_response = requests.get(author_search_url).json()
        except:
            logging.error(f"Error getting author data for {author}")
            continue
        
        # get fisrst 5 pubcs for each author
        for author_candidate in author_response['data'][0:5]:
            # For each author, check their publications for the given topic
            author_id = author_candidate['authorId']
            author_name = author_candidate['name']
            publications_search_url = f"https://api.semanticscholar.org/graph/v1/author/{author_id}/papers?fields=title,abstract,year&limit=100"
            #publications_response = requests.get(publications_search_url, headers=headers).json()
            publications_response = requests.get(publications_search_url).json()
            
            # Filter publications by topic in the title or abstract
            #author_publications = [paper for paper in publications_response['data'] if topic.lower() in (paper['title'].lower() + paper['abstract'].lower())]
            # replace with LLM filter
            author_publications = [paper for paper in publications_response['data']]

            if author_publications:
                publications[author] = author_publications
                break  # Assuming the first matching author is the correct one
            #publications[author_name] = author_publications
    
    return publications