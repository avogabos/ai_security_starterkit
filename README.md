# AI Security Starterkit: Integrating Large Language Models

Welcome to the AI Security Starterkit! Whether you're looking to delve into few-shot prompts, AI-driven intelligence summarization, or explore retrieval augmented generation, this repository is designed to help you get started on automating various aspects of security with AI.

## Few Shot Prompt Testing for Security Analysis
- **Purpose**: Test and iterate AI-powered security solutions
- **Scripts**:
  - `fs_test`: Uses OpenAI's API to analyze few-shot prompts from a markdown document, returning a JSON-formatted security analysis.
  - `fs_log_enrich`: Analyzes an entire log data file, outputting results in a structured JSON file.
- **Key Concepts**: Learn effective Few-shot prompting techniques to automate discrete analysis tasks.

## Map-Reduce for Intelligence Summarization
- **Purpose**: AI-driven summarization of large data sets to aid in analysis of specific and predtermined tactics, techniques, or procedures.
- **Script Features**:
  - `map_prompt`: Focuses on summarizing adversary targets, specifically technologies, industries, and business sectors.
  - `reduce_prompt`: Combines multiple intelligence briefs into a single unified brief.
- **Key Concept**: Leverage generalized summarization capabilities of LLMs to perform both broad summaries and specific intelligence collection criteria over a large data corpus.

## Auto Map-Reduce for Intelligence Summarization
- **Purpose**: Automate the process of data summarization end-to-end, focusing on specific predetermined tactics, techniques, or procedures.
- **Script Features**:
  - `File Evaluation`: Process and understand an arbitrary file by extracting its metadata and random samples for tokenized data evaluation.
  - `Dynamic Prompt Creation`: Based on the evaluation, the script will use an LLM to dynamically generate custom map and reduce prompts for intelligence summarization.
  - `Map-Reduce Execution`: The created prompts will be integrated into a map-reduce script to analyze and summarize the entire data file.

**Key Concept**: Incorporate LLMs to automate analyst tasks end-to-end. Seamlessly transition from raw data input to generating comprehensive summaries. This process captures overarching themes while pinpointing specific intelligence criteria, ensuring an analysis of extensive data corpora.

## Retrieval Augmented Generation (RAG)
- **Purpose**: Enhance model's capability by querying large datasets, leveraging both built-in and external knowledge.
- **Scripts**:
  - `json_chat_embedding.py`: Converts a large data corpus into structured embeddings using the `text-embedding-ada-002` model.
  - `query_embeddings.py`: Transforms user queries into embeddings and leverages GPT-4 to provide responses based on relevant chat data.
- **Key Concept**: Learn how to leverage embeddings, a core NLP technique to convert textual data into numerical vectors, capturing semantic relationships and providing LLMs the ability to reference a specific dataset.

## Take Aways

1. AI Integration: AI tools, when combined with traditional security tools and knowledge, can offer advanced threat detection and analysis capabilities.
2. Scalability: AI can process vast amounts of data efficiently, making it an invaluable asset for threat intelligence.
3. Customization: Tailoring AI tools to specific organizational needs can enhance their efficiency and applicability - customizing them to your specific analysis style can enhance your capabilities as an analyst.

## Conclusion
AI has immense potential in the field of security operations. Begin by testing and iterating, then scale and incorporate into broader security automation workflows. Remember to leverage the distinct capabilities of each script according to your data and security needs. Happy automating!
