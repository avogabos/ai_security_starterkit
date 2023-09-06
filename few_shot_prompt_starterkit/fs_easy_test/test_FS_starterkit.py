import os
import openai

# Read the OpenAI API key from environment variable
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")
openai.api_key = openai_api_key

def get_document_content(filename):
    """Read the content of the markdown document."""
    with open(filename, 'r') as file:
        return file.read()

def get_response_from_openai(prompt, document):
    """
    Use the OpenAI API to quickly evaluate our few shot prompt approach
    """
    messages = [
        {"role": "system", "content": document},
        {"role": "user", "content": prompt}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=500
    )
    return response.choices[0].message['content'].strip()

def main():
    document_content = get_document_content('test_command_line_fs.md')
    user_prompt = input("Enter your test data: ")
    response = get_response_from_openai(user_prompt, document_content)
    print("\nResponse from OpenAI:\n", response)

if __name__ == "__main__":
    main()
