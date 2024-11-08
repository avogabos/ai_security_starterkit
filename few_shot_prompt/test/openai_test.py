import os
from openai import OpenAI

# Instantiate a client using the new SDK
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')  # Defaults to the environment variable
)

def get_document_content(filename):
    """Read the content of the markdown document."""
    with open(filename, 'r') as file:
        return file.read()

def get_response_from_openai(prompt, document):
    """
    Use the OpenAI API to quickly evaluate our few-shot prompt approach.
    """
    messages = [
        {"role": "system", "content": document},
        {"role": "user", "content": prompt}
    ]

    # Use the instantiated client to make a call to the API
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=500
    )
    # Accessing the properties of the response which is now a Pydantic model
    return response.choices[0].message.content.strip()  # Adjusted to Pydantic model property access

def main():
    document_content = get_document_content('command_line_fs.md')
    user_prompt = input("Enter your test data: ")
    response = get_response_from_openai(user_prompt, document_content)
    print("\nResponse from OpenAI:\n", response)

if __name__ == "__main__":
    main()
