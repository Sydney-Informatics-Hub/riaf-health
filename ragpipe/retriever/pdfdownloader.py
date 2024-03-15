# Pdf downloader 
import os
import requests
import logging
import arxiv

def download_pdf(paper_id, url, base_dir):
    logger = logging.getLogger()
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
            " like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        )
    }
    # Making a GET request
    response = requests.get(url, headers=headers, stream=True)
    content_type = response.headers["Content-Type"]

    # As long as the content-type is application/pdf, this will download the file
    if "application/pdf" in content_type:
        os.makedirs(base_dir, exist_ok=True)
        file_path = os.path.join(base_dir, f"{paper_id}.pdf")
        # check if the file already exists
        if os.path.exists(file_path):
            logger.info(f"{file_path} already exists")
            return file_path
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        logger.info(f"Downloaded pdf from {url}")
        return file_path
    else:
        logger.warning(f"{url} was not downloaded: protected")
        return None
    

def download_pdf_from_arxiv(paper_id, arxiv_id, base_dir):
    paper = next(arxiv.Search(id_list=[arxiv_id], max_results=1).results())
    paper.download_pdf(dirpath=base_dir, filename=paper_id + ".pdf")
    return os.path.join(base_dir, f"{paper_id}.pdf")