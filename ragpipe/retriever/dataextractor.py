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
import pandas as pd
import logging
from typing import List
from utils.envloader import load_api_key
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage


class DataExtractor:

    def __init__(self, model="gpt-4o-mini"):
        load_api_key(toml_file_path='secrets.toml')
        self.llm = OpenAI(
            temperature=0,
            model=model,
            max_tokens=512)  # Increased max_tokens for more detailed responses
        self.llm_service = os.getenv("OPENAI_API_TYPE")

    def system_prompt(self):
        return ("You are an AI assistant tasked with identifying relevant rows in a table. "
                "Given a search query and table data, determine which rows are most relevant to the query.")

    def query_prompt(self, query: str, batch_data: List[Dict[str, str]]) -> str:
        return (f"Given the search query: '{query}', analyze the following table data and return "
                f"the indices of rows that are most relevant to the query. Only return the indices "
                f"as a comma-separated list of numbers.\n\nTable data:\n{json.dumps(batch_data, indent=2)}")

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
                logging.error(f"LLM not responding: {str(e)}")
                max_try += 1
                time.sleep(5)
        return []

    def extract_relevant_data_from_table(self, path_file: str, 
                                         column_names: List[str], 
                                         query: str, batchsize: int = 20) -> pd.DataFrame:
        """
        Extract relevant rows from a table that are relevant to a search query using LLM.

        :param path_file: str, path to the table file (excel or csv)
        :param column_names: List[str], list of column names to consider
        :param query: str, search query
        :param batchsize: int, batch size for processing the table
        :return: pd.DataFrame, relevant rows from the table
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
        n_batches = len(df) // batchsize
        if len(df) % batchsize != 0:
            n_batches += 1

        relevant_rows = []
        for i in range(n_batches):
            start = i * batchsize
            end = min((i + 1) * batchsize, len(df))
            batch = df.iloc[start:end]
            batch_dict = []
            for index, row in batch.iterrows():
                row_dict = {col: str(row[col]) for col in column_names}
                row_dict['row_index'] = index
                batch_dict.append(row_dict)

            # Use the LLM model to determine which rows are relevant to the search query
            relevant_indices = self.query(query, batch_dict)
            relevant_rows.extend(relevant_indices)

        # Return the relevant rows as a pandas dataframe
        return df.iloc[relevant_rows]
