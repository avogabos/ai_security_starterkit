import anthropic
import pandas as pd
from scipy import spatial
import os
import ast

# Initialize the Anthropic client
client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Load the embeddings dataframe
df = pd.read_csv('embedded_chats_json.csv')
df['embedding'] = df['embedding'].apply(ast.literal_eval)

# Constants
EMBEDDING_MODEL = "claude-2"  # Adjust as needed for your specific use-case
GPT_MODEL = "claude-2"       # Adjust as needed

def query_to_embedding(query):
    # TODO: This function needs to be adapted according to how you'd embed using Anthropics.
    # Example assumes embeddings can be obtained similarly to completions.
    prompt = f"\n\nHuman: {query}\n\nAssistant:"
    response = client.completions.create(
        model=EMBEDDING_MODEL, 
        prompt=prompt
    )
    return response.completion  # You may need to extract the embedding differently

def get_most_similar_chats(query_embedding, n=5):
    # Use cosine similarity to get the similarity scores
    df['similarity'] = df['embedding'].apply(lambda x: 1 - spatial.distance.cosine(x, query_embedding))
    
    # Return the top `n` chats
    return df.nlargest(n, 'similarity')

def gpt_answer(query, top_chat_message):
    prompt = f"\n\nHuman: Based on the chat message: '{top_chat_message}', {query}\n\nAssistant:"
    response = client.completions.create(
        model=GPT_MODEL,
        prompt=prompt
    )
    return response.completion.strip()

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
