# Process scripts for cleaning and converting publication sources

def publications_to_markdown(publications):
    markdown_list = []

    for pub_id, pub_details in publications.items():
        title = pub_details.get('title', 'No Title')
        authors = ', '.join(pub_details.get('authors', []))
        venue = pub_details.get('venue', 'No Venue')
        year = pub_details.get('year', 'No Year')
        doi = pub_details.get('externalIds', {}).get('DOI', 'No DOI')
        link = pub_details.get('openAccessPdf', '')

        # Constructing the markdown string for each publication
        markdown_entry = f"* {authors}. \"{title}.\" {venue} ({year}). "
        markdown_entry += f"DOI: [{doi}](https://doi.org/{doi})" if doi != 'No DOI' else "DOI: No DOI"
        markdown_entry += f". [Access Publication]({link})" if link else ""

        markdown_list.append(markdown_entry)

    return '\n\n'.join(markdown_list)

def clean_publications(list_sources):
    """
    Flatten list of dictionaries of publication sources and remove duplicates

    :param sources: list of dictionaries

    :return: cleaned sources
    """
    flattened_dict = {k: v for d in list_sources for k, v in d.items()}

    # Remove duplicates based on 'paperId'
    unique_papers = {}
    for key, value in flattened_dict.items():
        paper_id = value['paperId']
        if paper_id not in unique_papers:
            unique_papers[paper_id] = value

    # Convert back to list of dictionaries
    #result = [{k: v} for k, v in unique_papers.items()]
    return unique_papers