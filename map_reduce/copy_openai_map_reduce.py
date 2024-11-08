import os
import json
import traceback
from langchain.chat_models.openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.text_splitter import TokenTextSplitter
from langchain.chains.mapreduce import MapReduceChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate
)
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from threading import Lock

# Initialize the OpenAI Chat Model with the model name and API key
chat_model = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    openai_api_key=os.environ.get('OPENAI_API_KEY')
)

if chat_model.openai_api_key is None:
    raise ValueError("Environment variable OPENAI_API_KEY is not set.")

# Configuration for text splitting and processing
text_splitter = TokenTextSplitter(chunk_size=2000, chunk_overlap=10)
write_lock = Lock()

# Define the map and reduce prompts
map_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate(
        prompt=PromptTemplate(
            template="You are an expert threat intelligence analyst.",
            input_variables=[],
        )
    ),
    HumanMessagePromptTemplate(
        prompt=PromptTemplate(
            template="Review the chat transcripts below and write a one paragraph summary focusing on the technologies and industries mentioned and the context of the conversation. Cite specifics from the transcript to support your analysis.\n\n---\n\n{text}\n\n---\n",
            input_variables=["text"],
        )
    ),
])

reduce_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate(
        prompt=PromptTemplate(
            template="You are an expert threat intelligence analyst.",
            input_variables=[],
        )
    ),
    HumanMessagePromptTemplate(
        prompt=PromptTemplate(
            template="Combine the intelligence briefs below into a single intelligence brief. Identify the priority intelligence requirements, the technologies, and sectors the group is targeting, and their tools, tactics, and procedures. If there is not enough context, make a best guess. Use a list to organize the information.\n\n---\n\n{text}\n\n---\n",
            input_variables=["text"],
        )
    ),
])

def summarize(msgs):
    try:
        msgs = [msg.rstrip() for msg in msgs]
        texts = text_splitter.split_text('\n'.join(msgs))
        docs = [Document(page_content=t) for t in texts]
        
        # Define the llm_chain parameters
        llm_chain_object = {
            'llm': chat_model,
            'prompt': map_prompt,
            # Add other properties here if necessary
        }

        # Create the llm_chain by unpacking the dictionary as keyword arguments
        llm_chain = LLMChain(**llm_chain_object)

        # Create the MapReduceChain with the correct llm_chain and prompts
        chain = MapReduceChain(
            llm_chain=llm_chain,
            map_prompt=map_prompt,
            reduce_prompt=reduce_prompt,
            verbose=False
        )
        # Run the chain with the documents and obtain the summary
        summary = chain.run(docs)
    except Exception as e:
        print("An error occurred while summarizing:")
        traceback.print_exc()  # Print stack trace to console
        summary = "not available"
    return summary

# Your file processing function will also be largely the same
def process(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            summary = summarize(lines)
            res = {"uid": file_path, "summary": summary}
            with write_lock:
                with open('out.json', 'a') as outfile:
                    json.dump(res, outfile)
                    outfile.write('\n')
    except Exception as e:
        print(f'Error processing {file_path}:')
        traceback.print_exc()  # Print stack trace to console

# The script start remains unchanged
if __name__ == '__main__':
    # Clear the output file before appending results
    with open('out.json', 'w') as outfile:
        outfile.write("")

    # Ask the user for the filename and then process it
    file_name = input("Enter the name of the file you want to process (e.g., 1mon_parsed_chats.txt): ")
    file_path = os.path.join("test_data", file_name)
    process(file_path)
