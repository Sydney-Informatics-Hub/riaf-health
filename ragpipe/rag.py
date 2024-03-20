# RAG pipeline for generating impact assessment studies of research activities

import os
import json
import logging
from llama_index import load_index_from_storage
from llama_index.retrievers import VectorIndexRetriever
from llama_index.prompts import PromptTemplate
from llama_index.llms import ChatMessage, MessageRole
from llama_index.chat_engine.condense_question import CondenseQuestionChatEngine
from llama_index.chat_engine import CondensePlusContextChatEngine 
from llama_index.memory import ChatMemoryBuffer

# local package imports
from utils.pubprocess import publications_to_markdown, clean_publications
from retriever.semanticscholar import read_semanticscholar 
from retriever.scholarai import ScholarAI
from retriever.bingsearch import bing_custom_search, get_urls_from_bing, get_titles_from_bing
from retriever.webcontent import web2docs_async, web2docs_simple
from queryengine.queryprocess import QueryEngine
from queryengine.reviewer import ReviewAgent
from indexengine.process import (
    create_index, 
    add_docs_to_index, 
    load_index
    )

# Config parameters (TBD: move to config file)
_fnames_question_prompt = ['Prompt1.md', 'Prompt2.md', 'Prompt3.md', 'Prompt4.md']
_list_max_word =  [250, 300, 500, 300]
_context_window = 4096
_num_output = 600
_scholar_limit = 50
_model_llm = "gpt-4-1106-preview" #"gpt-4-1106-preview" #"gpt-4-32k"
_temperature = 0.1
# Set OpenAI service engine: "azure" or "openai". See indexengine.process.py for azure endpoint configuration
# make sure respective OPENAI_API_KEY is set in os.environ or keyfile
_llm_service = "azure" # "azure" or "openai" # , see 
_use_scholarai = True # use scholarai to retrieve documents. Much more accurate but slower than semanticscholar


logging.basicConfig(level=logging.INFO, format='%(message)s')


class RAGscholar:
    """
    RAG model for scholar publications

    :param fname_system_prompt: path and filename to system prompt
    :param path_index: path to index
    :param path_openai_key: path to openai key
    :param load_index_from_storage: bool, load index from storage path, default False

    """

    def __init__(self, 
                path_templates, 
                fname_system_prompt, 
                fname_report_template,
                outpath, 
                path_index, 
                path_openai_key = None, 
                language_style = "analytical",
                load_index_from_storage = False):
        
        self.path_index = path_index
        self.path_templates = path_templates
        self.path_openai_key = path_openai_key
        self.load_index_from_storage = load_index_from_storage
        self.fname_system_prompt = os.path.join(path_templates, fname_system_prompt)
        self.fname_report_template = os.path.join(path_templates, fname_report_template)
        self.outpath = outpath
        self.index = None
        self.documents = None
        self.research_topic = None
        self.author = None
        self.language_style = language_style

        self.openai_init()

        if load_index_from_storage:
            self.index = load_index(path_index)

    def openai_init(self):
        # Authenticate and read file from file
        #check if "OPENAI_API_KEY" parameter in os.environ:
        if "OPENAI_API_KEY" not in os.environ:
            if self.path_openai_key is None:
                logging.error("OPENAI_API_KEY not found in os.environ and path_openai_key is None")
            else:
                with open(self.path_openai_key , "r") as f:
                    os.environ["OPENAI_API_KEY"] = f.read()


    def generate_chatengine_react(self):
        """
        ReAct agent: follows a flexible approach where the agent decides 
        whether to use the query engine tool to generate responses or not.
        """
        query_engine = QueryEngine.generate_query_engine(self.index)
        self.chat_engine = self.index.as_chat_engine(chat_mode="react", 
                                                     verbose=True, 
                                                     query_engine=query_engine)
        system_prompt = self.generate_system_prompt()
        custom_chat_history = [
            ChatMessage(role=MessageRole.SYSTEM, content=system_prompt),
            ]
        response = self.chat_engine.chat("Are you ready?", custom_chat_history)


    def generate_chatengine_openai(self):
        """
        ReAct agent: follows a flexible approach where the agent decides 
        whether to use the query engine tool to generate responses or not.
        """
        query_engine = QueryEngine.generate_query_engine(self.index)
        self.chat_engine = self.index.as_chat_engine(chat_mode="openai", 
                                                     verbose=True)
        system_prompt = self.generate_system_prompt()
        custom_chat_history = [
            ChatMessage(role=MessageRole.SYSTEM, content=system_prompt),
            ]
        # Add system prompt
        response = self.chat_engine.chat("Are you ready?", custom_chat_history)


    def generate_chatengine_condense(self):
        # Condense Chat Engine:
        system_prompt = self.generate_system_prompt()
        custom_chat_history = [
            ChatMessage(role=MessageRole.SYSTEM, content=system_prompt),
            ]
        #query_engine = self.index.as_query_engine(response_mode="compact")
        query_engine = QueryEngine.generate_query_engine(self.index)
        self.chat_engine = CondenseQuestionChatEngine.from_defaults(
            query_engine=query_engine,
            chat_history=custom_chat_history,
            verbose=True,
            )
        
    def generate_chatengine_condensecontext(self):
        # Condense Plus Context Chat Engine (WIP)
        system_prompt = self.generate_system_prompt()
        """    
        retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=5,
        )
        self.chat_engine = CondensePlusContextChatEngine.from_defaults(
            retriever=retriever,

            chat_history=custom_chat_history,
            verbose=True,
            )
        """  
        memory = ChatMemoryBuffer.from_defaults(token_limit=3900)
        context =   (system_prompt + "\n"
            "Here are the relevant documents for the context:\n"
            "{context_str}"
            "\nInstruction: Use the previous chat history, or the context above, to interact and help the user."
        ),
        self.chat_engine = self.index.as_chat_engine(
            chat_mode="condense_plus_context",
            memory=memory,
            context_prompt=context,
            verbose=True,
            )
        
    def generate_chatengine_context(self):
        # Condense Plus Context Chat Engine (WIP)
        system_prompt = self.generate_system_prompt()

        memory = ChatMemoryBuffer.from_defaults(token_limit=8000)
        self.chat_engine = self.index.as_chat_engine(
            chat_mode="context",
            memory=memory,
            system_prompt=system_prompt,
            verbose=True,
            )
        
    def query_chatengine(self, query):
        """
        Query chat engine for content and sources.

        :param query: str, query to chat engine

        :return: content, sources
        """
        response = self.chat_engine.chat(query)
        content = response.response
        try:
            sources = response.sources[0].raw_output.metadata
        except:
            sources = []
        return content, sources
    

    

    def generate_system_prompt(self):
        with open(self.fname_system_prompt, "r") as file:
            case_study_text = file.read()
        system_prompt = json.dumps(case_study_text, indent=2)
        # replace in system prompt the following: ORG_NAME with org_name, RESEARCH_PERIOD with research_period, STAFF_NAMES with staff_names, IMPACT_PERIOD with impact_period
        system_prompt = system_prompt.replace("ORG_NAME", self.organisation)
        system_prompt = system_prompt.replace("TITLE_NAME", self.research_topic)
        system_prompt = system_prompt.replace("RESEARCH_PERIOD", self.research_period)
        system_prompt = system_prompt.replace("AUTHOR", self.author)
        system_prompt = system_prompt.replace("IMPACT_PERIOD", self.impact_period)
        system_prompt = system_prompt.replace("RESEARCH_TOPIC", self.research_topic)
        system_prompt = system_prompt.replace("LANGUAGE_STYLE", self.language_style)
        return system_prompt

    def prompt_pipeline(self, 
                        list_prompt_filenames = ['Prompt1.md', 'Prompt2.md', 'Prompt3.md', 'Prompt4.md'],
                        list_max_word = [250, 300, 500, 300],
                        review = True):
        """
        Run through prompts from list of prompt filenames.

        :param list_prompt_filenames: list of prompt filenames
        :param list_max_word: list of max word count for each prompt
        :param review: bool (Default False). Use review agent to review content and improve response

        :return: list_questions, list_answers, list_sources
        """
        self.list_answers = []
        self.list_sources = []
        self.list_questions = []
        # Initialize review agent
        # TBD should review agent evaluate each question separately or final report?
        if review:
            review_agent = ReviewAgent()
        for i, prompt_filename in enumerate(list_prompt_filenames):
            with open(os.path.join(self.path_templates, prompt_filename), "r") as file:
                prompt_text = file.read()
            self.list_questions.append(prompt_text.splitlines()[0])
            # query chat engine
            logging.info(f"Querying chat engine with prompt {i} ...")
            content, sources = self.query_chatengine(prompt_text)
            # Check content size
            #while len(content.split()) > list_max_word[i]:
            #    logging.info("Word count exceeds maximum word count. Content is run again though the model.")
            #    content, _ = self.query_chatengine(f"Shorten the last response to {list_max_word[i]} words.")
            if review:
                review_txt = review_agent.run(content, i)
                if review_txt is not None:
                    logging.info("Reviewing response ...")
                    review_prompt = (f"Improve the previous response given the review below: \n"
                                        + "Do not deviate from the original instructions for this question. \n"
                                        + "Review: \n"
                                        + f"{review_txt}")
                    content, sources = self.query_chatengine(review_prompt)
                else:
                    logging.info("No review response. Continuing with original response.")
            self.list_answers.append(content)
            self.list_sources.append(sources)
    

    def generate_case_study(self, process_sources = False):
        
        with open(self.fname_report_template, "r") as file:
            report = file.read()
        #report = json.dumps(report_text, indent=2)
        report = report.replace("ORG_NAME", self.organisation)
        report = report.replace("TITLE_NAME", self.research_topic)
        report = report.replace("RESEARCH_PERIOD", self.research_period)
        report = report.replace("AUTHOR", self.author)
        report = report.replace("IMPACT_PERIOD", self.impact_period)
        report = report.replace("RESEARCH_TOPIC", self.research_topic)
        for i, question in enumerate(self.list_questions):
            report += "\n\n"
            report += f"## {question}\n"
            report += f"{self.list_answers[i]}\n"
        # Process sources
        if process_sources:
            logging.info("Processing publications ...")
            sources = clean_publications(self.list_sources) 
            sources_text = publications_to_markdown(sources)
            report += "\n\n"
            report += "## Sources of evidence\n"
            report += sources_text

        # Save report
        with open(os.path.join(self.outpath, "Use_Case_Study.md"), "w") as file:
            file.write(report)
        logging.info(f"Use case study saved to {self.outpath}")

        
    def run(self, 
            research_topic, 
            author,
            keywords,
            organisation,
            research_start = None,
            research_end = None,
            impact_start = None,
            impact_end = None,
            scholarai_delete_pdfs = False):
        """
        Run RAG pipeline.

        :param research_topic: str, research topic
        :param author: str, author name
        :param keywords: str, keywords
        :param organisation: str, organisation
        :param research_start: int, research period start
        :param research_end: int, research period end
        :param impact_start: int, impact period start
        :param impact_end: int, impact period end
        :param scholarai_delete_pdfs: bool, delete pdfs after processing

        The pipeline includes the following key steps:
        - Search and process documents from Semantic Scholar
        - Search web for content related to research topic
        - Generate index store and save data and metadata in database
        - Initialize chat engine with context prompt
        - Run through prompt questions
        - Generate case study
        """
        path_index_name = research_topic + "_by_" + author
        path_index_name = path_index_name.replace(" ", "_")
        self.research_topic = research_topic
        self.author = author
        self.keywords = keywords
        self.scholarai_delete_pdfs = scholarai_delete_pdfs
        self.organisation = organisation
        
        if research_start is not None:
            try:
                self.research_start = int(research_start)
            except:
                logging.warning("Research period start be integers. Continuing without.")
                self.research_start = None
        if research_end is not None:
            try:
                self.research_end = int(research_end)
            except:
                logging.warning("Research period end be integers. Continuing without.")
                self.research_end = None
        if impact_start is not None:
            try:
                self.impact_start = int(impact_start)
            except:
                logging.warning("Research impact start be integers. Continuing without.")
                self.impact_start = None
        if impact_end is not None:
            try:
                self.impact_end = int(impact_end)
            except:
                logging.warning("Research impact end be integers. Continuing without.")
                self.impact_end = None
        self.research_period = f"{self.research_start}-{self.research_end}"
        self.impact_period = f"{self.impact_start}-{self.impact_end}"


        fname_out = self.research_topic + "_by_" + self.author
        fname_out = fname_out.replace(" ", "_")
        self.outpath = os.path.join(self.outpath, fname_out)
        os.makedirs(self.outpath, exist_ok=True)

        # Search, retrieve and read documents from Semantic Scholar
        if _use_scholarai:
            logging.info("Searching and reading documents with AI-assisted Semantic Scholar...")
            # check if author is a list
            if isinstance(self.author, list):
                authors = self.author
            else:
                authors = [self.author]
            scholar = ScholarAI(self.research_topic,
                                authors, 
                                year_start= self.research_start, 
                                year_end = self.research_end,
                                delete_pdfs = self.scholarai_delete_pdfs)
            papers = scholar.get_papers_from_authors(max_papers = _scholar_limit)
            self.documents = scholar.load_data(papers)

        else:
            logging.info("Searching and reading documents from Semantic Scholar API ..")
            self.documents = read_semanticscholar(self.research_topic, 
                                                self.author, 
                                                self.keywords, 
                                                limit = _scholar_limit,
                                                year_start=self.research_start,
                                                year_end=self.research_end)
            
        # Search web for content related to research topic
        bing_results = bing_custom_search(self.research_topic, 
                                          count=3, 
                                          year_start = self.impact_start, 
                                          year_end= self.impact_end)
        if len(bing_results) > 0:
            urls = get_urls_from_bing(bing_results)
            titles = get_titles_from_bing(bing_results)
            documents_web = web2docs_async(urls, titles)
            if len(self.documents) > 0:
                self.documents = self.documents + documents_web

        # generate index store and save index in self.path_index
        logging.info("Generating index database ...")
        self.path_index = os.path.join(self.path_index, path_index_name)
        self.index = create_index(self.documents, 
                                  self.path_index, 
                                  temperature=_temperature, 
                                  context_window=_context_window, 
                                  num_output=_num_output, 
                                  model_llm=_model_llm,
                                  llm_service=_llm_service)

        # Initialize chat engine with context prompt
        #self.generate_chatengine_condensecontext()
        logging.info("Initializing chat engine ...")
        #self.generate_chatengine_condense()
        # mode: openAI (no publication metadata)
        #self.generate_chatengine_openai()
        # mode: context. retrieve context and run LLM on context
        self.generate_chatengine_context()

        # Run through prompt questions
        logging.info("Processing questions ...")
        self.prompt_pipeline(
            list_prompt_filenames = _fnames_question_prompt,
            list_max_word = _list_max_word
        )
        logging.info("Generating case study ...")
        self.generate_case_study()
        logging.info("FINISHED.")
