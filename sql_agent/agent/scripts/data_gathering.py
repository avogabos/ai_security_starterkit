# data_gathering.py

import os
import sys
import sqlite3
import pandas as pd
import json
import re
import tiktoken
import glob
from datetime import datetime
from dotenv import load_dotenv
from typing import Any

# Load environment variables
load_dotenv()

# Initialize tokenizer
tokenizer = tiktoken.encoding_for_model("gpt-4")

# Define paths
current_dir = os.path.dirname(os.path.abspath(__file__))
# Adjust this path according to your directory structure
agent_dir = os.path.dirname(current_dir)
metadata_path = os.path.join(agent_dir, 'metadata')

# Ensure that the metadata_path exists
os.makedirs(metadata_path, exist_ok=True)

json_metadata_path = os.path.join(metadata_path, 'json')

# Ensure that the json_metadata_path exists
os.makedirs(json_metadata_path, exist_ok=True)

def count_tokens(text):
    return len(tokenizer.encode(text))

def get_table_info(conn):
    query = """
    SELECT 
        m.name AS table_name, 
        p.name AS column_name,
        p.type AS data_type
    FROM 
        sqlite_master m
    LEFT OUTER JOIN 
        pragma_table_info((m.name)) p
    ON 
        m.name <> p.name
    WHERE 
        m.type = 'table'
    ORDER BY 
        m.name, 
        p.cid
    """
    return pd.read_sql_query(query, conn)

def gather_table_info() -> str:
    """Gathers table information and saves it to a file."""
    global conn, metadata_path
    table_info = get_table_info(conn)
    persist_table_info(table_info, metadata_path)
    return "Table information gathered and saved to identified_table_data.json."

def persist_table_info(table_info):
    file_path = os.path.join(json_metadata_path, 'identified_table_data.json')
    table_info.to_json(file_path, orient='records')
    print(f"Table information persisted to {file_path}")

def query_table_column(conn, table_name, column_name, logs_path):
    # Get the data type of the column
    type_query = f"SELECT typeof({column_name}) FROM {table_name} LIMIT 1"
    data_type_df = pd.read_sql_query(type_query, conn)
    if data_type_df.empty:
        data_type = 'unknown'
    else:
        data_type = data_type_df.iloc[0, 0]

    # Query for sample values
    sample_query = f"""
    SELECT {column_name} as sample_values
    FROM {table_name}
    ORDER BY RANDOM()
    LIMIT 100
    """
    sample_result = pd.read_sql_query(sample_query, conn)

    # Query for statistics if the column is numeric
    if data_type in ('integer', 'real'):
        stats_query = f"""
        SELECT 
            COUNT(*) as count,
            AVG({column_name}) as avg,
            MIN({column_name}) as min,
            MAX({column_name}) as max
        FROM {table_name}
        """
        stats_result = pd.read_sql_query(stats_query, conn)
        result = pd.concat([sample_result, stats_result], axis=1)
    else:
        result = sample_result

    # Convert result to string and check token count
    result_str = result.to_string()
    token_count = count_tokens(result_str)
    
    # If token count exceeds 2000, truncate the result
    if token_count > 2000:
        result_str = result_str[:int(2000/token_count * len(result_str))]
    
    # Log the raw query output
    log_file = os.path.join(logs_path, f"{table_name}_{column_name}_query_log.txt")
    with open(log_file, 'w') as f:
        f.write(f"Query executed at: {datetime.now()}\n")
        f.write(f"Sample Query: {sample_query}\n")
        if data_type in ('integer', 'real'):
            f.write(f"Stats Query: {stats_query}\n")
        f.write(f"\nRaw output:\n{result_str}\n")
        f.write(f"Token count: {token_count}\n")
    
    return result_str, data_type

def validate_and_extract_json(response):
    # Try to parse the response as JSON directly
    try:
        json_obj = json.loads(response)
        return json_obj
    except json.JSONDecodeError:
        pass

    # Try to extract JSON from triple backticks
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
    if json_match:
        try:
            json_obj = json.loads(json_match.group(1))
            return json_obj
        except json.JSONDecodeError:
            pass

    return None

def retry_with_json_prompt(client, original_prompt):
    retry_prompt = (
        "This content is supposed to be in properly formatted json for processing in downstream applications. "
        "Please note your response to the initial prompt, consider if your response was correct, "
        "and provide only the correct json."
    )
    full_prompt = f"{original_prompt}\n\n{retry_prompt}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=800,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error retrying with JSON prompt: {e}")
        return None

def generate_summary(client, table_name, column_name, data_type, data, prompts_path):
    prompt_file = os.path.join(prompts_path, 'query_data_summary.md')
    if not os.path.exists(prompt_file):
        raise FileNotFoundError(f"Prompt file not found at {prompt_file}")

    with open(prompt_file, 'r') as file:
        prompt = file.read()

    full_prompt = f"{prompt}\n\nTable: {table_name}\nColumn: {column_name}\nData Type: {data_type}\nData:\n{data[:1000]}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=500,
            temperature=0.5
        )
        content = response.choices[0].message.content.strip()
        
        json_obj = validate_and_extract_json(content)
        if json_obj is None:
            print(f"Invalid JSON response for {table_name}.{column_name}. Retrying with JSON prompt.")
            retry_content = retry_with_json_prompt(client, full_prompt)
            json_obj = validate_and_extract_json(retry_content)
        
        if json_obj is None:
            print(f"Failed to get valid JSON for {table_name}.{column_name} after retry.")
            return content  # Return the original content if all attempts fail
        
        return json.dumps(json_obj, indent=2)
    except Exception as e:
        print(f"Error generating summary: {e}")
        return f"Error generating summary: {e}"

def generate_table_summary(client, table_name, columns, prompts_path):
    prompt_file = os.path.join(prompts_path, 'table_structure_summary.md')
    if not os.path.exists(prompt_file):
        raise FileNotFoundError(f"Prompt file not found at {prompt_file}")

    with open(prompt_file, 'r') as file:
        prompt = file.read()

    columns_str = "\n".join([f"- {col['column_name']} ({col['data_type']})" for col in columns])
    conversation = [
        {"role": "system", "content": "You are an expert at summarizing database table structures."},
        {"role": "user", "content": f"{prompt}\n\nTable Name: {table_name}\nColumns:\n{columns_str}"}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation,
            max_tokens=500,
            temperature=0.5
        )
        content = response.choices[0].message.content.strip()
        
        json_obj = validate_and_extract_json(content)
        if json_obj is None:
            print(f"Invalid JSON response for table {table_name}. Retrying with JSON prompt.")
            retry_content = retry_with_json_prompt(client, conversation[-1]['content'])
            json_obj = validate_and_extract_json(retry_content)
        
        if json_obj is None:
            print(f"Failed to get valid JSON for table {table_name} after retry.")
            return content  # Return the original content if all attempts fail
        
        return json.dumps(json_obj, indent=2)
    except Exception as e:
        print(f"Error generating table summary: {e}")
        return f"Error generating table summary: {e}"

def create_database_context_md() -> None:
    """
    Creates a 'database_context.md' file that compiles the table summaries and column summaries.
    """
    md_file_path = os.path.join(metadata_path, 'database_context.md')

    # Initialize the markdown content
    md_content = "The following is the schema and context for the target sqlite database\n\n"

    # First section: table summaries
    md_content += "table_name | structure_summary\n"
    md_content += "------------------------------\n"

    # Find all table summary files in json_metadata_path
    table_summary_files = glob.glob(os.path.join(json_metadata_path, '*_structure_summary.json'))

    for table_file in table_summary_files:
        table_name = os.path.basename(table_file).replace('_structure_summary.json', '')
        with open(table_file, 'r') as f:
            summary = f.read().strip()
        md_content += f"{table_name} | {summary}\n"

    md_content += "\n"

    # Second section: column summaries
    md_content += "table_name | column_name | summary\n"
    md_content += "----------------------------------\n"

    # Load the identified table data from json_metadata_path
    identified_table_data_path = os.path.join(json_metadata_path, 'identified_table_data.json')
    with open(identified_table_data_path, 'r') as f:
        identified_table_data = json.load(f)

    # Create a mapping from filenames to table_name and column_name
    filename_to_table_column = {}
    for row in identified_table_data:
        table_name = row['table_name']
        column_name = row['column_name']
        filename = f"{table_name}_{column_name}_summary.json"
        filename_to_table_column[filename] = (table_name, column_name)

    # Find all column summary files in json_metadata_path
    column_summary_files = glob.glob(os.path.join(json_metadata_path, '*_*_summary.json'))
    # Exclude table structure summary files
    column_summary_files = [f for f in column_summary_files if not f.endswith('_structure_summary.json')]

    # Sort the files for consistent ordering
    column_summary_files.sort()

    for column_file in column_summary_files:
        filename = os.path.basename(column_file)
        if filename in filename_to_table_column:
            table_name, column_name = filename_to_table_column[filename]
        else:
            # If the file is not in identified_table_data, attempt to split the filename
            base_name = filename.replace('_summary.json', '')
            parts = base_name.split('_')
            if len(parts) >= 2:
                table_name = parts[0]
                column_name = '_'.join(parts[1:])
            else:
                print(f"Unable to determine table and column names from filename: {filename}")
                continue

        with open(column_file, 'r') as f:
            summary_content = f.read().strip()
        # Extract the 'column_summary' field if the content is JSON
        try:
            summary_json = json.loads(summary_content)
            summary = summary_json.get('column_summary', summary_content)
        except json.JSONDecodeError:
            summary = summary_content

        md_content += f"{table_name} | {column_name} | {summary}\n"

    # Write the markdown content to the file
    with open(md_file_path, 'w') as md_file:
        md_file.write(md_content)

    print(f"Database context markdown file created at {md_file_path}")