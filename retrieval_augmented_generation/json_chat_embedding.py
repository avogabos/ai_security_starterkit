import openai
from transformers import GPT2Tokenizer
import pandas as pd
import os
import json
import time

# Initialize the tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2-medium")

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Constants
TOKEN_LIMIT = 8000  # a bit below the 8191 limit to account for uncertainties
OVERLAP = 25
EMBEDDING_MODEL = "text-embedding-ada-002"
RATE_LIMIT_TPM = 950000  # Set a bit below the 1,000,000 limit to be safe
current_tpm = 0  # Track tokens per minute
last_request_time = time.time()  # Track the last request time

# Load and parse the JSON data
with open("combined.json", "r", encoding="utf-8") as file:
    json_data = json.load(file)

combined_chats = []
for entry in json_data:
    chat = f"{entry['ts']} {entry['from']} {entry['to']} {entry['body']}"
    combined_chats.append(chat)

# Convert chats to chunks based on tokens!
text = " ".join(combined_chats)
tokens = tokenizer.tokenize(text)
token_ids = tokenizer.convert_tokens_to_ids(tokens)  # Convert tokens to their numerical IDs

chunks = []
idx = 0
while idx < len(token_ids):
    end_idx = idx + TOKEN_LIMIT
    if end_idx > len(token_ids):
        end_idx = len(token_ids)
    chunk = tokenizer.decode(token_ids[idx:end_idx])  # Decode numerical IDs to text
    chunks.append(chunk)
    idx += TOKEN_LIMIT - OVERLAP


# Calculate embeddings
BATCH_SIZE = 5  # Reduce if needed based on the size of the chunks and rate limits

embeddings = []
for batch_start in range(0, len(chunks), BATCH_SIZE):
    batch_end = batch_start + BATCH_SIZE
    batch = chunks[batch_start:batch_end]

    # Estimate the tokens in the current batch
    current_batch_tokens = sum([len(tokenizer.tokenize(chunk)) for chunk in batch])
    current_tpm += current_batch_tokens

    # If close to the rate limit, sleep until the start of the next minute
    if time.time() - last_request_time < 60 and current_tpm >= RATE_LIMIT_TPM:
        sleep_time = 60 - (time.time() - last_request_time)
        print(f"Approaching rate limit. Sleeping for {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)
        current_tpm = 0  # Reset after the wait

    try:
        print(f"Embedding batch {batch_start} to {batch_end-1}")
        response = openai.Embedding.create(model=EMBEDDING_MODEL, input=batch)
        for i, be in enumerate(response["data"]):
            assert i == be["index"]
        batch_embeddings = [e["embedding"] for e in response["data"]]
        embeddings.extend(batch_embeddings)
    except openai.error.RateLimitError:  # Catch rate limit errors
        print("Rate limit error encountered. Waiting for 60 seconds...")
        time.sleep(60)
        batch_start -= BATCH_SIZE  # Retry the batch after waiting
    finally:
        last_request_time = time.time()  # Update the last request time

# Create and save a dataframe
df = pd.DataFrame({
    'chunk': chunks,
    'embedding': embeddings
})

df.to_csv('embedded_chats_json.csv', index=False)

print("Embedding completed and saved to embedded_chats_json.csv!")
