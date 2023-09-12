import openai
import pandas as pd
from scipy import spatial
import os
import ast

# Fetch the API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

# Load the embeddings dataframe
df = pd.read_csv('embedded_chats_json.csv')
df['embedding'] = df['embedding'].apply(ast.literal_eval)

# Constants
EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-4"

def query_to_embedding(query):
    response = openai.Embedding.create(model=EMBEDDING_MODEL, input=[query])
    return response["data"][0]["embedding"]

def get_most_similar_chats(query_embedding, n=5):
    # Use cosine similarity to get the similarity scores
    df['similarity'] = df['embedding'].apply(lambda x: 1 - spatial.distance.cosine(x, query_embedding))
    
    # Return the top `n` chats
    return df.nlargest(n, 'similarity')

def gpt_answer(query, top_chat_message):
    prompt = [
        {"role": "system", "content": "You are an expert intelligence analyst, please assess the following text and provide your analysis in line with the question."},
        {"role": "user", "content": f"Based on the chat message: '{top_chat_message}', {query}"}
    ]
    response = openai.ChatCompletion.create(model=GPT_MODEL, messages=prompt)
    return response.choices[0].message['content'].strip()


def main():
    user_query = input("Enter your query: ")
    query_embedding = query_to_embedding(user_query)
    top_chats = get_most_similar_chats(query_embedding)
    print("Top relevant chat chunks:")
    print(top_chats['chunk'])
    
    # Fetching the answer using GPT and the top relevant chat message
    answer = gpt_answer(user_query, top_chats['chunk'].iloc[0])
    print("\nAnswer based on the most relevant chat chunk:")
    print(answer)

if __name__ == "__main__":
    main()