from transformers import GPT2Tokenizer
import pandas as pd
import os
import json
import time
import anthropic

# Initialize the tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2-medium")

# Initialize the Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Constants
TOKEN_LIMIT = 8000
OVERLAP = 25
RATE_LIMIT_TPM = 950000
current_tpm = 0
last_request_time = time.time()

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
token_ids = tokenizer.convert_tokens_to_ids(tokens)

chunks = []
idx = 0
while idx < len(token_ids):
    end_idx = idx + TOKEN_LIMIT
    if end_idx > len(token_ids):
        end_idx = len(token_ids)
    chunk = tokenizer.decode(token_ids[idx:end_idx])
    chunks.append(chunk)
    idx += TOKEN_LIMIT - OVERLAP

# Calculate embeddings
BATCH_SIZE = 5

embeddings = []

for batch_start in range(0, len(chunks), BATCH_SIZE):
    batch_end = batch_start + BATCH_SIZE
    batch = chunks[batch_start:batch_end]

    current_batch_tokens = sum([len(tokenizer.tokenize(chunk)) for chunk in batch])
    current_tpm += current_batch_tokens

    if time.time() - last_request_time < 60 and current_tpm >= RATE_LIMIT_TPM:
        sleep_time = 60 - (time.time() - last_request_time)
        print(f"Approaching rate limit. Sleeping for {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)
        current_tpm = 0

    try:
        print(f"Embedding batch {batch_start} to {batch_end-1}")

        for chunk in batch:
            # Adding "\n\nHuman:" to the beginning and "\n\nAssistant:" to the end
            chunk_with_human_prefix = f"\n\nHuman: {chunk}\n\nAssistant:"
            response = client.completions.create(
                model="claude-2",  # Replace with appropriate embedding model
                max_tokens_to_sample=300,  # Adjust based on needs
                prompt=chunk_with_human_prefix  # Updated chunk
            )
            embeddings.append(response.completion)

    except anthropic.RateLimitError as e:  # Catch rate limit errors
        print("Rate limit error encountered. Waiting for 60 seconds...")
        time.sleep(60)
        batch_start -= BATCH_SIZE  # Retry this batch after waiting
    finally:
        last_request_time = time.time()

# Create and save a DataFrame only if the lengths are the same
if len(chunks) == len(embeddings):
    df = pd.DataFrame({
        'chunk': chunks,
        'embedding': embeddings
    })
    df.to_csv('embedded_chats_json.csv', index=False)
    print("Embedding completed and saved to embedded_chats_json.csv!")
else:
    print("Lengths of chunks and embeddings do not match.")
