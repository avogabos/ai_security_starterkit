import os
import json
from openai import OpenAI

# Instantiate the client. The API key will be read from the environment variable OPENAI_API_KEY
client = OpenAI()

def get_document_content(filename):
    """Read the content of the markdown document."""
    with open(filename, 'r') as file:
        return file.read()

def get_log_data_from_file(file_path):
    """Read the content of the log data file specified by the user."""
    with open(file_path, 'r') as file:
        return file.read()

def get_response_from_openai(prompt, document):
    """
    Use the OpenAI API to quickly evaluate our few shot prompt approach
    """
    messages = [
        {"role": "system", "content": document},
        {"role": "user", "content": prompt}
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=2700
    )
    
    # Since the response is a Pydantic model, you should access attributes directly
    return response.choices[0].message.content.strip()

def save_response_as_json(response, csv_filename):
    # Extract the name of the CSV file without its extension
    base_name = os.path.basename(csv_filename).split('.')[0]
    json_filename = f"openai_analysis_{base_name}.json"
    
    with open(json_filename, 'w') as json_file:
        json.dump({"response": response}, json_file, indent=4)

def main():
    document_content = get_document_content('openai_command_line_analysis_fs.md')
    
    user_file_path = input("Enter the path to your log data file (or press enter for default 'sample_data_logs.csv'): ")
    if not user_file_path.strip():  # Check if user pressed enter without input
        user_file_path = 'sample_data_logs.csv'
    log_data = get_log_data_from_file(user_file_path)
    
    response = get_response_from_openai(log_data, document_content)
    print("\nResponse from OpenAI:\n", response)
    save_response_as_json(response, user_file_path)

if __name__ == "__main__":
    main()
