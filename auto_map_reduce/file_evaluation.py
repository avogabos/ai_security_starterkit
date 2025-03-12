import os
import chardet
import tiktoken
import openai
import random
import re

# Read the OpenAI API key from environment variable
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")
openai.api_key = openai_api_key

def extract_random_samples(filename, total_tokens=3000):
    with open(filename, 'r') as f:
        content = f.read()

    enc = tiktoken.encoding_for_model("gpt-4")
    lines = content.split('\n')
    num_sections = 10
    lines_per_section = len(lines) // num_sections

    sampled_lines = []
    accumulated_tokens = 0

    for i in range(num_sections):
        section_lines = lines[i*lines_per_section:(i+1)*lines_per_section]
        random_lines = [random.choice(section_lines) for _ in range(3)]
        
        for line in random_lines:
            if accumulated_tokens + len(enc.encode(line)) > total_tokens:
                break
            sampled_lines.append(line)
            accumulated_tokens += len(enc.encode(line))

    return '\n'.join(sampled_lines), len(sampled_lines)

def file_attributes(filename):
    stats = os.stat(filename)
    attributes = {
        "File Name": os.path.basename(filename),
        "File Size (bytes)": stats.st_size,
        "File Creation Date": stats.st_ctime,
        "File Modification Date": stats.st_mtime,
        "File Access Date": stats.st_atime,
        "File Permissions": oct(stats.st_mode)[-3:],
        "Character Set": charset_detection(filename)
    }
    return attributes

def content_metrics(filename):
    with open(filename, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.readlines()

    metrics = {
        "Total Lines Count": len(content),
        "Total Word Count": sum(len(line.split()) for line in content),
        "Total Character Count": sum(len(line) for line in content)
    }
    return metrics

def charset_detection(filename):
    with open(filename, 'rb') as file:
        result = chardet.detect(file.read())
    return result['encoding']

# Get Markdown document for our prompt
def get_document_content(filename):
    with open(filename, 'r') as f:
        return f.read()

def get_response_from_openai(document, samples, md_prompt):
    md_prompt = get_document_content("data_review_prompt.md")
    system_content = "\n".join([f"{key}: {value}" for key, value in document.items()]) + "\n\nSamples (lines count: " + str(len(samples.split('\n'))) + "):\n" + samples
    
    messages = [
        {"role": "system", "content": md_prompt},
        {"role": "user", "content": system_content}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=500
    )
    return response.choices[0].message['content'].strip()

def format_checker(content):
    if not content.startswith("map_prompt = ChatPromptTemplate.from_messages("):
        print("Mismatch at the start of content.")
        return False
    if not "SystemMessagePromptTemplate(" in content:
        print("Missing SystemMessagePromptTemplate.")
        return False
    if not "HumanMessagePromptTemplate(" in content:
        print("Missing HumanMessagePromptTemplate.")
        return False
    # Check if the reduce_prompt string exists without expecting it to be the exact end
    if "reduce_prompt = ChatPromptTemplate.from_messages(" not in content:
        print("Mismatch in reduce_prompt declaration.")
        return False
    return True

def get_python_response(document, previous_response):
    md_prompt = get_document_content("python_creation.md")
    system_content = "\n".join([f"{key}: {value}" for key, value in document.items()]) + "\n\nPrevious Response:\n" + previous_response
    
    messages = [
        {"role": "system", "content": md_prompt},
        {"role": "user", "content": system_content}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=1000  # Adjust based on the length of response you're expecting
    )
    return response.choices[0].message['content'].strip()

def main():
    file_path = input("Enter the path to the file: ")

    # Get file attributes and metrics
    attributes = file_attributes(file_path)
    metrics = content_metrics(file_path)
    document = {**attributes, **metrics}
    print("\nFile Information:", document)

    # Extract samples and count lines
    samples, sampled_lines_count = extract_random_samples(file_path)
    print(f"\nSampled {sampled_lines_count} lines to get 3000 tokens.")

    # Get Markdown prompt
    md_prompt = get_document_content("data_review_prompt.md")

    # Get response from model
    response = get_response_from_openai(document, samples, md_prompt)
    print("\nResponse from OpenAI:\n", response)

    # Save response to file
    output_filename = f"{os.path.splitext(file_path)[0]}_data_evaluation.txt"
    with open(output_filename, 'w') as f:
        f.write(response)
    print(f"\nEvaluation saved to: {output_filename}")
    
    # Get response for Python creation
    python_response = get_python_response(document, response)

    # Check the response format
    if format_checker(python_response):
        # Save response to file
        output_filename_python = f"{os.path.splitext(file_path)[0]}_AutoMR.py"
        with open(output_filename_python, 'w') as f:
            f.write(python_response)
        print(f"\nPython code snippet saved to: {output_filename_python}")
    else:
        print("\nPython code snippet is not in the correct format.")
    
    # Return python_response for use in the other script
    return python_response, file_path

if __name__ == "__main__":
    main()
