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
            max_tokens=3)
        self.llm_service = os.getenv("OPENAI_API_TYPE")
        self.llm = OpenAI(model=model)

    def system_prompt(self):
        pass

    def query_prompt(self):
        pass

    def query(self, query):
        messages = [
            ChatMessage(role="system", content=self.system_prompt),
            ChatMessage(role="user", content=self.query_prompt),
        ]
        result = None
        max_try = 0
        while result is None and max_try < 3:
            try:
                response = self.llm.chat(messages)
                result = response.message.content.strip().lower()
            except:
                logging.error(f"LLM not responding")
                max_try += 1
                # sleep for 5 seconds to avoid rate limit
                time.sleep(5)

        return result

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

        # Load the LLM model
        llm = OpenAI(model="gpt-4o-mini")

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
                # pass

            # Use the LLM model to determine which rows are relevant to the search query
            relevant_indices = llm.query(query, batch_dict)
            relevant_rows.extend(relevant_indices)

        # Return the relevant rows as a pandas dataframe
        return df.iloc[relevant_rows]