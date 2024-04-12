
# Convert Markdown to PDF using mdpdf


import os
import subprocess
import markdown

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
