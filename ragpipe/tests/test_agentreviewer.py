import os
import shutil

from agentreviewer.agentreviewer import AgentReviewer
from utils.mdconvert import markdown_to_question

# Setup environment variables required for Azure OpenAI
with open("../../openai_sih_key.txt", "r") as file:
    os.environ["OPENAI_API_KEY"]  = file.read().strip()
    os.environ["OPENAI_TECHLAB_API_KEY"]  = file.read().strip()

# Set the document store and index storage locations and create a temporary dir for the index
example_repsonse_file = '/home/nbutter/PROJECTS/PIPE-4668_FMHchatLLM/PIPE-4668-RIAF_NSWHEALTH/use_case_studies/Elastagen_by_Anthony_Weiss/RIAF_Case_Study_Weiss.md'
markdown_file_path = '/home/nbutter/PROJECTS/PIPE-4668_FMHchatLLM/PIPE-4668-RIAF_NSWHEALTH/use_case_studies/Elastagen_by_Anthony_Weiss/Use_Case_Study.md'
index_path = 'temp_index'

question1 = "## What is the problem this research seeks to address and why is it significant? (Max 250 words)"
question2 = "## What are the research outputs of this study?​ (Max 300 words)"
question3 = "## What impacts has this research delivered to date? (Max 500 words)"
question4 = "## What impact from this research is expected in the future? (Max 300 words)"
end_text = "**References**"

agent_reviewer = AgentReviewer(llm=None,LLMSERVICE='openai')

# Define a test function for create_index
def test_review_response():

    response_text = markdown_to_question(markdown_file_path, question1, end_text)

    question_text = 'What is the problem this research seeks to address and why is it significant?'

    with open(example_repsonse_file, 'r', encoding='utf-8') as file:
        example_response = file.readline().strip()

    response = agent_reviewer.review_response(question_text, response_text, example_response)

    # print(question_text)
    # print(response_text)
    # print(example_response)

    print("This gets a score of", response)



# Run the tests
test_review_response()
