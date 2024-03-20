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
                 filenames_review = ['Review1.md', 'Review2.md', 'Review3.md', 'Review4.md'],
                 path_templates = './templates/'):
        self.filenames_review = [os.path.join(path_templates, filename) for filename in filenames_review]

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
        # check if review filenames exists
        for filename in self.filenames_review:
            if not os.path.exists(filename):
                raise ValueError(f"Review file {filename} does not exist")


    def run(self, content, question_number):
        """
        LLM run to review a paper given a response and a question number

        :param content: str, content
        :param question_number: int, question number, 0 - 3
        """
        with open(self.filenames_review[question_number], "r") as file:
            review_criteria = file.read()
        self.system_prompt = ("You are an LLM agent that acts as a reviewer. You will review the response from another LLM query. \n"
                            "Follow the review criteria strictly and suggest changes to the text if necessary. \n"
                            "You do not need to address all review criteria, only suggest changes if they are necessary. \n"
                            "Suggestions must be short and concise. \n\n"
                            f"{review_criteria}")
        #self.system_prompt = json.dumps(review_criteria, indent=2)
        prompt = (f"Given the review criteria above, provide instructive and concise feedback how to improve the following response: \n"
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

