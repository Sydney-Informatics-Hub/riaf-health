# test for Langfuse observability platform
# if cloud hosted, traces, logs, metrics, and events are available on https://cloud.langfuse.com/
# How to setup evaluation  metrics: https://docs-staging.langfuse.com/docs/scores/overview

from llama_index.core import Settings
from llama_index.core.callbacks import CallbackManager
from langfuse.llama_index import LlamaIndexCallbackHandler
import os
import sys
from llama_index.core import SimpleDirectoryReader
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex

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

langfuse_callback_handler = LlamaIndexCallbackHandler(
  secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
  public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
  host="https://cloud.langfuse.com"
)

Settings.callback_manager = CallbackManager([langfuse_callback_handler]) 

documents = SimpleDirectoryReader(input_dir="../test_data/documents_to_add").load_data()
 
index = VectorStoreIndex.from_documents(documents)

model = OpenAI(model = LLM_MODEL)

response = index.as_query_engine(llm = model).query("What are the research priorities in health for Australia? Include references")
print(response)
response = index.as_query_engine().query("What does RIAF stand for? Provide references")
print(response)

langfuse_callback_handler.flush()