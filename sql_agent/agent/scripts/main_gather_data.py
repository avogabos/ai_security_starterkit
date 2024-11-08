# main_gather_data.py

import os
import sys
import json
import re
import sqlite3
import logging
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import tiktoken
from typing import Annotated as A, List, Dict
from annotated_docs.json_schema import as_json_schema
from collections.abc import Callable
from openai import OpenAI

# Define agent_dir before using it
current_dir = os.path.dirname(os.path.abspath(__file__))
agent_dir = os.path.dirname(current_dir)

# Then you can define logs_dir
logs_dir = os.path.join(agent_dir, 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Set up logging
log_filename = datetime.now().strftime('agent_%Y%m%d_%H%M%S.log')
log_file_path = os.path.join(logs_dir, log_filename)
logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Import functions from the data_gathering module
from data_gathering import (
    get_table_info,
    persist_table_info,
    query_table_column as query_table_column_function,
    generate_summary as generate_summary_function,
    generate_table_summary as generate_table_summary_function,
    count_tokens,
    create_database_context_md,
    json_metadata_path  
)

# Load environment variables
load_dotenv()

# Initialize tokenizer
tokenizer = tiktoken.encoding_for_model("gpt-4")

# Database and file paths
current_dir = os.path.dirname(os.path.abspath(__file__))
agent_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(agent_dir)

# Paths based on your directory structure
db_path = os.path.join(project_root, 'data', 'emails', 'database.sqlite')
metadata_path = os.path.join(agent_dir, 'metadata')
prompts_path = os.path.join(agent_dir, 'prompts')
logs_path = os.path.join(metadata_path, 'logs')

# Ensure directories exist
os.makedirs(metadata_path, exist_ok=True)
os.makedirs(prompts_path, exist_ok=True)
os.makedirs(logs_path, exist_ok=True)

def calculate_total_tokens(messages, function_schemas):
    total_tokens = 0
    for idx, message in enumerate(messages):
        content = message.get('content', '')
        if not isinstance(content, str):
            logging.error(f"Invalid content in message at index {idx}")
            content = ''
        total_tokens += len(tokenizer.encode(content))
    functions_str = json.dumps(function_schemas)
    total_tokens += len(tokenizer.encode(functions_str))
    return total_tokens

def save_messages_to_file(messages, function_schemas, iteration):
    log_filename = os.path.join(logs_dir, f'messages_iteration_{iteration}.json')
    log_data = {
        'messages': messages,
        'function_schemas': function_schemas,
    }
    with open(log_filename, 'w') as f:
        json.dump(log_data, f, indent=2)
    logging.info(f"Messages saved to {log_filename}")

# Create the database connection
conn = None

def request_pir_from_user():
    pir_dir = os.path.join(prompts_path, 'PIRs')
    os.makedirs(pir_dir, exist_ok=True)
    # Find the next available number
    existing_files = os.listdir(pir_dir)
    numbers = [int(re.findall(r'user_PIR_(\d+).md', fname)[0]) for fname in existing_files if re.match(r'user_PIR_\d+.md', fname)]
    next_number = max(numbers) + 1 if numbers else 1
    pir_filename = f'user_PIR_{next_number}.md'
    pir_filepath = os.path.join(pir_dir, pir_filename)
    # Prompt the user
    print("Please enter your Priority Intelligence Requirement (PIR). Press Enter when done:")
    pir_content = ''
    while True:
        try:
            line = input()
            if line == '':
                break
            pir_content += line + '\n'
        except EOFError:
            break
    # Save the PIR
    with open(pir_filepath, 'w') as f:
        f.write(pir_content)
    print(f"PIR saved to {pir_filepath}")
    return pir_content  

def check_database_context_md_exists() -> bool:
    """Checks if the 'database_context.md' file exists in the metadata directory."""
    md_file_path = os.path.join(metadata_path, 'database_context.md')
    return os.path.exists(md_file_path)

def read_database_context_md() -> str:
    """Reads the contents of 'database_context.md' with a token limit."""
    md_file_path = os.path.join(metadata_path, 'database_context.md')
    try:
        with open(md_file_path, 'r') as f:
            content = f.read()
        # Limit the content to 1500 tokens
        max_tokens = 2500
        tokens = tokenizer.encode(content)
        if len(tokens) > max_tokens:
            content = tokenizer.decode(tokens[:max_tokens])
            content += "\n\n[Content truncated due to token limit]"
        return content
    except FileNotFoundError:
        return f"File 'database_context.md' not found at {md_file_path}."

def initialize_database_connection():
    global conn
    try:
        conn = sqlite3.connect(db_path)
        print(f"Successfully connected to the database at {db_path}")
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

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

def gather_all_summaries() -> str:
    """Generates summaries for all tables and columns in the database in one action."""
    global conn, openai_client

    # Step 1: Identify and persist table information
    table_info = get_table_info(conn)
    persist_table_info(table_info)  # No need to pass path, as it's handled inside the function

    # Load the persisted table info from json_metadata_path
    identified_table_data_path = os.path.join(json_metadata_path, 'identified_table_data.json')
    try:
        with open(identified_table_data_path, 'r') as f:
            identified_table_data = json.load(f)
        print(f"Loaded persisted table info from {identified_table_data_path}")
    except FileNotFoundError:
        return f"Error: File not found at {identified_table_data_path}"
    except json.JSONDecodeError:
        return f"Error: Invalid JSON in file {identified_table_data_path}"

    # Generate summaries for each table
    tables = pd.DataFrame(identified_table_data).groupby('table_name')
    for table_name, table_data in tables:
        try:
            columns = table_data.to_dict('records')
            table_summary = generate_table_summary_function(openai_client, table_name, columns, prompts_path)

            # Store the table summary in json_metadata_path
            summary_file = f"{table_name}_structure_summary.json"
            with open(os.path.join(json_metadata_path, summary_file), 'w') as f:
                f.write(table_summary)

            print(f"Structure summary for {table_name} generated and stored.")

        except Exception as e:
            print(f"Error processing table {table_name}: {e}")
            continue  # Continue with the next table in case of an error

    # Query each table/column and generate summaries
    for row in identified_table_data:
        try:
            table_name = row['table_name']
            column_name = row['column_name']
            data_type = row['data_type']

            data, column_data_type = query_table_column_function(conn, table_name, column_name, logs_path)
            summary = generate_summary_function(openai_client, table_name, column_name, column_data_type, data, prompts_path)

            # Store the summaries in json_metadata_path
            summary_file = f"{table_name}_{column_name}_summary.json"
            with open(os.path.join(json_metadata_path, summary_file), 'w') as f:
                f.write(summary)

            print(f"Summary for {table_name}.{column_name} generated and stored.")

        except Exception as e:
            print(f"Error processing column {table_name}.{column_name}: {e}")
            continue  # Continue with the next column in case of an error

    # After generating all summaries, create the database context markdown file
    create_database_context_md()  # No need to pass path if handled inside the function

    return "All summaries generated successfully."

def execute_sql_query(query: str) -> str:
    """
    Executes a SQL query against the database.

    Before executing, it estimates the size of the result to ensure it does not exceed 4000 tokens.

    If the estimated size exceeds 4000 tokens, it returns an error message.

    The function uses an approximate conversion of 1 token ~ 4 characters.

    If the query does not contain a LIMIT clause, it adds 'LIMIT 50' to the query.
    """
    global conn
    cursor = conn.cursor()
    # Ensure the query has a LIMIT clause
    if 'limit' not in query.lower():
        query_with_limit = f"{query.strip().rstrip(';')} LIMIT 50"
    else:
        query_with_limit = query
    # Execute the query
    try:
        cursor.execute(query_with_limit)
        rows = cursor.fetchall()
        # Convert rows to string
        result = '\n'.join([str(row) for row in rows])
        # Estimate the size
        total_size_chars = len(result)
        total_tokens = total_size_chars / 4
        if total_tokens > 4000:
            return f"Result size is too large ({int(total_tokens)} tokens). Please refine your query."
        else:
            return result
    except Exception as e:
        return f"Error executing query: {e}"

def read_table_summary(table_name: str) -> str:
    """Reads the summary of a specified table."""
    summary_file = os.path.join(json_metadata_path, f"{table_name}_structure_summary.json")
    try:
        with open(summary_file, 'r') as f:
            summary = f.read()
        return summary
    except FileNotFoundError:
        return f"Summary file for table '{table_name}' not found."

def gather_table_info() -> str:
    """Gathers table information and saves it to a file."""
    global conn, metadata_path
    table_info = get_table_info(conn)
    persist_table_info(table_info, metadata_path)
    return "Table information gathered and saved to identified_table_data.json."

# Update the name_to_function_map by including 'gather_table_info'
name_to_function_map: Dict[str, Callable] = {
    'get_available_functions': get_available_functions,
    'gather_all_summaries': gather_all_summaries,
    # 'gather_table_info': gather_table_info,  # Commented out as per original code
    'read_table_summary': read_table_summary,
    'execute_sql_query': execute_sql_query,
    'check_database_context_md_exists': check_database_context_md_exists,
    'create_database_context_md': create_database_context_md,
    'read_database_context_md': read_database_context_md,
    'finish': finish,
}

# Generate JSON schemas for the functions
def generate_function_schemas():
    schemas = []
    for func in name_to_function_map.values():
        schema = as_json_schema(func)
        function_schema = {
            "name": schema["name"],
            "description": schema.get("description", ""),
            "parameters": schema.get("parameters", {})
        }
        schemas.append(function_schema)
    return schemas

def run(pir_content):
    global openai_client

    # Instantiate the OpenAI client
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    function_schemas = generate_function_schemas()

    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI agent tasked with answering a Priority Intelligence Requirement (PIR) by analyzing a database. "
                "You can call 'get_available_functions' at any time to see what functions you have available.\n\n"
                "Before attempting to gather data, check if 'database_context.md' exists by calling 'check_database_context_md_exists'. "
                "If it exists, you can read its contents using 'read_database_context_md' and use it to build your analysis plan. "
                "If not, you should gather data by calling 'gather_all_summaries'.\n\n"
                "You can use 'execute_sql_query' to execute SQLite queries. Carefully think through your strategy before executing queries. "
                "Use metadata or statistics about a given query to determine how useful it will be before executing it. "
                "Try your best to limit the amount of data your queries return. The function will automatically limit the result set to prevent exceeding 4000 tokens.\n\n"
                "In each turn, follow this format:\n\n"
                "THOUGHT: Reason about what to do next.\n"
                'ACTION: Call a function with arguments as JSON, e.g., {"function": "read_database_context_md", "arguments": {}}.\n\n'
                "Do not include OBSERVATION until after you receive the function result.\n\n"
                "When you receive the function result, proceed to the next step, incorporating the OBSERVATION and determining your next THOUGHT and ACTION.\n\n"
                "Continue this loop until you've completed the task, then finish the task by calling the 'finish' function with your final answer."
            )
        },
        {
            "role": "user",
            "content": (
                "Please answer the following Priority Intelligence Requirement (PIR) by analyzing the database:\n\n"
                f"{pir_content}\n\n"
                "A good place to start is 'get_available_functions' to see what capabilities you currently have."
            ),
        },
    ]

    max_iterations = 20
    iteration = 0
    while iteration < max_iterations:
        try:
            # Calculate total tokens
            total_tokens = calculate_total_tokens(messages, function_schemas)
            logging.debug(f"Total tokens before API call: {total_tokens}")
            if total_tokens > 8000:
                logging.warning(f"Total tokens ({total_tokens}) approaching model limit.")

            # Save messages to a log file
            save_messages_to_file(messages, function_schemas, iteration)

            # Prune messages if necessary
            max_token_limit = 7000
            if total_tokens > max_token_limit:
                logging.warning(f"Total tokens ({total_tokens}) exceed the limit ({max_token_limit}). Pruning messages.")
                messages = [messages[0]] + messages[-5:]
                total_tokens = calculate_total_tokens(messages, function_schemas)
                logging.debug(f"Total tokens after pruning: {total_tokens}")

            # Send the messages to get the next response
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                functions=function_schemas,
                function_call="auto",
            )

            assistant_message = response.choices[0].message.to_dict()
            messages.append(assistant_message)
            content = assistant_message.get('content', '')
            if content:
                print(f"Assistant: {content}")
                logging.debug(f"Assistant content: {content}")

            # Check if the assistant wants to call a function
            if assistant_message.get('function_call'):
                function_call = assistant_message['function_call']
                function_name = function_call['name']
                if function_name not in name_to_function_map:
                    print(f"Invalid function name: {function_name}")
                    messages.append({
                        "role": "assistant",
                        "content": f"Invalid function name: {function_name}"
                    })
                    iteration += 1
                    continue

                function_to_call = name_to_function_map[function_name]
                function_args = function_call.get('arguments', {})

                if not isinstance(function_args, dict):
                    try:
                        function_args = json.loads(function_args)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding function arguments: {e}")
                        messages.append({
                            "role": "assistant",
                            "content": f"Error decoding function arguments: {e}"
                        })
                        iteration += 1
                        continue

                # Call the function
                print(f"Calling function {function_name} with args: {function_args}")
                try:
                    function_response = function_to_call(**function_args)
                    # Convert function response to string if needed
                    if isinstance(function_response, (list, dict)):
                        function_response_str = json.dumps(function_response)
                    else:
                        function_response_str = str(function_response)

                    # Append the function response to the messages
                    messages.append({
                        "role": "function",
                        "name": function_name,
                        "content": function_response_str,
                    })

                    # After receiving the function response, we continue the loop
                    # without incrementing the iteration counter, so the assistant can process the observation
                    continue

                except StopException as e:
                    # The agent has decided to finish
                    print(f"Agent finished with message: {e}")
                    print("Final messages exchanged:")
                    for msg in messages:
                        role = msg.get("role", "")
                        name = msg.get("name", "")
                        content = msg.get("content", "")
                        if name:
                            print(f"{role} ({name}): {content}")
                        else:
                            print(f"{role}: {content}")
                    return
            else:
                # Assistant did not call a function, increment iteration
                iteration += 1
                if content:
                    print("Assistant did not call a function. Ending the loop.")
                else:
                    print("Assistant provided no content. Ending the loop.")
                break  # End the loop if the assistant does not call a function

        except Exception as e:
            logging.error(f"An error occurred in the REACT loop: {e}")
            print(f"An error occurred in the REACT loop: {e}")
            break

def main():
    # Initialize the database connection
    initialize_database_connection()

    # Prompt the user for a PIR and get the content
    pir_content = request_pir_from_user()

    # Run the REACT loop with the PIR content
    run(pir_content)

    # Close the connection at the end
    if conn:
        conn.close()
        print("Database connection closed.")
