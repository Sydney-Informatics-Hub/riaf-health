from docxtpl import DocxTemplate
import os
from docx import Document
from bs4 import BeautifulSoup
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import Pt, Inches
import pypandoc

def insert_doc_at_placeholder(src_path, dst_path, placeholder_text, remove_title = False):
    """
    replace the placeholder in the destination document with the content of the source document.

    Args:
        src_path (str): Path to the source document.
        dst_path (str): Path to the destination document.
        placeholder_text (str): Placeholder text to be replaced in the destination document.
    """
    # Load the source and destination documents
    src_doc = Document(src_path)
    dst_doc = Document(dst_path)

    # remove the title from the source document
    if remove_title:
        src_doc.paragraphs[0].clear()

    # Find the placeholder in the destination document
    for paragraph in dst_doc.paragraphs:
        if placeholder_text in paragraph.text:
            # Split the paragraph where the placeholder is found
            parts = paragraph.text.split(placeholder_text)
            if len(parts) == 2:
                before_text = parts[0]
                after_text = parts[1]

                # Clear the current paragraph's text
                paragraph.clear()
                
                # Add the text before the placeholder
                paragraph.add_run(before_text)

                # Insert the content from the source document
                for element in src_doc.element.body:
                    new_element = paragraph._element.addnext(element)
                
                # Add the text after the placeholder
                paragraph = paragraph.insert_paragraph_after(after_text)

            break

def markdown_to_docx(input_path):
    """
    Convert a Markdown file to a DOCX file.

    Args:
        input_path (str): Path to the input Markdown file.
    """
    output_path_docx = os.path.splitext(input_path)[0] + ".docx"
    output_path_html = os.path.splitext(input_path)[0] + ".html"

    pypandoc.convert_file(input_path, format='md', to='html', outputfile=output_path_html)
    pypandoc.convert_file(output_path_html, format='html', to='docx', outputfile=output_path_docx)

    # remove the temporary HTML file
    os.remove(output_path_html)



# Function to convert markdown to DOCX format
def markdown_to_docx2(markdown_text):
    html = markdown(markdown_text)
    soup = BeautifulSoup(html, features="html.parser")
    doc = Document()

    for element in soup:
        if element.name == 'h1':
            docdco.add_heading(element.text, level=1)
        elif element.name == 'h2':
            doc.add_heading(element.text, level=2)
        elif element.name == 'h3':
            doc.add_heading(element.text, level=3)
        elif element.name == 'h4':
            doc.add_heading(element.text, level=4)
        elif element.name == 'h5':
            doc.add_heading(element.text, level=5)
        elif element.name == 'h6':
            doc.add_heading(element.text, level=6)
        elif element.name == 'p':
            doc.add_paragraph(element.text)
        elif element.name == 'strong':
            doc.add_paragraph(element.text, style='Bold')
        elif element.name == 'em':
            doc.add_paragraph(element.text, style='Italic')
        elif element.name == 'ul':
            for li in element.find_all('li'):
                doc.add_paragraph(li.text, style='ListBullet')
        elif element.name == 'ol':
            for li in element.find_all('li'):
                doc.add_paragraph(li.text, style='ListNumber')

    return doc

def clone_formatting(source, target):
    """ Clone formatting from source paragraph to target paragraph, including font styles and paragraph spacing. """
    target.style = source.style
    target.alignment = source.alignment
    target.paragraph_format.left_indent = source.paragraph_format.left_indent
    target.paragraph_format.right_indent = source.paragraph_format.right_indent
    target.paragraph_format.first_line_indent = source.paragraph_format.first_line_indent
    target.paragraph_format.space_before = source.paragraph_format.space_before
    target.paragraph_format.space_after = source.paragraph_format.space_after
    target.paragraph_format.line_spacing = source.paragraph_format.line_spacing
    target.paragraph_format.keep_together = source.paragraph_format.keep_together
    target.paragraph_format.keep_with_next = source.paragraph_format.keep_with_next
    target.paragraph_format.page_break_before = source.paragraph_format.page_break_before
    target.paragraph_format.widow_control = source.paragraph_format.widow_control

def clone_paragraph(p, cell):
    """Clone a paragraph into a specified table cell with full formatting, including lists."""
    target_p = cell.add_paragraph(style = p.style)
    clone_formatting(p, target_p)
    for run in p.runs:
        target_run = target_p.add_run(run.text)
        # Copy run formatting
        target_run.bold = run.bold
        target_run.italic = run.italic
        target_run.underline = run.underline
        target_run.font.size = run.font.size
        target_run.font.color.rgb = run.font.color.rgb
        target_run.font.name = run.font.name
        target_run.style = run.style

def ensure_styles(source_doc, target_doc):
    for style in source_doc.styles:
        if style.name not in [s.name for s in target_doc.styles]:
            # If the style doesn't exist, create a new one based on a built-in style if possible
            new_style = target_doc.styles.add_style(style.name, style.type)
            if style.type == WD_STYLE_TYPE.PARAGRAPH:
                new_style.base_style = target_doc.styles['Normal']  # Base new styles on 'Normal'
            # Copy style attributes as needed
            new_style.font.name = style.font.name
            new_style.font.size = style.font.size
            # Add other attributes as needed

def insert_content_into_cell(source_docx, target_docx, table_index, row_index, col_index):
    """Insert content from a source DOCX into a specific cell of a target DOCX table."""
    source_doc = Document(source_docx)
    target_doc = Document(target_docx)
    ensure_styles(source_doc, target_doc)

    # Identify the target cell
    cell = target_doc.tables[table_index].rows[row_index].cells[col_index]

    # Clear existing cell content
    cell.text = ""
    cell.paragraphs[0].clear()

    for para in source_doc.paragraphs:
        clone_paragraph(para, cell)

    target_doc.save('updated_target.docx')

# Usage
source_docx = '/mnt/data/markdown_text.docx'  # Path to the source DOCX file
target_docx = 'target_template.docx'  # Path to the target DOCX template
insert_content_into_cell(source_docx, target_docx, table_index=0, row_index=1, col_index=1)

def insert_content_into_placeholder(target_doc_path, source_doc_path, placeholder):
    target_doc = docx.Document(target_doc_path)
    source_doc = docx.Document(source_doc_path)

    # Search for the placeholder in target document tables
    for table in target_doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if placeholder in cell.text:
                    # Clear existing cell content
                    cell.text = ''
                    # Insert content from source document
                    for para in source_doc.paragraphs:
                        copy_paragraph_to_cell(para, cell)

# Convert list answers to DOCX format
def convert_answers_to_docx(answers):
    docs = []
    for answer in answers:
        doc = markdown_to_docx(answer)
        #docs.append(doc)
        docx_content = "\n".join([p.text for p in doc.paragraphs])
        docs.append(docx_content)
    return docs

def replace_html_and_convert_to_docx(html_template_path, replacements, output_docx_path, title):
    """
    Reads an HTML file, replaces placeholders with HTML content, and saves as a docx file with a specified title.
    
    Args:
        html_template_path (str): Path to the HTML template file.
        replacements (dict): Dictionary of placeholders and their corresponding HTML replacements.
        output_docx_path (str): Path where the output docx file should be saved.
        title (str): Title for the generated DOCX file.
    """
    # Read the HTML template file
    with open(html_template_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Replace placeholders in the HTML content
    for placeholder, replacement_html in replacements.items():
        # Using regular expressions to replace placeholders that include HTML content safely
        pattern = re.escape(placeholder)  # Escape to handle special characters in the placeholder
        html_content = re.sub(pattern, replacement_html, html_content)
    
    # Convert the modified HTML to a docx file
    docx_bytes_io = html2docx(html_content, title)
    
    # Save the docx file
    with open(output_docx_path, 'wb') as f:
        f.write(docx_bytes_io.getvalue())  # getvalue() extracts bytes from BytesIO object

def replace_in_html_and_convert_to_docx(docx_template_path, replacements, output_docx_path):
    """
    Convert DOCX to HTML, replace placeholders in HTML, and convert back to DOCX.
    
    Args:
        docx_template_path (str): Path to the DOCX template file.
        replacements (dict): Dictionary of placeholders and their corresponding HTML replacements.
        output_docx_path (str): Path where the output DOCX file should be saved.
    """
    # Convert DOCX to HTML
    with open(docx_template_path, "rb") as docx_file:
        result = mammoth.convert_to_html(docx_file)
        html_content = result.value  # The generated HTML

    # Replace placeholders in the HTML content
    for placeholder, replacement_html in replacements.items():
        pattern = re.escape(placeholder)  # Ensure the placeholder is treated as a literal string in regex
        html_content = re.sub(pattern, replacement_html, html_content)

    # Save the modified HTML to an HTML file
    with open(html_output_path, 'w', encoding='utf-8') as html_file:
        html_file.write(html_content)
        print(f"HTML file saved to {html_output_path}")

    # Convert the modified HTML back to DOCX
    pypandoc.convert_text(html_content, 'docx', format='html', outputfile=docx_output_path)
    print(f"DOCX file created at {docx_output_path}")

# Example usage
replacements = {
    '{{ q1 }}': '<p>This is an answer to question 1.</p>',
    '{{ q2 }}': '<p>This is an answer to question 2.</p>',
    '{{ q3 }}': '<ul><li>Item 1 for Q3</li><li>Item 2 for Q3</li></ul>',
    '{{ q4 }}': '<p>This is an answer to question 4 with <strong>bold</strong> text.</p>'
}
replace_in_html_and_convert_to_docx('path_to_docx_template.docx', replacements, 'output_document.docx')

# Assuming the following attributes exist within your class or context
self.organisation = "Organization Name"
self.research_topic = "Research Topic"
self.research_period = "Research Period"
self.author = "Author Name"
self.impact_period = "Impact Period"
self.list_answers = [
    "### Answer to question 1 in markdown format",
    "**Answer to question 2 in markdown format**",
    "Answer to question 3 in markdown format",
    "*Answer to question 4 in markdown format*"
]
sources_text = "References text"

# Convert list answers to DOCX content
converted_answers = convert_answers_to_docx(self.list_answers)

# Create DOCX template and render content
doc = DocxTemplate("./templates/RIAF_template.docx")
docx_content = { 
    "ORG_NAME": self.organisation, 
    "TITLE_NAME": self.research_topic,
    "RESEARCH_PERIOD": self.research_period,
    "AUTHOR": self.author,
    "IMPACT_PERIOD": self.impact_period,
    "RESEARCH_TOPIC": self.research_topic,
    "q1": converted_answers[0],
    "q2": converted_answers[1],
    "q3": converted_answers[2],
    "q4": converted_answers[3],
    "refs": sources_text
}
doc.render(docx_content)
doc.save(os.path.join(self.outpath, "Use_Case_Study.docx"))

docx_content = { 
    "ORG_NAME": organisation, 
    "TITLE_NAME": research_topic,
    "RESEARCH_PERIOD": research_period,
    "AUTHOR": author,
    "IMPACT_PERIOD": impact_period,
    "RESEARCH_TOPIC": research_topic,
    "q1": docs[0],
    "q2": docs[1],
    "q3": docs[2],
    "q4": docs[3],
    "refs": sources_text
}