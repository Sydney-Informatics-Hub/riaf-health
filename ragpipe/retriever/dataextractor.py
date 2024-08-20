# Extractor class for finding relevant data from tables using LLM

"""
Given filename for table (excel or csv file) and a list of column names, extract relevant rows from the table that are relevant to a topic (search query) using LLM.
Steps:
1. Load the table into a pandas dataframe; automatically detect the type of file (excel or csv) and load it.
2. Load the LLM model: use Llama-index OpenAI's model gpt-4o-mini
3. Batch data in the table (batchsize = 20 by default).
4. Combine for each row the entries in the given column names into a a dict of strings, using column names as keys. 
Also include the row index as a key. Add to a list of dicts for the batch.
5. Use the LLM model to determine which rows are relevant to the search query amd return the relevant row indexes.
6. Return the relevant rows as a pandas dataframe.

"""
import os
import time
import json
import pandas as pd
import logging
import tempfile
from typing import List, Dict, Tuple
from utils.envloader import load_api_key
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage


class DataExtractor:

    def __init__(self, model="gpt-4o-mini", batchsize=10):
        self.batchsize = batchsize
        load_api_key(toml_file_path='secrets.toml')
        self.llm = OpenAI(
            temperature=0,
            model=model,
            max_tokens=10*self.batchsize)  # Increased max_tokens for more detailed responses
        self.llm_service = os.getenv("OPENAI_API_TYPE")

    def system_prompt(self):
        return ("You are an AI assistant tasked with identifying relevant rows in a table. "
                "Given a search query and table data, determine which rows are most relevant to the query.")

    def query_prompt(self, query: str, batch_data: List[Dict[str, str]]) -> str:
        return (f"Given the search query: '{query}', analyze the following table data and return "
                f"the indices of rows that are most relevant to the query. Only return the indices "
                f"as a comma-separated list of numbers.\n\n"
                f"Table data:\n{json.dumps(batch_data, indent=2)}")

    def query(self, query: str, batch_data: List[Dict[str, str]]) -> List[int]:
        messages = [
            ChatMessage(role="system", content=self.system_prompt()),
            ChatMessage(role="user", content=self.query_prompt(query, batch_data)),
        ]
        result = None
        max_try = 0
        while result is None and max_try < 3:
            try:
                response = self.llm.chat(messages)
                result = response.message.content.strip()
                # Parse the comma-separated list of indices
                relevant_indices = [int(idx.strip()) for idx in result.split(',') if idx.strip().isdigit()]
                return relevant_indices
            except Exception as e:
                print(f"LLM not responding: {str(e)}")
                logging.error(f"LLM not responding: {str(e)}")
                max_try += 1
                time.sleep(5)
        return []
    
    def rank_relevant_rows(self, query: str, batch_data: List[Dict[str, str]]) -> List[int]:
        # Order the rows by relevance
        messages = [
            ChatMessage(role="system", content=self.system_prompt()),
            ChatMessage(role="user", content=(
                f"Given the search query: '{query}', analyze the following table data "
                "and return the indices of rows ordered by their relevance to the query, "
                "from most relevant to least relevant. "
                "Only return the indices as a comma-separated list of numbers.\n\n"
                f"Table data:\n{json.dumps(batch_data, indent=2)}"
            )),
        ]
        
        result = None
        max_try = 0
        while result is None and max_try < 3:
            try:
                response = self.llm.chat(messages)
                result = response.message.content.strip()
                # Parse the comma-separated list of indices
                ranked_indices = [int(idx.strip()) for idx in result.split(',') if idx.strip().isdigit()]
                return ranked_indices
            except Exception as e:
                logging.error(f"LLM not responding: {str(e)}")
                max_try += 1
                time.sleep(5)
        return []

    def extract_relevant_data_from_table(self, path_file: str, 
                                         column_names: List[str], 
                                         query: str,
                                         relevance_ranking = True) -> pd.DataFrame:
        """
        Extract relevant rows from a table that are relevant to a search query using LLM.

        :param path_file: str, path to the table file (excel or csv)
        :param column_names: List[str], list of column names to consider
        :param query: str, search query
        :param relevance_ranking: bool, whether to rank the results by relevance
        :return: pd.DataFrame, relevant rows from the table, ordered by relevance if specified
        """
        # Load the table into a pandas dataframe
        if path_file.endswith('.csv'):
            df = pd.read_csv(path_file)
        elif path_file.endswith('.xlsx'):
            df = pd.read_excel(path_file)
        else:
            raise ValueError("File type not supported. Please provide a csv or excel file.")

        # Ensure all specified column names exist in the dataframe
        if not all(col in df.columns for col in column_names):
            raise ValueError("One or more specified column names do not exist in the table.")

        # Batch data in the table
        n_batches = len(df) // self.batchsize
        if len(df) % self.batchsize != 0:
            n_batches += 1

        relevant_rows = []
        for i in range(n_batches):
            start = i * self.batchsize
            end = min((i + 1) * self.batchsize, len(df))
            batch = df.iloc[start:end]
            batch_dict = []
            for index, row in batch.iterrows():
                row_dict = {col: str(row[col]) for col in column_names}
                row_dict['row_index'] = index
                batch_dict.append(row_dict)

            # Use the LLM model to determine which rows are relevant to the search query
            relevant_indices = self.query(query, batch_dict)
            relevant_rows.extend(relevant_indices)

        result = df.iloc[relevant_rows]
        if relevance_ranking:
            print("not ranked results:")
            print(result)
            # Rank and order the relevant rows in results by relevance
            res_dict = []
            for index, row in result.iterrows():
                row_dict = {col: str(row[col]) for col in column_names}
                row_dict['row_index'] = index
                res_dict.append(row_dict)

            ranked_indices = self.rank_relevant_rows(query, res_dict)
            result = result.loc[ranked_indices]

        # Return the relevant rows as a pandas dataframe, ordered by relevance if ranking was applied
        return result
    


    def extract_score_data_from_table(self, path_file: str, 
                                         column_names: List[str], 
                                         query: str) -> pd.DataFrame:
        """
        Extract relevant rows for a table that are relevant to a search query using LLM and provide relevance scores.

        :param path_file: str, path to the table file (excel or csv)
        :param column_names: List[str], list of column names to consider
        :param query: str, search query
        :return: pd.DataFrame, relevant rows from the table with relevance scores
        """
        # Load the table into a pandas dataframe
        if path_file.endswith('.csv'):
            df = pd.read_csv(path_file)
        elif path_file.endswith('.xlsx'):
            df = pd.read_excel(path_file)
        else:
            raise ValueError("File type not supported. Please provide a csv or excel file.")

        # Ensure all specified column names exist in the dataframe
        if not all(col in df.columns for col in column_names):
            raise ValueError("One or more specified column names do not exist in the table.")

        # Batch data in the table
        n_batches = len(df) // self.batchsize
        if len(df) % self.batchsize != 0:
            n_batches += 1

        relevant_rows = []
        relevance_scores = []

        for i in range(n_batches):
            start = i * self.batchsize
            end = min((i + 1) * self.batchsize, len(df))
            batch = df.iloc[start:end]
            batch_dict = []
            for index, row in batch.iterrows():
                row_dict = {col: str(row[col]) for col in column_names}
                row_dict['row_index'] = index
                batch_dict.append(row_dict)

            # Use the LLM model to determine which rows are relevant to the search query and their scores
            relevant_indices, scores = self.query_with_scores(query, batch_dict)
            print(f"relevant_indices: {relevant_indices}, scores: {scores}")
            relevant_rows.extend(relevant_indices)
            relevance_scores.extend(scores)

        result = df.iloc[relevant_rows].copy()
        result['relevance_score'] = relevance_scores

        return result.sort_values('relevance_score', ascending=False)

    def query_with_scores(self, query: str, batch_data: List[Dict[str, str]]) -> Tuple[List[int], List[float]]:
        messages = [
            ChatMessage(role="system", content=self.system_prompt_with_scores()),
            ChatMessage(role="user", content=self.query_prompt_with_scores(query, batch_data)),
        ]
        result = None
        max_try = 0
        while result is None and max_try < 3:
            try:
                response = self.llm.chat(messages)
                result = response.message.content.strip()
                print(f"LLM result: {result}")
                # Parse the response to get indices and scores
                lines = result.split('\n')
                relevant_indices = []
                scores = []
                for line in lines:
                    if ':' in line:
                        idx, score = line.split(':')
                        relevant_indices.append(int(idx.strip()))
                        scores.append(float(score.strip()))
                return relevant_indices, scores
            except Exception as e:
                logging.error(f"LLM not responding: {str(e)}")
                max_try += 1
                time.sleep(3)
        return [], []

    def system_prompt_with_scores(self):
        return ("You are an AI assistant tasked with identifying relevant rows in a table and scoring their relevance. "
                "Given a search query and table data, determine which rows are most relevant to the query and assign a relevance score between 0 and 1 for each relevant row.")

    def query_prompt_with_scores(self, query: str, batch_data: List[Dict[str, str]]) -> str:
        return (f"Given the search query: '{query}', analyze the following table data and return "
                f"the indices of rows that are most relevant to the query along with their relevance scores. "
                f"Return the results in the format 'index: score' (one per line), where the score is between 0 and 1.\n\n "
                #f"Only include rows with a relevance score greater than 0.5.\n\n"
                f"Table data:\n{json.dumps(batch_data, indent=2)}")
    

### test functions

def test_dataextractor():
    """
    Test function for the DataExtractor class.
    """

    # Create a temporary CSV file for testing
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_file:
        temp_file.write("id,title,content\n")
        temp_file.write("1,AI in Healthcare,Artificial Intelligence is revolutionizing healthcare.\n")
        temp_file.write("2,Climate Change,Global warming is a pressing issue.\n")
        temp_file.write("3,Space Exploration,NASA plans new missions to Mars.\n")
        temp_filename = temp_file.name

    try:
        # Initialize DataExtractor
        extractor = DataExtractor(batchsize=2)

        # Test extract_relevant_data_from_table method
        result = extractor.extract_relevant_data_from_table(
            temp_filename,
            ['title', 'content'],
            "AI applications in healthcare",
            relevance_ranking=True
        )

        # Check if the result is a DataFrame
        assert isinstance(result, pd.DataFrame), "Result should be a pandas DataFrame"

        # Check if the relevant row was extracted
        assert len(result) == 1, "Expected 1 relevant row"
        assert result.iloc[0]['title'] == "AI in Healthcare", "Expected to extract the AI in Healthcare row"

        print("DataExtractor test passed successfully!")

    finally:
        # Clean up: remove the temporary file
        os.unlink(temp_filename)


def test_on_file():
    """
    Test function for the DataExtractor class using a sample file.
    """
    # Initialize DataExtractor
    extractor = DataExtractor()

    topic = "Elastagan is a flexible, elastic material designed for medical applications,\
        offering durability and comfort in wound care and surgical products."
    
    filename = "templates/data/Australia-Burden-of-Disease-Catalogue_2023.xlsx"
    column_names = ['category', 'disease']

    # Test extract_relevant_data_from_table method
    result = extractor.extract_relevant_data_from_table(
        filename,
        column_names,
        topic,
        relevance_ranking = True
    )

    # Check if the result is a DataFrame
    assert isinstance(result, pd.DataFrame), "Result should be a pandas DataFrame"

    # Check if the relevant row was extracted
    assert len(result) == 1, "Expected 1 relevant row"
    assert result.iloc[0]['title'] == "AI in Healthcare", "Expected to extract the AI in Healthcare row"

    print("DataExtractor test on file passed successfully!")


def test_dataextractor_score():
    """
    Test function for the DataExtractor class.
    """

    # Create a temporary CSV file for testing
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_file:
        temp_file.write("id,title,content\n")
        temp_file.write("1,AI in Healthcare,Artificial Intelligence is revolutionizing healthcare.\n")
        temp_file.write("2,Climate Change,Global warming is a pressing issue.\n")
        temp_file.write("3,Space Exploration,NASA plans new missions to Mars.\n")
        temp_filename = temp_file.name

    try:
        # Initialize DataExtractor
        extractor = DataExtractor(batchsize=2)

        # Test extract_relevant_data_from_table method
        result = extractor.extract_score_data_from_table(
            temp_filename,
            ['title', 'content'],
            "AI applications in healthcare"
        )

        # Check if the result is a DataFrame
        assert isinstance(result, pd.DataFrame), "Result should be a pandas DataFrame"

        # Check if the relevant row was extracted
        assert len(result) == 1, "Expected 1 relevant row"
        assert result.iloc[0]['title'] == "AI in Healthcare", "Expected to extract the AI in Healthcare row"

        print("DataExtractor test passed successfully!")

    finally:
        # Clean up: remove the temporary file
        os.unlink(temp_filename)


def test_scores_on_file():
    """
    Test function for the DataExtractor class using a sample file.
    """
    # Initialize DataExtractor
    extractor = DataExtractor()

    topic = "Elastagan is a flexible, elastic material designed for medical applications,\
        offering durability and comfort in wound care and surgical products."
    
    filename = "templates/data/Australia-Burden-of-Disease-Catalogue_2023.xlsx"
    column_names = ['category', 'disease']

    # Test extract_relevant_data_from_table method
    result = extractor.extract_score_data_from_table(
        filename,
        column_names,
        topic
    )

    # Check if the result is a DataFrame
    assert isinstance(result, pd.DataFrame), "Result should be a pandas DataFrame"

    # Check if the relevant row was extracted
    assert len(result) == 1, "Expected 1 relevant row"
    assert result.iloc[0]['title'] == "AI in Healthcare", "Expected to extract the AI in Healthcare row"

    print("DataExtractor test on file passed successfully!")
