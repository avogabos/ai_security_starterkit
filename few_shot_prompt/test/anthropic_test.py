import os
from anthropic import Anthropic

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

def get_response_from_anthropic(prompt, document):
    """
    Use the Anthropic API to quickly evaluate our few-shot prompt approach
    """
    # Adjust the combined_prompt to meet Anthropic's requirements
    combined_prompt = f"{document} \n\nHuman: {prompt}\n\nAssistant:"
    
    completion = anthropic.completions.create(
        model="claude-2",
        max_tokens_to_sample=4000,
        prompt=combined_prompt
    )
    
    return completion.completion.strip()

def main():
    # The markdown content becomes the "system prompt" or guidelines for the model
    document_content = get_document_content('command_line_fs.md')
    
    user_prompt = input("Enter your test data: ")
    response = get_response_from_anthropic(user_prompt, document_content)
    print("\nResponse from Anthropic:\n", response)

if __name__ == "__main__":
    main()
