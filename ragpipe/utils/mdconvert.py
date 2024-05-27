
# Convert Markdown to PDF using mdpdf


import os,sys
import subprocess
# import markdown
from docxtpl import DocxTemplate 
from docx import Document
from markdown import markdown
from bs4 import BeautifulSoup

def markdown_to_pdf(markdown_file_path):
    """
    Convert Markdown to PDF

    Parameters
    ----------
    markdown_file_path : str
        The path to the Markdown file
    """
    # Check if the file exists
    if not os.path.exists(markdown_file_path):
        raise FileNotFoundError(f"The file {markdown_file_path} does not exist")

    # Generate the PDF file path
    base_name = os.path.splitext(markdown_file_path)[0]
    pdf_file_path = base_name + '.pdf'

    # Convert MD to PDF and save it
    cmd = f"mdpdf -o {pdf_file_path} {markdown_file_path}"
    subprocess.run(cmd, shell=True, check=True)


def markdown_to_html(markdown_file_path):
    """
    Convert Markdown to HTML

    Parameters
    ----------
    markdown_file_path : str
        The path to the Markdown file
    """
    # Check if the file exists
    if not os.path.exists(markdown_file_path):
        raise FileNotFoundError(f"The file {markdown_file_path} does not exist")

    # Generate the PDF file path
    base_name = os.path.splitext(markdown_file_path)[0]
    html_file_path = base_name + '.html'

    # Convert MD to PDF and save it
    markdown.markdownFromFile(
        input=markdown_file_path,
        output=html_file_path,
        encoding='utf8',
        )
    

def report_to_docx(markdown_file_path,ORG_NAME,TITLE_NAME,RESEARCH_PERIOD, AUTHOR, IMPACT_PERIOD, RESEARCH_TOPIC, q1, q2, q3, q4, refs):
    """
    Convert Markdown to HTML

    Parameters
    ----------
    markdown_file_path : str
        The path to the Markdown file
    """
    # Check if the file exists
    if not os.path.exists(markdown_file_path):
        raise FileNotFoundError(f"The file {markdown_file_path} does not exist")
    
    # convert questions to docx
    converted_answers = convert_answers_to_docx([q1, q2, q3, q4])

    # Generate the PDF file path
    base_name = os.path.splitext(markdown_file_path)[0]
    docx_file_path = base_name + '.docx'

    # Convert MD to PDF and save it
    doc = DocxTemplate("./templates/RIAF_template.docx")
    docx_content = { 
                "ORG_NAME":ORG_NAME, 
                "TITLE_NAME": TITLE_NAME,
                "RESEARCH_PERIOD":RESEARCH_PERIOD,
                "AUTHOR":AUTHOR,
                "IMPACT_PERIOD":IMPACT_PERIOD,
                "RESEARCH_TOPIC":RESEARCH_TOPIC,
                "q1":converted_answers[0],
                "q2":converted_answers[1],
                "q3":converted_answers[2],
                "q4":converted_answers[4],
                "refs":refs
                }
    doc.render(docx_content)
    doc.save(docx_file_path)


def markdown_to_docx(markdown_text):
    html = markdown(markdown_text)
    soup = BeautifulSoup(html, features="html.parser")
    doc = Document()

    for element in soup:
        if element.name == 'h1':
            doc.add_heading(element.text, level=1)
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

# Convert list answers to DOCX format
def convert_answers_to_docx(answers):
    docs = []
    for answer in answers:
        doc = markdown_to_docx(answer)
        docx_content = "\n".join([p.text for p in doc.paragraphs])
        docs.append(docx_content)
    return docs
    

if __name__ == '__main__':  
    if 'markdown_to_docx' in sys.argv:  
        markdown_to_docx(sys.argv[2], 
                         "an org", 
                         "a good title", 
                         "2010", 
                         "butters", 
                         "2020",
                         "how to make bread",
                         "this is the answer", 
                         "it is a good one",
                         "We should know about it",
                         "is this your final answer",
                         "This is a reference")  


def markdown_to_question(markdown_file_path, start_text, end_text):
    """
    Grabs specific questions from the output Markdown

    Parameters
    ----------
    markdown_file_path : str
        The path to the Markdown file

    # Example usage:
    start_text = "## What is the problem this research seeks to address and why is it significant? (Max 250 words)"
    end_text = "**References**"
    question_text = markdown_to_question(start_text, end_text)
    print(question_text)
    """
    # Check if the file exists
    if not os.path.exists(markdown_file_path):
        raise FileNotFoundError(f"The file {markdown_file_path} does not exist")

    question_text = ""
    capture = False

    try:
        with open(markdown_file_path, "r", encoding="utf-8") as file:
            for line in file:
                # Check if the line contains the start text and begin capture
                if start_text in line:
                    capture = True
                    continue  # Skip the line with the start text

                # Check if the line contains the end text and stop capture
                if end_text in line and capture:
                    break

                # Capture the text if between start_text and end_text
                if capture:
                    question_text += line

    except FileNotFoundError:
        print("The file 'output.md' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return question_text.strip()  # Remove any leading/trailing whitespace
