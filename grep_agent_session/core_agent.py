# core_agent.py

import os
import sys
import json
import subprocess
import tiktoken
from dotenv import load_dotenv
from typing import Annotated as A, List, Dict
from collections.abc import Callable
import base64  # Import for base64 encoding

# Load environment variables
load_dotenv()

# Import the OpenAI client
from openai import OpenAI

# Instantiate the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize tokenizer
tokenizer = tiktoken.encoding_for_model("gpt-4o")  # Updated to use 'gpt-4o'

# Paths and directories
current_dir = os.path.dirname(os.path.abspath(__file__))
agent_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(agent_dir)

# Ensure necessary directories exist
metadata_path = os.path.join(agent_dir, 'metadata')
prompts_path = os.path.join(agent_dir, 'prompts')
logs_path = os.path.join(metadata_path, 'logs')

os.makedirs(metadata_path, exist_ok=True)
os.makedirs(prompts_path, exist_ok=True)
os.makedirs(logs_path, exist_ok=True)

# OpenAI function definitions
class StopException(Exception):
    """Stop Execution by raising this exception (Signal that the task is Finished)."""

def finish(answer: A[str, "Final response to the user."]) -> None:
    """Finish the task with a final answer."""
    raise StopException(answer)

def get_available_functions() -> List[Dict[str, str]]:
    """Returns a list of available functions with their descriptions."""
    functions_info = []
    for func_name, func in name_to_function_map.items():
        if func_name != 'get_available_functions':  # Avoid recursion
            desc = func.__doc__ or "No description available."
            functions_info.append({"name": func_name, "description": desc})
    return functions_info

# Variable to store the target directory
target_directory = ""

def list_files(directory: str = "") -> str:
    """Lists files in the specified directory within the target directory."""
    try:
        # Use the target_directory as base
        base_dir = os.path.join(target_directory, directory)
        files = os.listdir(base_dir)
        return json.dumps(files)
    except Exception as e:
        return f"Error listing files in directory '{directory}': {e}"

def read_file(file_path: str) -> str:
    """Reads the content of a file within the target directory, limited to 10000 tokens."""
    try:
        full_path = os.path.join(target_directory, file_path)
        with open(full_path, 'r') as f:
            content = f.read()
        # Limit content to 10000 tokens
        max_tokens = 10000
        tokens = tokenizer.encode(content)
        if len(tokens) > max_tokens:
            content = tokenizer.decode(tokens[:max_tokens])
            content += "\n\n[Content truncated due to token limit]"
        return content
    except Exception as e:
        return f"Error reading file '{file_path}': {e}"

def search_files(pattern: str, directory: str = "") -> str:
    """Searches for files containing the given pattern within the target directory."""
    try:
        # Use the target_directory as base
        base_dir = os.path.join(target_directory, directory)
        # Use grep to search for the pattern recursively in the base directory
        command = f"grep -ril '{pattern}' '{base_dir}'"
        process = subprocess.run(command, shell=True, capture_output=True, text=True)
        if process.returncode == 0:
            return process.stdout.strip()
        else:
            return "No files found containing the pattern."
    except Exception as e:
        return f"Error searching files: {e}"

def analyze_image(image_path: str, instruction: str = "") -> str:
    """Analyzes an image using GPT-4o's image analysis capabilities."""
    try:
        full_image_path = os.path.join(target_directory, image_path)
        with open(full_image_path, 'rb') as image_file:
            image_data = image_file.read()
        # Base64 encode the image
        base64_image = base64.b64encode(image_data).decode('utf-8')
        # Prepare the messages
        content = []
        if instruction:
            content.append({"type": "text", "text": instruction})
        else:
            content.append({"type": "text", "text": "Analyze the following image."})
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image}"
            }
        })
        messages = [
            {
                "role": "user",
                "content": content,
            }
        ]
        # Send the request to OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1000,
            temperature=0.5,
        )
        analysis = response.choices[0].message.content.strip()
        return analysis
    except Exception as e:
        return f"Error analyzing image '{image_path}': {e}"

# Update the name_to_function_map with the essential functions
name_to_function_map: Dict[str, Callable] = {
    'get_available_functions': get_available_functions,
    'list_files': list_files,
    'read_file': read_file,
    'search_files': search_files,
    'analyze_image': analyze_image,
    'finish': finish,
}

# Generate JSON schemas for the functions (OpenAI function calling format)
def generate_function_schemas():
    schemas = []
    for func_name, func in name_to_function_map.items():
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        # Define parameter schemas based on the function
        if func_name == 'list_files':
            parameters["properties"]["directory"] = {
                "type": "string",
                "description": "The subdirectory within the target directory to list files from."
            }
            # 'directory' is optional
        elif func_name == 'read_file':
            parameters["properties"]["file_path"] = {
                "type": "string",
                "description": "The path to the file to read, relative to the target directory."
            }
            parameters["required"].append("file_path")
        elif func_name == 'search_files':
            parameters["properties"]["pattern"] = {
                "type": "string",
                "description": "The pattern to search for in files."
            }
            parameters["properties"]["directory"] = {
                "type": "string",
                "description": "The subdirectory within the target directory to search within."
            }
            parameters["required"].append("pattern")
            # 'directory' is optional
        elif func_name == 'analyze_image':
            parameters["properties"]["image_path"] = {
                "type": "string",
                "description": "The path to the image file to analyze, relative to the target directory."
            }
            parameters["properties"]["instruction"] = {
                "type": "string",
                "description": "Custom instructions for analyzing the image."
            }
            parameters["required"].append("image_path")
            # 'instruction' is optional
        elif func_name == 'finish':
            parameters["properties"]["answer"] = {
                "type": "string",
                "description": "Final response to the user."
            }
            parameters["required"].append("answer")
        function_schema = {
            "name": func_name,
            "description": func.__doc__,
            "parameters": parameters
        }
        schemas.append(function_schema)
    return schemas

def calculate_total_tokens(messages, function_schemas):
    total_tokens = 0
    for message in messages:
        content = message.get('content', '')
        if isinstance(content, list):
            # Handle list of content pieces (for images and text)
            for item in content:
                if 'text' in item:
                    total_tokens += len(tokenizer.encode(item['text']))
                elif 'image_url' in item:
                    # Image URLs might be long due to base64 encoding
                    total_tokens += len(tokenizer.encode(item['image_url']['url']))
        else:
            total_tokens += len(tokenizer.encode(content))
    functions_str = json.dumps(function_schemas)
    total_tokens += len(tokenizer.encode(functions_str))
    return total_tokens

def summarize_interaction(user_request: str, agent_answer: str) -> str:
    """Summarizes the interaction between the user and the agent."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant that summarizes interactions."},
        {"role": "user", "content": f"User requested: {user_request}\n\nAgent's answer: {agent_answer}\n\nProvide a concise summary of the user request, the tasks performed and the final answer."}
    ]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=4000,
        temperature=0.5,
    )
    summary = response.choices[0].message.content.strip()
    return summary

def save_session_summary(summary: str, counter: int):
    session_dir = os.path.join(metadata_path, 'sessions')
    os.makedirs(session_dir, exist_ok=True)
    summary_file = os.path.join(session_dir, f'summary_{counter}.txt')
    with open(summary_file, 'w') as f:
        f.write(summary)

def run():
    global target_directory
    session_history = []
    session_counter = 0

    # Prompt the user to specify the target directory within Desktop
    desktop_path = os.path.expanduser("~/Desktop")
    print(f"Your Desktop directory is: {desktop_path}")
    target_subdir = input("Please enter the subdirectory within Desktop to use as the target directory: ").strip()
    target_directory = os.path.join(desktop_path, target_subdir)
    # Validate the directory
    if not os.path.exists(target_directory):
        print(f"The directory '{target_directory}' does not exist. Exiting.")
        return
    else:
        print(f"Target directory set to: {target_directory}")

    # Generate function schemas for OpenAI function calling
    function_schemas = generate_function_schemas()

    while True:
        user_input = input("Please enter your instruction (or type 'exit' to end the session): ")
        if user_input.lower() == 'exit':
            print("Ending the session.")
            break

        # Prepare session summaries
        if session_history:
            previous_actions = "\n\n".join(session_history)
            session_context = f"Previous interactions:\n{previous_actions}\n\n"
        else:
            session_context = ""

        # Prepare the system message
        system_message = {
            "role": "system",
            "content": (
                f"{session_context}"
                "You are an AI agent that interacts with the file system using command-line tools.\n\n"
                f"The target directory is '{target_directory}'. All file paths are relative to this directory.\n\n"
                "You have the following functions available:\n"
                "- list_files(directory: str): Lists files in a subdirectory within the target directory.\n"
                "- read_file(file_path: str): Reads the content of a file within the target directory, limited to 10000 tokens.\n"
                "- search_files(pattern: str, directory: str): Searches for files containing a specific pattern within the target directory.\n"
                "- analyze_image(image_path: str, instruction: str): Analyzes an image file using GPT-4o's image analysis capabilities.\n"
                "- finish(answer: str): Finish the task with a final answer.\n\n"
                "In each turn, follow this format:\n\n"
                "THOUGHT: Reason about what to do next.\n"
                'ACTION: Call a function with arguments as JSON, e.g., {"function": "list_files", "arguments": {"directory": "subdir"}}.\n\n'
                "Do not include OBSERVATION until after you receive the function result.\n\n"
                "When you receive the function result, proceed to the next step, incorporating the OBSERVATION and determining your next THOUGHT and ACTION.\n\n"
                "Continue this loop until you've completed the task, then finish the task by calling the 'finish' function with your final answer."
            )
        }

        messages = [
            system_message,
            {
                "role": "user",
                "content": user_input,
            },
        ]

        max_iterations = 10  # Adjust iterations as needed
        iteration = 0
        while iteration < max_iterations:
            try:
                # Calculate total tokens
                total_tokens = calculate_total_tokens(messages, function_schemas)
                if total_tokens > 120000:
                    # Prune messages to stay within limit
                    messages = [messages[0]] + messages[-5:]
                    total_tokens = calculate_total_tokens(messages, function_schemas)

                # Send the messages to get the next response, including functions
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    functions=function_schemas,
                    function_call="auto",  # Let the model decide when to call a function
                )
                assistant_message = response.choices[0].message

                # Extract function call if any
                function_call = assistant_message.function_call

                # Append the assistant's message to the conversation
                if function_call:
                    messages.append({
                        "role": "assistant",
                        "content": assistant_message.content or '',
                        "function_call": {
                            "name": function_call.name,
                            "arguments": function_call.arguments,
                        },
                    })
                else:
                    messages.append({
                        "role": "assistant",
                        "content": assistant_message.content or '',
                    })

                content = assistant_message.content or ''

                if content:
                    print(f"Assistant: {content}")

                if function_call:
                    # The assistant decided to call a function
                    function_name = function_call.name
                    if function_name not in name_to_function_map:
                        print(f"Invalid function name: {function_name}")
                        messages.append({
                            "role": "assistant",
                            "content": f"Invalid function name: {function_name}"
                        })
                        iteration += 1
                        continue

                    function_to_call = name_to_function_map[function_name]
                    function_args_json = function_call.arguments

                    # Parse the JSON arguments
                    try:
                        function_args_dict = json.loads(function_args_json)
                    except json.JSONDecodeError as e:
                        print(f"Error parsing function arguments: {e}")
                        messages.append({
                            "role": "assistant",
                            "content": f"Error parsing function arguments: {e}"
                        })
                        iteration += 1
                        continue

                    # Call the function
                    print(f"Calling function '{function_name}' with args: {function_args_dict}")
                    try:
                        function_response = function_to_call(**function_args_dict)
                        # Convert function response to string if needed
                        if isinstance(function_response, (list, dict)):
                            function_response_str = json.dumps(function_response)
                        else:
                            function_response_str = str(function_response)

                        # Append the function response to the messages as an observation
                        messages.append({
                            "role": "function",
                            "name": function_name,
                            "content": function_response_str,
                        })

                        # Continue the loop so the assistant can process the observation
                        continue

                    except StopException as e:
                        # The agent has decided to finish
                        final_answer = str(e)
                        print(f"Agent finished with message: {final_answer}")

                        # Summarize the interaction
                        summary = summarize_interaction(user_input, final_answer)
                        session_history.append(summary)
                        session_counter += 1

                        # Keep up to 10 summaries
                        if session_counter > 10:
                            session_history.pop(0)
                            session_counter -= 1

                        # Save the summary
                        save_session_summary(summary, session_counter)

                        # Break out of the inner loop to ask for the next instruction
                        break

                    except Exception as e:
                        print(f"Error calling function '{function_name}': {e}")
                        messages.append({
                            "role": "assistant",
                            "content": f"Error calling function '{function_name}': {e}"
                        })
                        iteration += 1
                        continue
                else:
                    # Assistant did not call a function, proceed to next iteration
                    iteration += 1
                    if content:
                        print("Assistant provided a response without calling a function.")
                    else:
                        print("Assistant provided no content. Ending the loop.")
                        break

            except Exception as e:
                print(f"An error occurred in the agent loop: {e}")
                break

        print("Session ended. Agent has completed the process.")

def main():
    print("Starting the agent...")
    run()
    print("Agent has completed the process.")

if __name__ == "__main__":
    main()
