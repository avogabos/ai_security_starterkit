import pandas as pd
import numpy as np
from ast import literal_eval
from collections import Counter

# Load your embeddings dataframe
df = pd.read_csv('embeddings.csv')

# Convert the embeddings from strings to numpy arrays
df['embedding_np'] = df['embedding'].apply(lambda x: np.array(literal_eval(x)))

# Calculate lengths of each embedding
embedding_lengths = df['embedding_np'].apply(len)

# Determine the most common length
length_counts = Counter(embedding_lengths)
most_common_length = length_counts.most_common(1)[0][0]

# Filter out inconsistent embeddings
consistent_embeddings_df = df[embedding_lengths == most_common_length]

# Save the consistent embeddings to a new CSV for future use
consistent_embeddings_df.to_csv('consistent_embeddings.csv', index=False)

# Print out diagnostics
print(f"Unique lengths of embeddings: {embedding_lengths.unique()}")
print(f"Number of consistent embeddings: {consistent_embeddings_df.shape[0]}")
print(f"Number of inconsistent embeddings: {df.shape[0] - consistent_embeddings_df.shape[0]}")
print(f"Consistent embeddings saved to 'consistent_embeddings.csv'")
