# RAG pipeline for generating impact assessment studies of research activities

import os
import json
import logging

from llama_index.core import load_index_from_storage
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core import PromptTemplate, Document
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.chat_engine import CondenseQuestionChatEngine
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from docxtpl import DocxTemplate

# local package imports
from utils.pubprocess import publications_to_markdown, clean_publications
from utils.envloader import load_api_key
from retriever.semanticscholar import read_semanticscholar 
from retriever.scholarai import ScholarAI
from retriever.bingsearch import (
    bing_custom_search, 
    get_urls_from_bing, 
    get_titles_from_bing,
    get_snippets_from_bing)
from retriever.webcontent import web2docs_async, web2docs_simple
from retriever.directoryreader import MyDirectoryReader
from queryengine.queryprocess import QueryEngine
from queryengine.reviewer import ReviewAgent
from indexengine.process import (
    create_index, 
    add_docs_to_index, 
    load_index
    )
from agentreviewer.agentreviewer import AgentReviewer
#from utils.mdconvert import convert_answers_to_docx

# Config parameters (TBD: move to config file)
_fnames_question_prompt = ['Prompt1.md', 'Prompt2.md', 'Prompt3.md', 'Prompt4.md']
_list_max_word =  [250, 300, 500, 300]
_context_window = 4096
_num_output = 1000
_scholar_limit = 50
_model_llm = "gpt-4o" #"gpt-4-1106-preview" #"gpt-4-32k"
_temperature = 0.1
# Set OpenAI service engine: "azure" or "openai". See indexengine.process.py for azure endpoint configuration
_use_scholarai = True # use scholarai script to retrieve documents. Much more accurate but slower than semanticscholar


class RAGscholar:
    """
    RAG model for scholar publications

    :param path_templates: path to templates
    :param fname_system_prompt: path and filename to system prompt
    :param fname_report_template: path and filename to report template
    :param outpath: path to output
    :param path_index: path to index
    :param path_documents: path name to directory from where to read documents for index
    :param path_openai_key: path to openai key
    :param language_style: str, language style, default "analytical"
    :param load_index_from_storage: bool, load index from storage path, default False
    """

    def __init__(self, 
                path_templates, 
                fname_system_prompt, 
                fname_report_template,
                outpath, 
                path_index, 
                path_documents = None,
                path_openai_key = None, 
                language_style = "analytical",
                load_index_from_storage = False,
                output_stream=None):
        
        self.path_index = path_index
        self.path_templates = path_templates
        self.path_openai_key = path_openai_key
        self.load_index_from_storage = load_index_from_storage
        self.fname_system_prompt = os.path.join(path_templates, fname_system_prompt)
        self.fname_report_template = os.path.join(path_templates, fname_report_template)
        self.outpath = outpath
        self.index = None
        self.documents = None
        self.context = '' # context scratchpad
        self.research_topic = None
        self.author = None
        self.language_style = language_style
        self.documents_missing = []
        if path_documents is not None:
            if os.path.exists(path_documents):
                self.path_documents = path_documents
            else:
                self.path_documents = None

        load_api_key(toml_file_path='secrets.toml')
        self.llm_service = os.getenv("OPENAI_API_TYPE")

        if load_index_from_storage:
            self.index = load_index(path_index)

    def openai_init(self):
        # Authenticate and read file from file
        #check if "OPENAI_API_KEY" parameter in os.environ:
        if "OPENAI_API_KEY" not in os.environ:
            logging.error("OPENAI_API_KEY not found in os.environ nor in secrets.toml")


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

        memory = ChatMemoryBuffer.from_defaults(token_limit=10000)
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
                        review = True,
                        include_context_text = True):
        """
        Run through prompts from list of prompt filenames.

        :param list_prompt_filenames: list of prompt filenames
        :param list_max_word: list of max word count for each prompt
        :param review: bool (Default False). Use review agent to review content and improve response
        :param include_context_text: bool (Default True). Add context text to prompt as saved in self.context

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
            if include_context_text and (self.context != ''):
                prompt_text = prompt_text + "\n\n Additional context info:\n" + self.context
            # query chat engine
            logging.info(f"Querying chat engine with prompt {i} ...")
            content, sources = self.query_chatengine(prompt_text)
            logging.info(f"Response {i}: {content}")
            # Check content size
            #while len(content.split()) > list_max_word[i]:
            #    logging.info("Word count exceeds maximum word count. Content is run again though the model.")
            #    content, _ = self.query_chatengine(f"Shorten the last response to {list_max_word[i]} words.")
            if review:
                review_txt = review_agent.run(content, i)
                logging.info(f"Review response {i}: {review_txt}")
                if review_txt is not None:
                    logging.info("Reviewing response ...")
                    review_prompt = (f"Improve the previous response given the suggestions in the review below: \n"
                                        + "Instructions: \n"
                                        + "Do not deviate from the original instructions for this question. \n"
                                        + "Stay close to original response and references, only improve the parts of response that need to be fixed. \n"
                                        + "If you can not find an improvement, keep the original response. \n"
                                        + "You must include all references and links to references. Update reference footnote numbers if necessary. \n\n"
                                        + "Review: \n"
                                        + f"{review_txt}")
                    content, sources = self.query_chatengine(review_prompt)
                    logging.info(f"Response {i} after review: {content}")
                else:
                    logging.info("No review response. Continuing with original response.")
            self.list_answers.append(content)
            self.list_sources.append(sources)
            print(f'Finished processing question {i}.')

    def context_engine(self, max_tokens_context = 2000):
        """
        Analyse problem and context using chat engine.
        Save results to self.context

        Args:
        max_tokens_context: int, maximum tokens for context

        Steps:
        1. Generate context question prompt
        2. Query chat engine
        3. Add context to self.context
        4. Find missing information and generate web search queries
        5. Run web search queries
        6. Extract content from web search results 
        7. Generate index store and save content and metadata in vector database
        8. Answer missing questions by querying database
        9. Add missing info to self.context
        """
        # Step 1
        prompt_text = ("Analyse the problem and context for the following topic:\n"
                        f"{self.research_topic}\n\n"
                        "Use the following questions to guide your analysis:\n"
                        "1. What is the primary problem that this topic is aiming to address with regard to the healthcare and medical sector? (max 100 words)\n"
                        "2. What is the context of the problem in terms of healthcare sector and medicine? (max 100 words)\n"
                        "3. Who is mainly impacted or effected by this problem or its consequences? (max 50 words)\n"
                        "4. How many people are impacted by health issues that are related to this problem? (max 50 words)\n"
                        "5. What are the economic costs in $ related to this problem? (max 50 words)\n"
                        f"6. What is the novelty or advantage of the new solution as proposed by {self.author} (max 100 words)\n"
                        "7. How would the proposed solution to this problem improve healthcare? (max 100 words)\n"
                        "8. What are the commercial (in $) or societal implications of the proposed solution? (max 100 words)\n"
            
                        "Instructions:\n"
                        "Do not repeat or rephrase the questions and only provide concise answers within the word limit.\n"
                        "You must include references and links to relevant sources of evidence."
                        )
        # Step 2
        content, sources = self.query_chatengine(prompt_text)

        # Step 3: add content to context string
        self.context = content
        logging.info(f"Problem and context added: {content}")

        # Step 4:  Extract missing information and generate web search queries
        prompt_text = ("Based on the answers above, identify missing information and quantitative data statements to back up the answers.\n"
                        "Then formulate up to 10 short Google search queries that will search for this missing information and data.\n"
                        "What do you type in the search box?\n\n"

                        "Example missing information statements: \n"
                        "The commercial value of this technology is [X] billion dollars. \n"
                        "This research application would save the Australian healthcare sector [X] million dollars yearly.\n"
            
                        "Instructions:\n"
                        "Do not repeat or rephrase the questions and only provide concise answers.\n"
                        "Provide missing information in one sentence per line, starting with 'MissingInfo:' and using '[X]' as blank.\n"
                        "Start each web query with 'WebSearch_String:'\n"
                        )
        
        content_missing, sources = self.query_chatengine(prompt_text)
        
        logging.info(f"Missing information: {content_missing}")

        missing_info = []
        web_search_queries = []
        for line in content_missing.splitlines():
            if line.startswith("MissingInfo:"):
                missing_info.append(line)
            elif line.startswith("WebSearch_String:"):
                web_search_queries.append(line)

        # Step 5: run web search queries for missing information
        web_search_results = []
        webcontext = []
        #create missing information index
        for query in web_search_queries:
            # Todo: replace with retriever.bingsearch.BingSearch (snippets created from web page content)
            logging.info(f"Running web search query: {query}")
            print(f"Running web search query: {query}")
            query = query.replace("WebSearch_String:", "").strip()
            bing_results = bing_custom_search(query, count=2)
            webcontext = []
            # Step 6: Extract content from web search results
            if len(bing_results) > 0:
                logging.info(f"Retrieving web content for {len(bing_results)} sources...")
                urls = get_urls_from_bing(bing_results)
                titles = get_titles_from_bing(bing_results)
                snippets = get_snippets_from_bing(bing_results)
                webcontent, documents_missing = web2docs_async(urls, titles)
                if len(webcontent) > 0:
                    webcontext += webcontent
                if len(documents_missing) > 0:
                    logging.info(f"Web content missing for {len(documents_missing)} sources.")
                    self.documents_missing.extend(documents_missing)
                    # add web snippets to documents instead of full content
                    urls_missing = [doc['url'] for doc in documents_missing]
                    titles_missing = [doc['title'] for doc in documents_missing]
                    # find snippets missing by finding indices matching urls_missing with urls
                    snippets_missing = []
                    for url in urls_missing:
                        index = urls.index(url)
                        snippets_missing.append(snippets[index])
                    metadata = [{'href': url, 'title': title} for url, title in zip(urls_missing, titles_missing)]
                    documents = [Document(text=content, doc_id = url, extra_info = metadata) for content, url, metadata in zip(snippets_missing, urls_missing, metadata)]
                    webcontext += documents
                    logging.info(f"Added {len(snippets_missing)} snippets to web context.")
            else:
                logging.info("No web search results found.")

        # Step 7. Generate index store and save content and metadata in vector database
        if len(webcontext) > 0:
            # generate index store and save data and metadata in database
            logging.info("Generating index database for web context ...")
            self.path_index_context = os.path.join(self.path_index, "webcontext")
            self.index_context = create_index(webcontext,
                                                self.path_index_context,
                                                temperature=_temperature,
                                                context_window=_context_window,
                                                num_output=_num_output,
                                                model_llm=_model_llm,
                                                llm_service=self.llm_service)
            # Initialize chat engine with context prompt
            logging.info("Initializing chat engine with web context ...")
            system_prompt = ("You are an LLM agent that acts as a assistant to find missing information from data.\n"
                             "You must provide concise and quantitative answers.\n"
                             "If you can not find the answer, respond with 'No data found'.\n"
                             "You must provide references for each answer.\n"
            )

            memory = ChatMemoryBuffer.from_defaults(token_limit=4000)
            chat_engine_context2 = self.index_context.as_chat_engine(
                chat_mode="context",
                memory=memory,
                system_prompt=system_prompt,
                verbose=True,
                )
            
            # Step 8. Answer missing questions by querying chat engine with index_context as context
            logging.info("Answering missing questions with web context ...")
            missing_info_remaining = []
            for info in missing_info:
                info = info.replace("MissingInfo:", "")
                query = ("Fill in the blanks (e.g. [X]) in the following sentence: \n"
                        f"{info} \n\n"
                        "Instructions: Return the original sentence with information replacing the blank.\n"
                        "If you can't find the answer to fill in the blank, you must respond with only 'None'.\n"
                        )
                response = chat_engine_context2.chat(query)
                content = response.response
                logging.info(f"Missing question: {query}")
                logging.info(f"Answer: {content}")
                # Step 9: add to self.context
                if content == "None":
                    missing_info_remaining.append(info)
                else:
                    self.context += content + "\n\n"
            if len(missing_info_remaining) > 0:
                logging.info("Some missing information could not be found.")
                print("saving missing info in missing_info.txt")
                with open(os.path.join(self.outpath, "missing_info.txt"), "w") as file:
                    for info in missing_info_remaining:
                        file.write(info + "\n")
        else:
            logging.info("No web context found. Continuing with current context.")
            print("saving missing info in missing_info.txt")
            with open(os.path.join(self.outpath, "missing_info.txt"), "w") as file:
                for info in missing_info:
                    file.write(info + "\n")

        # check token limit and truncate context if necessary
        if len(self.context.split()) > max_tokens_context:
            logging.info("Token limit exceeded. Context is too long. Context is truncated.")
            self.context = " ".join(self.context.split()[:max_tokens_context])

    

    def generate_case_study(self, process_sources = False, make_docx = True):
        
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
        sources_text = None
        if process_sources:
            logging.info("Processing publications ...")
            sources = clean_publications(self.list_sources) 
            sources_text = publications_to_markdown(sources)
            report += "\n\n"
            report += "## Sources of evidence\n"
            report += sources_text
        else:
            sources_text = ""

        # Save report
        with open(os.path.join(self.outpath, "Use_Case_Study.md"), "w") as file:
            file.write(report)

        print(sources_text)
        if make_docx:
            doc = DocxTemplate("./templates/RIAF_template.docx")
            docx_content = { 
                "ORG_NAME":self.organisation, 
                "TITLE_NAME": self.research_topic,
                "RESEARCH_PERIOD":self.research_period,
                "AUTHOR":self.author,
                "IMPACT_PERIOD":self.impact_period,
                "RESEARCH_TOPIC":self.research_topic,
                "q1":self.list_answers[0],
                "q2":self.list_answers[1],
                "q3":self.list_answers[2],
                "q4":self.list_answers[3],
                "refs":sources_text
                }
            doc.render(docx_content)
            doc.save(os.path.join(self.outpath, "Use_Case_Study.docx"))
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
            scholarai_delete_pdfs = False,
            local_document_path = None,
            benchmark_review = True):
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
        :param local_document_path: str, path to the optional user-defined folder of documents  

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

        # setup log function
        logfile = os.path.join(self.outpath, 'ragscholar.log')
        logging.basicConfig(filename = logfile, filemode = 'w', level=logging.INFO, format='%(message)s')

        # Search, retrieve and read documents from Semantic Scholar
        if _use_scholarai:
            print("Searching and reading documents with AI-assisted Semantic Scholar...")
            logging.info("Searching and reading documents with AI-assisted Semantic Scholar...")
            # check if author is a list
            if isinstance(self.author, list):
                authors = self.author
            else:
                authors = [self.author]
            # convert keywords to list
            if isinstance(self.keywords, str):
                keywords = self.keywords.split(",")
            else:
                keywords = self.keywords
            scholar = ScholarAI(self.research_topic,
                                authors, 
                                year_start= self.research_start, 
                                year_end = self.research_end,
                                delete_pdfs = self.scholarai_delete_pdfs,
                                keywords = keywords)
            papers, citations = scholar.get_papers_from_authors(max_papers = _scholar_limit)
            self.documents, documents_missing = scholar.load_data(papers)
            self.papers_scholarai = papers
            self.citations_scholarai = citations
            # publication count
            npublications = len(self.papers_scholarai)
            # add all counts in list self.citations_scholarai
            ncitations = sum([int(c) for c in self.citations_scholarai])
            # three papers with most citations
            if len(self.papers_scholarai) > 2:
                top_cited_papers = [self.papers_scholarai[i]['title'] + ', citations: ' + str(self.citations_scholarai[i]) for i in range(3)]
            else:
                top_cited_papers = []
            if len(documents_missing) > 0:
                self.documents_missing.extend(documents_missing)
                
        else:
            print("Searching and reading documents from Semantic Scholar API ..")
            logging.info("Searching and reading documents from Semantic Scholar API ..")
            self.documents = read_semanticscholar(self.research_topic, 
                                                self.author, 
                                                self.keywords, 
                                                limit = _scholar_limit,
                                                year_start=self.research_start,
                                                year_end=self.research_end)
            npublications = None
            
        # Upload documents to index from directory
        if self.path_documents is not None:
            print("Loading documents from directory ...")
            logging.info("Loading documents from directory ...")
            reader = MyDirectoryReader(self.path_documents)
            mydocuments = reader.load_data()
            # if len(self.documents) > 0:
            #     self.documents = self.documents + mydocuments
            # else:
            self.documents = mydocuments

        
        # Search web for content related to research topic
        print("Searching web for content ...")
        logging.info("Searching web for content ...")
        bing_results = bing_custom_search(self.research_topic, 
                                          count=3, 
                                          year_start = self.impact_start, 
                                          year_end= self.impact_end)
        if len(bing_results) > 0:
            print(f"Retrieving web content for {len(bing_results)} sources...")
            logging.info(f"Retrieving web content for {len(bing_results)} sources...")
            urls = get_urls_from_bing(bing_results)
            titles = get_titles_from_bing(bing_results)
            snippets = get_snippets_from_bing(bing_results)
            documents_web, documents_missing = web2docs_async(urls, titles)
            if len(self.documents) > 0:
                self.documents = self.documents + documents_web
            else:
                self.documents = documents_web
            if len(documents_missing) > 0:
                # add list of a urls and titles to missing documents
                self.documents_missing.extend(documents_missing)
                # add web snippets to documents instead of full content
                urls_missing = [doc['url'] for doc in documents_missing]
                titles_missing = [doc['title'] for doc in documents_missing]
                # find snippets missing by finding indices matching urls_missing with urls
                snippets_missing = []
                for url in urls_missing:
                    index = urls.index(url)
                    snippets_missing.append(snippets[index])
                metadata = [{'href': url, 'title': title} for url, title in zip(urls_missing, titles_missing)]
                documents_web = [Document(text=content, doc_id = url, extra_info = metadata) for content, url, metadata in zip(snippets_missing, urls_missing, metadata)]
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
                                llm_service=self.llm_service)
        
        # Add documents from the additional folder to the aggregated documents
        if local_document_path: 
            print("Adding documents from local folder ...")
            self.index = add_docs_to_index(local_document_path, self.index)  

        # Initialize chat engine with context prompt
        #self.generate_chatengine_condensecontext()
        logging.info("Initializing chat engine ...")
        #self.generate_chatengine_condense()
        # mode: openAI (no publication metadata)
        #self.generate_chatengine_openai()
        # mode: context. retrieve context and run LLM on context
        self.generate_chatengine_context()

        # Analyse problem and context
        print("Analyse problem and context...")
        self.context_engine()


        # Add publications and citations to context
        # npublications = None
        if npublications is not None:
            self.context += "\n\n"
            self.context += f"Publication analysis for {self.author}:\n"
            self.context += f"Number of topic-related publications for period {self.research_start} - {self.research_end}: At least {npublications}\n"
            self.context += f"Number of citations: At least {ncitations}\n"
            if len(top_cited_papers) > 0:
                self.context += "Top cited papers:\n"
                for i, paper in enumerate(top_cited_papers):
                    self.context += f"{i+1}. {paper}\n"

        # Save context to file
        with open(os.path.join(self.outpath, "context_analysis.txt"), "w") as file:
            file.write(self.context)

        # Save missing documents to file
        if len(self.documents_missing) > 0:
            with open(os.path.join(self.outpath, "missing_documents.txt"), "w") as file:
                for doc in self.documents_missing:
                    file.write(doc['title'] + ": " + doc['url'] + "\n")

        # Run through prompt questions
        print("Processing assessment questions ...")
        logging.info("Processing assessment questions ...")
        self.prompt_pipeline(
            list_prompt_filenames = _fnames_question_prompt,
            list_max_word = _list_max_word
        )
        print("Generating case study ...")
        logging.info("Generating case study ...")
        self.generate_case_study(make_docx=True)
        print("Finished.")
        logging.info("FINISHED.")

        if benchmark_review:
            agent_reviewer = AgentReviewer(llm=None,LLMSERVICE='openai')
            # Set gold standard response paths. These are broken up by indivdual question.
            # check that the path ../use_case_studies/'+fname_out+'/ exists, if not stop the review
            if not os.path.exists('../use_case_studies/'+fname_out+'/'):
                print("No benchmark review possible. No matching case study folder found.")
                logging.info("No benchmark review possible. No matching case study folder found.")
            else:
                print("Benchmark review ...")
                logging.info("Benchmark review ...")
                example_repsonse_file_q1 = '../use_case_studies/'+fname_out+'/RIAF_Case_Study_q1.md'
                example_repsonse_file_q2 = '../use_case_studies/'+fname_out+'/RIAF_Case_Study_q2.md'
                example_repsonse_file_q3 = '../use_case_studies/'+fname_out+'/RIAF_Case_Study_q3.md'
                example_repsonse_file_q4 = '../use_case_studies/'+fname_out+'/RIAF_Case_Study_q4.md'


                question1 = "What is the problem this research seeks to address and why is it significant?"
                question2 = "What are the research outputs of this study?"
                question3 = "What impacts has this research delivered to date?"
                question4 = "What impact from this research is expected in the future?"

                questions_and_files = [  
                    (question1, example_repsonse_file_q1, self.list_answers[0]),  
                    (question2, example_repsonse_file_q2, self.list_answers[1]),  
                    (question3, example_repsonse_file_q3, self.list_answers[2]),  
                    (question4, example_repsonse_file_q4, self.list_answers[3])   
                ]  

                logging.info("Reviewing.")
                for i, (question_text, example_response_file, response_text) in enumerate(questions_and_files, start=1):   
                    with open(example_response_file, 'r', encoding='utf-8') as file:  
                        example_response = file.readline().strip()  
                    response = agent_reviewer.review_response(question_text, response_text, example_response)  
                    print(f"Q{i}", response)  
                    logging.info(f"Q{i}")
                    logging.info(response) 

                print("Fully Done. Results in "+ self.outpath)
                logging.info("Fully Done.")
