# Auto Map Reduce:

Ok so we want a script that goes from `arbitrary data` ---> `custom intelligence report` with as few steps as possible. 

Here's the plan:

1. Provide the model with a file containing arbitrary text data.
2. One script (`file_evaluation.py`) conducts an initial file analysis (extendable as needed), tokenizes the data, and extracts random samples to send to the model.
3. The model crafts a summary of the sampled data, assigns expert roles, pinpoints specific tactics, techniques, and procedures (TTPs) or indicators to monitor.
4. Leveraging this summary, the model then composes a custom Python snippet tailored to analyze the entire file.
5. The second python script (`openai_auto_map_reduce.py`) integrates this snippet as it's map-reduce instruction set, and subsequently executes the map-reduce process.
6. The outcome is a comprehensive map-reduce intelligence brief, generated directly from the file input. Note that this process is entirely automated, however print statements are integrated into commandline output for visibility and inspection.

The guide below provides an overview of two Python scripts:

## Overview:

1. file_evaluation.py: This script Evaluates the attributes of a given file, extracts random samples, and then uses two few-shot prompts to analyze arbitrary file data and create the appropriate necessary python scripts. The output of these scripts feeds into the next script.
2. openai_auto_map_reduce.py: Uses the output of the file_evaluation.py script - specifically the properly formatted python to perform a map reduce summary of the target file.

### Scripts Breakdown

#### File Evaluation (file_evaluation.py):

This script evaluates your target file, it is not necessary to run this script separately, however we break it out in this example since it may be helpful for understanding your data and how it relates to the model. Key actions include

- File Analysis: Fetches file metadata including name, size, creation date, etc
- Sample Extraction: Randomly selects parts of your file until it accumulates 3000 tokens.
- OpenAI Model Interaction:
    - Generates an initial summary using the data_review_prompt.md few-shot prompt.
    - Generates a Python code snippet specifically tailored for map-reduce operations using the python_creation.md few shot prompt.
- Output Creation: The above generations are saved as individual files, for analyst review and are leveraged by the openai_auto_map_reduce.py script script.

#### File Summarization (openai_auto_map_reduce.py):

This is the main script, the functionalities of this script are:

- Integration with file_evaluation.py: The script calls the main function from the previous script to obtain our dynamically generated prompts.
- Prompt Extraction: Extracts the map-reduce prompts from the previously generated output.
- File Processing:
    - Segregates the file into smaller, more manageable chunks.
    - Utilizes the langchain library, combining it with the derived prompts to perform a map-reduce based summarization.
- Summary Compilation: The summarization results are penned down in a JSON format within an output file named out.json.

### Instructions for Use:

openai_auto_map_reduce.py encompasses the combined capabilities of both individual scripts:

- Integration with File Evaluation Functionalities: It internally processes the actions of the file_evaluation.py:
    - Retrieves file metadata.
    - Extracts samples up to 3000 tokens.
    - Interacts with the OpenAI model for evaluation and fetches a tailored Python code snippet.

- Prompt Extraction: Parses the output to extract map-reduce prompts.
- File Processing:
    - Splits the file into manageable chunks.
    - Harnesses the langchain library to execute map-reduce summarization using the derived prompts.
- Summary Compilation: Records the summarization results in out.json.

#### Using the Script:

- Ensure you have Python installed.
- Install essential Python packages:
```bash 
pip install openai tiktoken chardet zstandard langchain
```

#### Workflow:
1. Launch the openai_auto_map_reduce.py script.
2. Input the desired text file's path when prompted.
3. The script will present file attributes, the OpenAI model's feedback, and then proceed with the summarization.
4. Once done, you'll find:
    - An evaluation saved in the directory of the input file.
    - A summarization in the out.json file within the same directory.

#### Points of Caution:
- The script interacts with the OpenAI API; be mindful of any potential charges associated with the tokens used.
- It also leverages the langchain library; ensure it's correctly installed with its dependencies.
- Execute arbitrary code with caution. The script uses the exec() function to process the dynamically produced snippets. Always inspect the intermediate outputs to ensure safety.