import os

from agentreviewer.agentreviewer import AgentReviewer
from utils.mdconvert import markdown_to_question

# Setup environment variables required for Azure OpenAI
with open("../../openai_sih_key.txt", "r") as file:
    os.environ["OPENAI_API_KEY"]  = file.read().strip()
    os.environ["OPENAI_TECHLAB_API_KEY"]  = file.read().strip()

# Set gold standard response paths. These are broken up by indivdual question.
example_repsonse_file_q1 = '../use_case_studies/Elastagen_by_Anthony_Weiss/RIAF_Case_Study_Weiss_q1.md'
example_repsonse_file_q2 = '../use_case_studies/Elastagen_by_Anthony_Weiss/RIAF_Case_Study_Weiss_q2.md'
example_repsonse_file_q3 = '../use_case_studies/Elastagen_by_Anthony_Weiss/RIAF_Case_Study_Weiss_q3.md'
example_repsonse_file_q4 = '../use_case_studies/Elastagen_by_Anthony_Weiss/RIAF_Case_Study_Weiss_q4.md'

# Set the Final output file from the pipeline, this is in the full markdown format
markdown_file_path = '../../results/Elastagen_by_Anthony_Weiss_withoutlocal/Use_Case_Study.md'

# The markdown file needs to be broken up into approriate chunks (i.e. each question), which
# can be captured between the question and the references tage.
question1 = "## What is the problem this research seeks to address and why is it significant? (Max 250 words)"
question2 = "## What are the research outputs of this study?​ (Max 300 words)"
question3 = "## What impacts has this research delivered to date? (Max 500 words)"
question4 = "## What impact from this research is expected in the future? (Max 300 words)"
end_text = "**References**"

# Inititalise the Reviwer Agent.
agent_reviewer = AgentReviewer(llm=None,LLMSERVICE='openai')

# Define a test function for create_index
def test_review_response():

    #Grab the q1 phrasing to pass to the review agent, the pipeline response to q1, and the q1 exemplar response.
    question_text_q1 = 'What is the problem this research seeks to address and why is it significant?'
    response_text_q1 = markdown_to_question(markdown_file_path, question1, end_text)
    with open(example_repsonse_file_q1, 'r', encoding='utf-8') as file:
        example_response_q1 = file.readline().strip()

    question_text_q2 = 'What are the research outputs of this study?'
    response_text_q2 = markdown_to_question(markdown_file_path, question2, end_text)
    with open(example_repsonse_file_q2, 'r', encoding='utf-8') as file:
        example_response_q2 = file.readline().strip()

    question_text_q3 = 'What impacts has this research delivered to date?'
    response_text_q3 = markdown_to_question(markdown_file_path, question3, end_text)
    with open(example_repsonse_file_q3, 'r', encoding='utf-8') as file:
        example_response_q3 = file.readline().strip()

    question_text_q4 = 'What impact from this research is expected in the future?'
    response_text_q4 = markdown_to_question(markdown_file_path, question4, end_text)
    with open(example_repsonse_file_q1, 'r', encoding='utf-8') as file:
        example_response_q4 = file.readline().strip()

    response_q1 = agent_reviewer.review_response(question_text_q1, response_text_q1, example_response_q1)
    print("Q1", response_q1)
    response_q2 = agent_reviewer.review_response(question_text_q2, response_text_q2, example_response_q2)
    print("Q2", response_q2)
    response_q3 = agent_reviewer.review_response(question_text_q3, response_text_q3, example_response_q3)
    print("Q3", response_q3)
    response_q4 = agent_reviewer.review_response(question_text_q4, response_text_q4, example_response_q4)
    print("Q4", response_q4)

# Run the tests
test_review_response()