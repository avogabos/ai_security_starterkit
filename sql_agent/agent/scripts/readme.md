# README

## Overview

This project is an AI agent designed to analyze a SQLite database to answer user-specified Priority Intelligence Requirements (PIRs). The agent interacts with the database to gather metadata, generate summaries of tables and columns, and uses OpenAI's GPT-4 model to assist in generating analyses based on the data. It follows a REACT (Reasoning and Acting) loop to iteratively process user inputs, perform actions, and generate outputs.

## Scripts

### `agent_run.py`

This is the entry point of the agent. It sets up the necessary paths and imports, then starts the agent by calling the `main()` function from `main_gather_data.py`.

**Key functionalities:**

- Initializes import paths for modules.
- Calls the main function to start the data gathering and analysis process.
- Provides console output to indicate the start and completion of the agent's execution.

### `data_gathering.py`

This script contains functions for interacting with the database and generating summaries using OpenAI's GPT-4 model.

**Key functionalities:**

- **Database Interaction:**
  - `get_table_info(conn)`: Retrieves information about all tables and columns in the database.
  - `query_table_column(conn, table_name, column_name, logs_path)`: Queries a specific column in a table to gather sample data and statistics.
  - `persist_table_info(table_info)`: Saves table information to a JSON file.

- **Data Summarization:**
  - `generate_summary(client, table_name, column_name, data_type, data, prompts_path)`: Generates a summary for a specific column using GPT-4.
  - `generate_table_summary(client, table_name, columns, prompts_path)`: Generates a structural summary for a table.
  - `create_database_context_md()`: Compiles all table and column summaries into a Markdown file for context.

- **Utilities:**
  - `count_tokens(text)`: Counts the number of tokens in a given text using the GPT-4 tokenizer.
  - `validate_and_extract_json(response)`: Validates and extracts JSON from GPT-4 responses.
  - `retry_with_json_prompt(client, original_prompt)`: Retries generating a summary if the initial response is invalid.

### `main_gather_data.py`

This script contains the main logic of the agent, including initializing the database connection, handling user input, and managing the REACT loop.

**Key functionalities:**

- **Agent Initialization:**
  - Sets up logging and environment variables.
  - Initializes the OpenAI client with the provided API key.
  - Connects to the SQLite database.

- **User Interaction:**
  - `request_pir_from_user()`: Prompts the user to input their Priority Intelligence Requirement.
  - Reads and saves the user's PIR for processing.

- **REACT Loop and Function Handling:**
  - `run(pir_content)`: Executes the REACT loop, where the agent processes messages, calls functions, and generates outputs.
  - Defines available functions the agent can call, such as `gather_all_summaries`, `execute_sql_query`, `read_table_summary`, etc.
  - Manages message exchanges and token counts to stay within model limits.

- **Function Definitions:**
  - `finish(answer)`: Signals the agent to stop execution and provide the final answer.
  - `gather_all_summaries()`: Generates summaries for all tables and columns.
  - `execute_sql_query(query)`: Executes a SQL query against the database with safety checks.
  - `check_database_context_md_exists()`: Checks if the context Markdown file exists.
  - `read_database_context_md()`: Reads the database context for analysis.

## Use

To utilize the agent for analyzing your database based on specific PIRs, follow these steps:

1. **Prepare the Database:**
   - Ensure your SQLite database is located at `data/hrc_emails/database.sqlite`.
   - The database should contain the tables and data relevant to your PIR.

2. **Run the Agent:**
   - Navigate to the directory containing `agent_run.py`.
   - Execute the script:

     ```bash
     python agent_run.py
     ```

3. **Input Your PIR:**
   - When prompted, enter your Priority Intelligence Requirement.
   - Press Enter on an empty line to indicate you are done.

4. **Agent Processing:**
   - The agent will start processing your PIR.
   - It will gather necessary data from the database, generate summaries, and perform analysis using GPT-4.

5. **Review Outputs:**
   - The results, summaries, and context files will be saved in the `metadata` directory.
   - Logs detailing the agent's actions and any errors will be saved in the `logs` directory.

6. **Access the Analysis:**
   - Open `metadata/database_context.md` to view the compiled summaries and analysis.
   - Review any generated JSON summary files in the `metadata/json` directory.

## Setup

Follow these steps to set up the agent on your local machine:

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/yourrepository.git
   cd yourrepository
   ```

2. **Install Dependencies:**

   Ensure you have Python 3.7 or higher installed. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

   **Contents of `requirements.txt`:**

   ```
   pandas
   tiktoken
   openai
   python-dotenv
   ```

3. **Set Environment Variables:**

   - Create a `.env` file in the project root directory.
   - Add your OpenAI API key to the `.env` file:

     ```
     OPENAI_API_KEY=your-openai-api-key
     ```

4. **Directory Structure:**

   Ensure the following directory structure is in place:

   ```
   project_root/
   ├── agent/
   │   ├── scripts/
   │   │   ├── agent_run.py
   │   │   ├── data_gathering.py
   │   │   └── main_gather_data.py
   │   ├── metadata/
   │   │   ├── json/
   │   │   ├── logs/
   │   │   └── database_context.md
   │   ├── prompts/
   │   │   ├── PIRs/
   │   │   ├── query_data_summary.md
   │   │   └── table_structure_summary.md
   │   └── logs/
   ├── data/
   │   └── emails/
   │       └── database.sqlite
   ├── .env
   └── requirements.txt
   ```

   - Create directories if they do not exist:

     ```bash
     mkdir -p agent/metadata/json
     mkdir -p agent/metadata/logs
     mkdir -p agent/prompts/PIRs
     mkdir -p agent/logs
     mkdir -p data/hrc_emails
     ```

5. **Place the Database:**

   - Copy your SQLite database file to `data/emails/database.sqlite`.

6. **Configure Paths (if necessary):**

   - If your directory structure differs, adjust the paths in `data_gathering.py` and `main_gather_data.py` accordingly.
   - Update the `db_path`, `metadata_path`, `prompts_path`, and `logs_path` variables to reflect your setup.

7. **Run the Agent:**

   - Execute the agent from the `scripts` directory or adjust your command to include the correct path:

     ```bash
     python agent/scripts/agent_run.py
     ```

   - Follow the on-screen instructions to input your PIR.

8. **Check the Results:**

   - Summaries and analyses will be available in the `agent/metadata` directory.
   - Logs for each session will be stored in `agent/logs`.

9. **Troubleshooting:**

   - Ensure that all required Python packages are installed.
   - Verify that the OpenAI API key is correct and has sufficient permissions.
   - Check the logs in `agent/logs` for detailed error messages if the agent fails to run properly.

---

By following this guide, you should be able to set up and run the AI agent to analyze your SQLite database and generate insights based on your Priority Intelligence Requirements.