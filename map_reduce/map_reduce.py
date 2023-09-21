import os
import json
import gzip
import zstandard as zstd
import base64
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

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("Environment variable OPENAI_API_KEY is not set.")

gpt4 = ChatOpenAI(
    model_name="gpt-4",
    openai_api_key=OPENAI_API_KEY,
)

text_splitter = TokenTextSplitter(chunk_size=2000,chunk_overlap=10)

write_lock = Lock()

# A prompt used to combine separate summaries into one cohesive summary
map_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                template="You are an expert threat intelligence analyst.",
                input_variables=[],
            )
        ),
        HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                template="As a threat intelligence analyst, review the chat transcripts below and write a one paragraph summary. Focus on the technologies and industries mentioned and context of the conversation. Cite specifics from the transcript to support your analysis.\n\n---\n\n {text} \n\n---\n",
                input_variables=["text"],
            )
        ),
    ]
)

reduce_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                template="You are an expert threat intelligence analyst.",
                input_variables=[],
            )
        ),
        HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                template="Combine the intelligence briefs below into a single intelligence brief. Identify the priority intelligence requirements, the technologies, and sectors the group is targeting, and their tools, tactics, and procedures. If there is not enough context, make a best guess. use a list to organize the information.\n\n---\n\n {text} \n\n---\n",
                input_variables=["text"],
            )
        ),
    ]
)

def summarize(msgs):
    try:
        msgs = [msg.rstrip() for msg in msgs]
        texts = text_splitter.split_text('\n'.join(msgs))
        docs = [Document(page_content=t) for t in texts]
        chain = load_summarize_chain(gpt4, chain_type="map_reduce", verbose=False, map_prompt=map_prompt, combine_prompt=reduce_prompt)
        summary = chain.run(docs)
    except Exception as e: 
        print(e)
        summary = "not available"
    return summary


def process(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            summary = summarize(lines) 
            res = {"uid": file_path, "summary": summary}  
            with write_lock:
                with open('out.json', 'a') as outfile:
                    outfile.write(json.dumps(res) + '\n') 
    except Exception as e:
        print(f'Error reading {file_path}: {e}')

# Clear the output file before appending results
with open('out.json', 'w') as outfile:
    outfile.write("")

# Ask the user for the filename and then process it
file_name = input("Enter the name of the file you want to process (e.g., 1mon_parsed_chats.txt): ")
file_path = os.path.join("test_data", file_name)
process(file_path)