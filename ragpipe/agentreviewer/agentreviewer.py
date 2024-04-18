"""
AgentReviewer class reviews text and gives it a score.

How to use:

set environment variable OPENAI_API_KEY  with your Azure OpenAI key (default) or OpenAI key.

Python:
------
from agentreviewer.agentreviewer import AgentReviewer
reviewer = AgentReviewer()
updated_text = reviewer.review_output("This is the text to review.", {"ees": "All words should end in e",})
------

see for example: tests/test_responsereview.py

Author: Nathaniel Butterworth
"""
import os
import time
import logging

from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI
from llama_index.llms.azure_openai import AzureOpenAI


AZURE_ENDPOINT = "https://techlab-copilots-aiservices.openai.azure.com/"
AZURE_API_VERSION = "2023-12-01-preview"
AZURE_ENGINE = "gpt-35-turbo"

techlab_endpoint = 'https://apim-techlab-usydtechlabgenai.azure-api.net/'
techlab_deployment = 'GPT35shopfront'
techlab_api_version = '2023-12-01-preview'

class AgentReviewer:
    def __init__(self, llm, LLMSERVICE):
        self.LLMSERVICE = 'openai'  # 'openai' or 'azure' or 'techlab'
        self.llm = None

    def init_llm(self):
        if self.LLMSERVICE == 'openai':
            self.llm = OpenAI(
                temperature=0,
                model='gpt-4-1106-preview',
                max_tokens=600)
        elif self.LLMSERVICE == 'azure':
            self.llm = AzureOpenAI(
                engine=AZURE_ENGINE,
                model='gpt-3.5-turbo',
                temperature=0,
                azure_endpoint=AZURE_ENDPOINT,
                api_key=os.environ["OPENAI_API_KEY"],
                api_version=AZURE_API_VERSION,
            )
        elif self.LLMSERVICE == 'techlab':
            self.llm = AzureOpenAI(
                engine=techlab_deployment,
                model='gpt-4-1106-preview',
                temperature=0,
                azure_endpoint=techlab_endpoint,
                api_key=os.environ["OPENAI_TECHLAB_API_KEY"],
                api_version=techlab_api_version,
            )
        else:
            logging.error(f"LLM service {self.LLMSERVICE} not supported")
            return None
        return self.llm

    def review_output(self, output_text, marking_criteria):
        """
        Review the output from another LLM query based on marking criteria.

        :param output_text: str, the text output from an LLM query to be reviewed
        :param marking_criteria: dict, the marking criteria to be used for the review
        """
        system_prompt = ("You are an LLM agent that reviews text. "
                         "You will review text following a marking criteria strictly and suggest changes to the text if necessary.")

        user_prompt = ("Here is text:\n\n"
                       f"{output_text}\n\n"
                       "Review this output according to the following marking criteria:\n")

        # Add marking criteria to the prompt
        for criterion, description in marking_criteria.items():
            user_prompt += f"\n{criterion}: {description}"

        user_prompt += "\n\nImplement any changes that should be made to the text."

        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_prompt),
        ]

        if self.llm is None:
            self.llm = self.init_llm()

        max_try = 0
        result = None
        while result is None and max_try < 3:
            try:
                response = self.llm.chat(messages)
                result = response.message.content.strip()
            except Exception as e:
                logging.error(f"LLM not responding: {e}")
                max_try += 1
                time.sleep(5)  # Sleep to avoid rate limit

        return result

    def review_response(self, question_text, response_text, example_response):

        system_prompt = ("You are an LLM agent that acts as a reviewer. You will review responses to specific questions based on a baseline example and review criteria. You will only give a score between 1 and 5.")

        user_prompt = (f"This is a response to the question '{question_text}':\n\n")
        user_prompt += f"{response_text}\n\n"
        user_prompt += "Compare the question response to the provided example (which represents a score of 3) and give it a score based on the example and the marking criteria."

        user_prompt += "The example response that represents a score of 3 is as follows:\n"
        user_prompt += f"{example_response}\n\n"

        user_prompt += "Compare this response to the baseline example provided and give it a Score of 5, 4, 3, 2, or 1 based on the following marking criteria:\n"

        # Define the marking criteria based on the assessment criteria provided
        marking_criteria = {
            'Score 5' : "Research is highly relevant and congruent with the needs and interests of its users and/or beneficiaries. It is fully focused on addressing their challenges or priorities. Research that has achieved exceptional dissemination, understanding and application. Research findings have reached beyond the target audience and relevant stakeholders. Research outcomes have a transformational impact on advancing policy and practice, health and wellbeing, the economy, and/or the organisation’s reputation and brand. ",
            'Score 3': "Research shows a reasonable level of relevance and congruence with the needs and interests of its users and/or beneficiaries. It is moderately focused on addressing their challenges or priorities. Research has achieved moderate dissemination, understanding and application. Research findings have reached a considerable proportion of the target audience and relevant stakeholders. Research outcomes have a notable influence on advancing policy and practice, health and wellbeing, the economy, and/or the organization's reputation and brand.",
            'Score 1': "Research lacks relevance and congruence with the needs and interest of its users and/or beneficiaries. It is not focused on addressing their challenges or priorities. Research has a minimal dissemination, understanding and application. The research findings have not reached the target audience and relevent stakeholders. The research outcomes have a minimal or negligible contribution to advancing policy and practice, health and wellbeing, the economy, and/or the organisation's reputation and brand."
        }

        # Add marking criteria to the prompt
        for criterion, description in marking_criteria.items():
            user_prompt += f"\n{criterion}: {description}"

        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_prompt),
        ]

        if self.llm is None:
            print("initiing")
            self.llm = self.init_llm()

        max_try = 0
        result = None
        while result is None and max_try < 3:
            try:
                response = self.llm.chat(messages)
                result = response.message.content.strip()
            except Exception as e:
                logging.error(f"LLM not responding: {e}")
                max_try += 1
                time.sleep(5)  # Sleep to avoid rate limit

        return result

        # Send the prompt to the LLM
        response = self.llm.query(prompt)

        # Process the response and return the review
        return response.text



# Usage example
if __name__ == "__main__":
    agent_reviewer = AgentReviewer()
    example_reports = [
        "Example report 1 text...",
        "Example report 2 text...",
        # More example reports...
    ]
    example_reviews = [
        "Example review 1 text...",
        "Example review 2 text...",
        # More example reviews...
    ]
    new_report = "Example of a new report text here..."
    review = agent_reviewer.review_output(new_report, example_reports, example_reviews)
    print("Generated Review:", review)

# # Example usage:
# if __name__ == "__main__":
#     # Marking criteria example (should be replaced with actual criteria)
#     marking_criteria = {
#         "Relevance": "The text should be strictly relevant to the topic of discussion.",
#         "Clarity": "The text should be clear and understandable without ambiguity.",
#         "Accuracy": "All factual information should be accurate and verifiable."
#     }

#     # Example output text from another LLM query
#     output_text = "The research is important."

#     # Initialize the LLMAgentReviewer
#     reviewer = AgentReviewer(llm=None)

#     # Review the output text
#     review_result = reviewer.review_output(output_text, marking_criteria)

#     print("Review Result:")
#     print(review_result)
