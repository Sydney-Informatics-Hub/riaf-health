""" test for Langfuse observability platform
 if cloud hosted, traces, logs, metrics, and events are available on https://cloud.langfuse.com/
 How to setup evaluation  metrics: https://docs-staging.langfuse.com/docs/scores/overview
 How to integrate with LLama-index: https://langfuse.com/docs/integrations/llama-index/get-started
 with decorators: https://langfuse.com/docs/sdk/python/decorators
 """

from llama_index.core import Settings
from llama_index.core.callbacks import CallbackManager
from langfuse.llama_index import LlamaIndexCallbackHandler
from langfuse.decorators import langfuse_context, observe
import os
import sys
from llama_index.core import SimpleDirectoryReader
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex
import time
# local imports
from utils.envloader import load_api_key

# read secrets.toml file
load_api_key(toml_file_path='secrets.toml')

LLM_MODEL = "gpt-4o"

if 'LANGFUSE_SECRET_KEY' not in os.environ or 'LANGFUSE_PUBLIC_KEY' not in os.environ:
    print("LANGFUSE_SECRET_KEY and LANGFUSE_PUBLIC_KEY environment variables must be set.")
    sys.exit(1)
if 'OPENAI_API_KEY' not in os.environ:
    print("OPENAI_API_KEY environment variable must be set.")
    sys.exit(1)


def test1(with_langfuse = True):

  start_time = time.time()

  if with_langfuse:
    langfuse_callback_handler = LlamaIndexCallbackHandler(
    secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
    public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
    host="https://cloud.langfuse.com"
    )
    Settings.callback_manager = CallbackManager([langfuse_callback_handler]) 

  documents = SimpleDirectoryReader(input_dir="../test_data/documents_to_add").load_data()
  
  index = VectorStoreIndex.from_documents(documents)

  model = OpenAI(model = LLM_MODEL)

  query_engine = index.as_query_engine(llm = model)

  response = query_engine.query("What are the research priorities in health for Australia? Include references")
  print(response)
  response = query_engine.query("What does RIAF stand for? Provide references")
  print(response)

  if with_langfuse:
    langfuse_callback_handler.flush()

  print(f"Time taken: {round(time.time() - start_time, 2)} seconds")


@observe()
def langfuse_genengine():
  # Set callback manager for LlamaIndex, will apply to all LlamaIndex executions in this function
  langfuse_handler = langfuse_context.get_current_llama_index_handler()
  Settings.callback_manager = CallbackManager([langfuse_handler])

  # Run application
  documents = SimpleDirectoryReader(input_dir="../test_data/documents_to_add").load_data()
  index = VectorStoreIndex.from_documents(documents)
  model = OpenAI(model = LLM_MODEL)
  query_engine = index.as_query_engine(llm = model)
  return query_engine

@observe()
def langfuse_query(question, query_engine):
  langfuse_handler = langfuse_context.get_current_llama_index_handler()
  Settings.callback_manager = CallbackManager([langfuse_handler])
  response = query_engine.query(question)
  return response


@observe()
def langfuse_fn(question):
  langfuse_handler = langfuse_context.get_current_llama_index_handler()
  Settings.callback_manager = CallbackManager([langfuse_handler])
  documents = SimpleDirectoryReader(input_dir="../test_data/documents_to_add").load_data()
  index = VectorStoreIndex.from_documents(documents)
  model = OpenAI(model = LLM_MODEL)
  query_engine = index.as_query_engine(llm = model)
  response = query_engine.query(question)
  return response

def test2():

  start_time = time.time()
  
  query_engine = langfuse_genengine()
  #response = langfuse_query("What are the research priorities in health for Australia? Include references", query_engine)
  #print(response)

  #response2 = query_engine.query("What does RIAF stand for? Provide references")
  #print(response2)  

  response = langfuse_fn("What are the research priorities in health for Australia? Include references")
  print(response)

  langfuse_context.flush()
  print(f"Time taken: {round(time.time() - start_time, 2)} seconds")
  