import os
import logging
import json
import time
from llama_index.llms.openai import OpenAI
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core.llms import ChatMessage


LLMSERVICE = 'azure' # 'openai' or 'azure'
AZURE_ENDPOINT = "https://techlab-copilots-aiservices.openai.azure.com/" 
AZURE_API_VERSION = "2023-12-01-preview" 
AZURE_ENGINE = "gpt-35-turbo"

class ReviewAgent:
    def __init__(self, 
                 filename_review_prompt = "review_criteria.txt",
                 path_templates = './templates/'):
        self.filename_review_prompt = os.path.join(path_templates, filename_review_prompt)

        if LLMSERVICE == 'openai':
            self.llm = OpenAI(
                temperature=0,
                model='gpt-3.5-turbo',
                max_tokens=1)
        elif LLMSERVICE == 'azure':
            self.llm = AzureOpenAI(
                engine=AZURE_ENGINE,
                model='gpt-3.5-turbo',
                temperature=0,
                azure_endpoint=AZURE_ENDPOINT,
                api_key=os.environ["OPENAI_API_KEY"],
                api_version=AZURE_API_VERSION,
            )
        else:
            logging.error(f"LLM service {LLMSERVICE} not supported")
            self.llm = None\
        # check if review_prompt exists
        if not os.path.exists(self.filename_review_prompt):
            logging.error(f"Review prompt {self.filename_review_prompt} not found")
        with open(self.filename_review_prompt, "r") as file:
            review_criteria = file.read()
        self.system_prompt = json.dumps(review_criteria, indent=2)

    def run(self, content):
        """
        LLM run to review a paper.

        :param content: str, content
        """
        prompt = (f"Given the review criteria, provide instructive and concise feedback how to improve the following content: \n"
                    + f"{content}")
        messages = [
                ChatMessage(role="system", content=self.system_prompt),
                ChatMessage(role="user", content=prompt),
            ]
        max_try = 0
        result = None
        while result is None and max_try < 3:
            try:
                response = self.llm.chat(messages)
                result = response.message.content
            except:
                logging.error(f"LLM not responding")
                max_try += 1
                # sleep for 5 seconds to avoid rate limit
                time.sleep(5)
        if result is not None:
            return result
        else:
            logging.error(f"LLM response is None after 3 tries.")
            return None

