
# Convert Markdown to PDF using mdpdf


import os,sys
import subprocess
# import markdown
from docxtpl import DocxTemplate 

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
    

def markdown_to_docx(markdown_file_path,ORG_NAME,TITLE_NAME,RESEARCH_PERIOD, AUTHOR, IMPACT_PERIOD, RESEARCH_TOPIC, q1, q2, q3, q4, refs):
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
                "q1":q1,
                "q2":q2,
                "q3":q3,
                "q4":q4,
                "refs":refs
                }
    doc.render(docx_content)
    doc.save(docx_file_path)
    

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

