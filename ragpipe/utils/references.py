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