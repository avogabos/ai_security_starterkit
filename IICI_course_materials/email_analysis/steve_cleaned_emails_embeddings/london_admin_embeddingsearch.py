import openai
import pandas as pd
import os
import numpy as np
from scipy.spatial.distance import cdist
import ast

# Fetch the API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

path_to_emails_dir = '/Users/gabe/code/ai_tools/email_spool/mailboxes/mail_dir/formationshouse/formations_embeddings/LondonAdmin_cleaned_emails'

# Load the embeddings dataframe
df = pd.read_csv('consistent_embeddings.csv')

# Convert embeddings from string representations of lists to numpy arrays
df['embedding'] = df['embedding'].apply(ast.literal_eval).apply(np.array)

# Constants
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-4"

def query_to_embedding(query):
    response = openai.Embedding.create(model=EMBEDDING_MODEL, input=query)
    return response['data'][0]['embedding']

def find_most_similar_documents(query_embedding, n=5):
    # First, ensure that embeddings are 2D by removing any unnecessary dimensions
    df['embedding'] = df['embedding'].apply(lambda emb: np.squeeze(emb))

    # Now stack the embeddings
    stacked_embeddings = np.vstack(df['embedding'].values)
    
    print(f"Corrected shape of the stacked embeddings: {stacked_embeddings.shape}")
    
    # Now the stacked_embeddings should be a 2D array (4206, 1536), ready to be used with cdist
    distances = cdist([query_embedding], stacked_embeddings, 'cosine')[0]
    df['similarity'] = 1 - distances  # Convert distance to similarity
    
    # Return the top `n` most similar documents
    return df.nlargest(n, 'similarity')

def gpt_answer(document_content, user_query):
    prompt = [
        {"role": "system", "content": "You are a helpful assistant. Answer the following question based on the provided document content."},
        {"role": "user", "content": document_content},
        {"role": "user", "content": user_query}
    ]
    response = openai.ChatCompletion.create(model=GPT_MODEL, messages=prompt)
    return response['choices'][0]['message']['content'].strip()

def main():
    user_query = input("Enter your query: ")
    query_embedding = query_to_embedding(user_query)
    top_docs = find_most_similar_documents(query_embedding, n=20)  # Change here for more documents

    print("Fetching the custom prompt for document analysis...")
    with open('summarize.md', 'r') as md_file:
        custom_prompt_template = md_file.read()

    print("Top relevant documents and similarity scores:")
    summarization_responses = []
    for index, row in top_docs.iterrows():
        print(f"Document: {row['file']}, Score: {row['similarity']}")
        top_doc_relative_path = row['file'].strip().replace('./', '')
        path_to_file = os.path.join(path_to_emails_dir, os.path.basename(top_doc_relative_path))

        try:
            with open(path_to_file, 'r') as file:
                document_content = file.read()
                prompt = custom_prompt_template.replace('<<document_content>>', document_content)
                print(f"Analyzing document: {path_to_file}")
                answer = gpt_answer(prompt, user_query)
                summarization_responses.append(answer)
        except FileNotFoundError:
            print(f"The file {path_to_file} does not exist.")

    print("Writing summarizations to file...")
    with open('summarization.txt', 'w') as summary_file:
        for response in summarization_responses:
            summary_file.write(response + "\n\n")

    print("Reading summarizations for final analysis...")
    with open('summarization.txt', 'r') as summary_file:
        summarization_content = summary_file.read()

    final_prompt = f"{user_query}\nUse the following summarization of emails obtained from our dataset to answer this question:\n{summarization_content}"
    print("Sending final analysis to the GPT-4 model...")
    final_response = gpt_answer(final_prompt, user_query)
    
    print("\nGPT-4 Response:")
    print(final_response)

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
