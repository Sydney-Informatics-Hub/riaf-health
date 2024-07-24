import os
import logging
import json
import time
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.azure_openai import AzureOpenAI
from llama_index.core.llms import ChatMessage


LLMSERVICE = 'openai' # 'openai' or 'azure'  or 'techlab'

AZURE_ENDPOINT = "https://techlab-copilots-aiservices.openai.azure.com/" 
AZURE_API_VERSION = "2023-12-01-preview" 
AZURE_ENGINE = "gpt-35-turbo"

techlab_endpoint = 'https://apim-techlab-usydtechlabgenai.azure-api.net/'
techlab_deployment = 'GPT35shopfront'
techlab_api_version = '2023-12-01-preview'

class ReviewAgent:
    def __init__(self, 
                 filenames_review = ['Review1.md', 'Review2.md', 'Review3.md', 'Review4.md'],
                 path_templates = './templates/'):
        self.filenames_review = [os.path.join(path_templates, filename) for filename in filenames_review]

        if LLMSERVICE == 'openai':
            self.llm = OpenAI(
                temperature=0,
                model='gpt-4o',
                max_tokens=800)
        elif LLMSERVICE == 'azure':
            self.llm = AzureOpenAI(
                engine=AZURE_ENGINE,
                model='gpt-4-1106-preview', 
                temperature=0,
                azure_endpoint=AZURE_ENDPOINT,
                api_key=os.environ["OPENAI_API_KEY"],
                api_version=AZURE_API_VERSION,
            )
        elif LLMSERVICE == 'techlab':
            self.llm = AzureOpenAI(
                engine=techlab_deployment,
                model='gpt-4-1106-preview', 
                temperature=0,
                azure_endpoint=techlab_endpoint,
                api_key=os.environ["OPENAI_TECHLAB_API_KEY"],
                api_version=techlab_api_version,
            )
        else:
            logging.error(f"LLM service {LLMSERVICE} not supported")
            self.llm = None\
        # check if review filenames exists
        for filename in self.filenames_review:
            if not os.path.exists(filename):
                raise ValueError(f"Review file {filename} does not exist")


    def run(self, content, question_number, response_history=[], additional_context=""):
        """
        LLM run to review a paper given a response and a question number

        :param content: str, content
        :param question_number: int, question number, 0 - 3
        :param response_history: list, response history
        :param additional_context: str, additional context
        """
        with open(self.filenames_review[question_number], "r") as file:
            review_criteria = file.read()
        if additional_context == "":
            self.system_prompt = ("You are an agent that acts as a reviewer. You will review the response from another LLM query. \n"
                    "Follow the review criteria and suggest specific points how to improve the response. \n"
                    "You do not need to address all review criteria, only suggest changes if they are necessary. \n"
                    "Suggestions must be short and concise.\n"
                    "Do not include a revised version in you response\n"
                    "Do NOT introduce any new statements or make up any facts that are not included in the original response.\n\n"
                    f"{review_criteria}")
        else:
            self.system_prompt = ("You are an agent that acts as a reviewer. You will review the response from another LLM query. \n"
                                "Follow the review criteria and suggest specific points how to improve the response. \n"
                                "You do not need to address all review criteria, only suggest changes if they are necessary. \n"
                                "Suggestions must be short and concise.\n"
                                "Do not include a revised version in you response\n"
                                "Do NOT introduce any new statements or make up any facts that are not included in the original response.\n\n"
                                f"{review_criteria}\n\n"
                                f"In addition check that the response also addresses the following: \n"
                                f"{additional_context}"
                                )

        #self.system_prompt = json.dumps(review_criteria, indent=2)
        prompt = (f"Given the review criteria above, provide instructive and concise feedback how to improve the following response: \n"
                    + f"{content}")
        
        if len(response_history) > 0:
            prompt = (f"{prompt} \n\n"
                        + "**Duplications**: check that no statements are repeated from response history.\n"
                        + "If you find any repeated statements, you must also return a list of duplications in your response.\n"
                        + "Each point in this duplication list must include the text snippet of the statement that is duplicated.\n"
                        + "Advise in your review response to not include these duplications.\n\n"
                        + "Do not just refer to the 'response history', but provide specific feedback on the response.\n\n"
                        + "Response History:\n"
            )
            for j in range(len(response_history)):
                prompt = prompt + f"{response_history[j]} \n"
            prompt = prompt + "----End of Response History----\n"

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

