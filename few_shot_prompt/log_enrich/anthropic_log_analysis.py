import os
import json
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

# Read the Anthropic API key from environment variable
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
if not anthropic_api_key:
    raise ValueError("Please set the ANTHROPIC_API_KEY environment variable.")

# Initialize the Anthropic API client
anthropic = Anthropic(api_key=anthropic_api_key)

def get_document_content(filename):
    """Read the content of the markdown document."""
    with open(filename, 'r') as file:
        return file.read()

def get_log_data_from_file(file_path):
    """Read the content of the log data file specified by the user."""
    with open(file_path, 'r') as file:
        return file.read()

def get_response_from_anthropic(prompt, document):
    """
    Use the Anthropic API to quickly evaluate our few-shot prompt approach
    """
    combined_prompt = f"{HUMAN_PROMPT} {document} {AI_PROMPT} {prompt}"
    
    completion = anthropic.completions.create(
        model="claude-2",
        max_tokens_to_sample=2700,
        prompt=combined_prompt
    )
    
    return completion.completion.strip()

def save_response_as_json(response, csv_filename):
    # Extract the name of the CSV file without its extension
    base_name = os.path.basename(csv_filename).split('.')[0]
    json_filename = f"anthropic_analysis_{base_name}.json"
    
    with open(json_filename, 'w') as json_file:
        json.dump({"response": response}, json_file, indent=4)

def main():
    document = get_document_content('anthropic_command_line_analysis_fs.md')
    user_file_path = input("Enter the path to your log data file (or press enter for default 'sample_data_logs.csv'): ")
    if not user_file_path.strip():  # Check if user pressed enter without input
        user_file_path = 'sample_data_logs.csv'
    log_data = get_log_data_from_file(user_file_path)
    
    response = get_response_from_anthropic(log_data, document)
    print("\nResponse from Anthropic:\n", response)
    save_response_as_json(response, user_file_path)

if __name__ == "__main__":
    main()
