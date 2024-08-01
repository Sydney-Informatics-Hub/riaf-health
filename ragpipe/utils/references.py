import re

def clean_references(markdown_text):

    # Split the text into two parts: content and references
    parts = markdown_text.split('**References**')
    content = parts[0]
    references_section = parts[1] if len(parts) > 1 else ''

    # Extract references from the reference section
    references = re.findall(r'(\d+)\. \[(.*?)\]\((.*?)\)', references_section)

    # Remove duplicates and keep the first occurrence
    seen = {}
    cleaned_references = []
    for num, title, link in references:
        if link not in seen:
            seen[link] = len(seen) + 1
            cleaned_references.append((seen[link], title, link))

    # Replace the old reference numbers in the content with new numbers
    for old_num, title, link in references:
        if link in seen:
            new_num = seen[link]
            content = re.sub(f'\[{old_num}\]', f'[{new_num}]', content)

    # Construct the new references section
    new_references_section = '**References**\n\n'
    for num, title, link in cleaned_references:
        new_references_section += f'{num}. [{title}]({link})\n'

    # Return the cleaned-up markdown text
    return content + new_references_section

def test_clean_references():
    markdown_text = """
### Problem Statement

The research conducted by Professor Anthony Weiss at the University of Sydney addresses the critical need for effective skin and tissue repair solutions, particularly for conditions such as acne scars, stretch marks, and surgical wounds [1]. These conditions not only affect millions of individuals globally but also impose significant health and socioeconomic burdens [2]. Chronic skin conditions and non-healing wounds can lead to prolonged recovery times, increased healthcare costs, and reduced quality of life for patients [3]. 

Existing treatments often fall short in terms of efficacy and biocompatibility, necessitating the development of more advanced solutions. Elastagen's technology, based on recombinant human tropoelastin, offers a novel approach by utilizing a protein identical to natural elastin, thereby enhancing biocompatibility and effectiveness [4]. This innovation builds on decades of research and has demonstrated promising results in clinical trials, showing potential to accelerate healing, reduce scarring, and improve skin elasticity [5].

The significance of this problem is underscored by the high morbidity associated with chronic skin conditions and the potential for severe complications, including infections, which can lead to increased mortality [6]. Economically, the global market for wound healing products is substantial, with billions spent annually on treatments and lost productivity [7]. By providing more effective and faster-acting treatments, Elastagen's technology could lead to significant cost savings and improved patient outcomes, thereby addressing a critical gap in current medical practice [8].

**References**

1. [BioSpectrum Asia](https://www.biospectrumasia.com/news/26/10304/allergan-to-acquire-australian-biotech-startup-elastagen.html)
2. [Australian Financial Review](https://www.afr.com/companies/healthcare-and-fitness/university-of-sydney-spinoff-elastagen-sold-for-120m-to-botox-maker-20180208-h0vrkf)
3. [Sydney University News](https://www.sydney.edu.au/news-opinion/news/2018/02/09/allergan-to-acquire-university-of-sydney-spinoff-elastagen.html)
4. [Micro.org.au](https://micro.org.au/innovation/fast-tracking-elastin-to-market/)
5. [BioPharma Dive](https://www.biopharmadive.com/news/allergan-picks-up-australian-biotech-elastagen-in-95m-deal/516838/)
6. [BioSpectrum Asia](https://www.biospectrumasia.com/news/26/10304/allergan-to-acquire-australian-biotech-startup-elastagen.html)
7. [Grand View Research](https://www.grandviewresearch.com/industry-analysis/wound-care-market)
8. [Sydney University News](https://www.sydney.edu.au/news-opinion/news/2018/02/09/allergan-to-acquire-university-of-sydney-spinoff-elastagen.html)
"""
    cleaned_markdown = clean_references(markdown_text)
    print(cleaned_markdown)
