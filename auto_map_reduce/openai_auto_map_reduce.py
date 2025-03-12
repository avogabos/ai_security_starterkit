import os
import json
import gzip
import zstandard as zstd
import base64
import file_evaluation
import re
import openai
from langchain import LLMChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.mapreduce import MapReduceChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from threading import Lock
from langchain.text_splitter import TokenTextSplitter
from langchain.prompts.chat import (ChatPromptTemplate,
                                    HumanMessagePromptTemplate,
                                    SystemMessagePromptTemplate)

# Execute the main function from file_evaluation.py to get the dynamically generated prompts and carry over the file name
dynamic_prompts, filename = file_evaluation.main()

# Verify that dynamic_prompts is a string if it is not, thats a significant problem make sure to check the output from file_evaluation.py!
if not isinstance(dynamic_prompts, str):
    raise ValueError("The returned dynamic prompts are not in string format.")

# Extract map_prompt and reduce_prompt from dynamic_prompts using a parser - if you mess around with this and it breaks thats on you.

map_match = re.search(r"(map_prompt = ChatPromptTemplate.from_messages\(.*?\n\))", dynamic_prompts, re.DOTALL)
reduce_match = re.search(r"(reduce_prompt = ChatPromptTemplate.from_messages\(.*?\n\))", dynamic_prompts, re.DOTALL)

if map_match and reduce_match:
    map_prompt_code = map_match.group(1)
    reduce_prompt_code = reduce_match.group(1)
    
    # Execute the code to define map_prompt and reduce_prompt - executing arbitrary code is generally frowned upon, make sure you have sanitized your inputs!
    exec(map_prompt_code)
    exec(reduce_prompt_code)
else:
    raise ValueError("Could not extract map_prompt and reduce_prompt from dynamic response.")

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("Environment variable OPENAI_API_KEY is not set.")

# You can use GPT-3.5-turbo or other models for this if you prefer
gpt4 = ChatOpenAI(
    model_name="gpt-4",
    openai_api_key=OPENAI_API_KEY,
)

text_splitter = TokenTextSplitter(chunk_size=2000,chunk_overlap=10)

write_lock = Lock()

def summarize(msgs):
    try:
        print("Starting the summarization process...")
        msgs = [msg.rstrip() for msg in msgs]
        print("Splitting text into manageable chunks...")
        texts = text_splitter.split_text('\n'.join(msgs))
        print(f"Total chunks created: {len(texts)}")
        docs = [Document(page_content=t) for t in texts]
        print("Loading summarization chain...")
        chain = load_summarize_chain(gpt4, chain_type="map_reduce", verbose=False, map_prompt=map_prompt, combine_prompt=reduce_prompt)
        print("Running summarization chain...")
        summary = chain.run(docs)
        print("Summarization completed.")
    except Exception as e: 
        print(e)
        summary = "not available"
    return summary

def process(file_path):
    try:
        print(f"Reading and processing file: {file_path}")
        with open(file_path, 'r') as file:
            lines = file.readlines()
            print("Running summarization...")
            summary = summarize(lines) 
            res = {"uid": file_path, "summary": summary}
            print("Writing results to output file...")
            with write_lock:
                with open('out.json', 'a') as outfile:
                    outfile.write(json.dumps(res) + '\n')
            print(f"Results for {file_path} written to output file.")
    except Exception as e:
        print(f'Error reading {file_path}: {e}')

# Clear the output file before appending results
with open('out.json', 'w') as outfile:
    outfile.write("")

# Catch the filename and process it
file_path = filename
process(file_path)
