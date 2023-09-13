# Map-Reduce for Intelligence Summarization

In this walkthrough we will leverage Langchain and GPT-4 for a basic intelligence summarization task. If you are new to security automation with AI you're in the right place or curious of how to incorporate AI capabilities into your existing analysis workflow you are in the right place. If you are unfamiliar with language models and have a half hour bus ride consider reading this introduction

## 🤖 What's the Purpose?
The world of threat intelligence and security is awash with vast amounts of unstructured data. Analysts often sift through large volumes of texts, from communications logs to threat intelligence reports, trying to distill relevant insights. The purpose of this project is to offer an efficient solution for this challenge via AI-driven summarization. The goal is to empower analysts with a flexible tool that provides the ability to summarize large data sets and perform analysis of the underlying tactics, techniques or procedures.

## 🚀 Quick Start
**Pre-requisites**
1. Python Libraries:
 - os
 - openai
 - json
 - gzip (not used in the provided script, but included in the case that your dataset is gzipped)
 - zstandard (as zstd)
 - base64
 - concurrent.futures
 - tqdm
 - threading
2. Custom Libraries
- langchain
3. API key for LLM (in this script we use GPT-4, however GPT-3.5-turbo or equivalent LLM should suffice)
4. Curiosity and an experimental mindset!

**Steps to Get Going**
Ensure you have set up your OpenAI API key as an environment variable

```bash
export OPENAI_API_KEY=YOUR_API_KEY
```

**Dependencies:** Install the openai Python library.

```bash
pip install openai
```

**Run & Experiment:** Execute the script and experiment! To begin, you may find it helpful to start with a small corpus of text that you know well. Comparing your understanding of the text to the output of the LLM's analysis will help you find prompts which work best with your subject matter and intelligence summarization goals.

```bash
python YOUR_SCRIPT_NAME.py
```

After executing the script, it will ask for the filename:

```bash
Enter the name of the file you want to process (e.g., 1mon_parsed_chats.txt): <enter your target file here>
```

Once the script finishes processing, you can quickly view the summarized results in the out.json file directly from the command line.

```bash
cat out.json
```

**Iterate on your intelligence requirements** Although response should be relatively standard, the analysis will vary depending on the template prompts and model used. Take your time to experiment and determine the combination of prompts and model that returns consistent results for your data. Note that this summarization capability is subject to current model limitations such as hallucinations or prompt-injections and its results should be carefully weighed alongside human analysis. 

## 📖 Understanding the Script

**Prompt Templates**
There are two main prompt templates:

map_prompt: This is used to instruct the model to read chat transcripts and provide a paragraph summary, in this script we use the map_prompt to focus on technologies, industries, and business sectors.

reduce_prompt: This is used to instruct the model to combine multiple intelligence briefs into a a single unified brief.

Both these prompts begin with a SystemMessagePromptTemplate which sets the role or mindset for the AI, followed by HumanMessagePromptTemplate which gives the specific task. These templates define how the model will interact with our content.

```python
SystemMessagePromptTemplate(
    prompt=PromptTemplate(
        template="You are an expert intelligence and cybersecurity analyst.",
        input_variables=[],
    )
)
```
Here, we provide the model a role to ensure that the context is set correctly for the task

```python
HumanMessagePromptTemplate(
    prompt=PromptTemplate(
        template="As an intelligence analyst, review the chat transcripts below and write a one paragraph summary...{text}...",
        input_variables=["text"],
    )
)
```

This template instructs the model to review chat transcripts and summarize them


## 🧠 Tips for Effective Iterations
Map-reduce is a powerful tool that allows us to effectively summarize a large body of text. However, its usage is slightly different - unlike a few-shot approach, in this example we leverage a non-specific summary instruction for the model to avoid bias as it assesess the text. Below are some tips for effective iteration on this starter kit:

* Experiment with language and roles for the model, if your data is consistently
* Remove formatting from the data the more the model thinks of this as just text the better.
* Simple models may fit your needs better - in our cursory evaluation of this one dataset gpt-3.5-turbo appears to perform as well at this task as gpt-4 with a preference for creating lists (although your mileage may vary depending on the text you are assessing and your intelligence requirements)
* GPT-4 may take longer than gpt-3.5-turbo - especially for longer texts.

## 📝 Example Summarizations

Use these example summarizations to benchmark your own tests. Remember, this script does not persist the map functions, so no two summaries will be the same. In the examples below, we present summaries using gpt-3.5.-turbo and gpt-4 over 1 month and 3 months of chat logs (provided in the test_data folder).

Note: 1mon_parsed_chats.txt contains approximately 5500 tokens, 3mon_parsed_chats.txt contains approximately 150,000 tokens.

### 1 month gpt-3.5-turbo summary

**uid:** `test_data/1mon_parsed_chats.txt`

**Unified Brief:**

Target: The target's activities involve discussions related to various technologies, industries, and business sectors. The specific details vary across the chat transcripts, but there are indications of involvement in underground activities, cybersecurity, software development, and potentially illegal activities in the dark web. The target seems to be engaged in secretive communication and coordination of activities, potentially related to illicit transactions, hacking, and the sharing of sensitive information.

Priority Intelligence Requirements:
1. Identification of individuals involved in underground activities, illegal transactions, and hacking.
2. Mapping of the target's network and connections in the dark web.
3. Understanding the target's tactics and procedures for conducting illegal activities.
4. Identification of potential vulnerabilities in cryptocurrency systems and encryption methods used by the target.
5. Identification of any potential collaboration with other threat actors or criminal organizations.

Technologies/Industries/Business Sectors Targeted:
1. Cryptocurrency (specifically Bitcoin) - Coordinating payments, discussing Bitcoin transactions, and seeking additional downloads or bots for software testing.
2. Dark web communication - Using .onion domains and potentially engaging in illicit activities.
3. Cybersecurity - Mention of cryptography, encryption, VPN networks, and observing account validation patterns.
4. Software development - Focus on back-end development, implementing features, and handling errors during implementation.
5. Potentially illegal activities - Engagement in underground activities, involvement in the dark web, and coordination of illegal transactions.

Tools, Tactics, and Procedures:
1. Use of PGP encryption - Indicated by the mention of \"-----BEGIN PGP PUBLIC KEY BLOCK-----\" in the chat transcripts, suggesting the use of encryption for secure communication.
2. Sharing of URLs - The sharing of URLs (e.g., hxxps://qaz[.]im/load/Tb6rNh/dYkYy2, hxxps://qaz[.]im/load/hzkQTQ/BTa6Ze) may indicate the sharing of illicit or sensitive information.
3. Coordinating payments in Bitcoin - The target is involved in coordinating payments and receiving amounts in Bitcoin (bc1qy2083z665ux68zda3tfuh5xed2493uaj8whdwv).
4. Seeking VPN networks - The target is searching for a supplier and discussing accessing VPN networks, potentially for anonymizing their activities.
5. Engagement in secretive communication - The target is using chat transcripts and discussing the need to handle documents at home, suggesting a secretive approach to communication and potential involvement in illicit activities.
6. Focus on coding and software development - The chat transcripts involve discussions regarding coding, software testing, and implementation of features, indicating the target's focus on software development.\n\nNote: The information provided in the brief is based on the available chat transcripts and may be subject to interpretation. Additional context or information would be beneficial to provide a more accurate assessment."}

### 1 month gpt-4 summary

**uid:** `"test_data/1mon_parsed_chats.txt"`

**Unified Brief**
The intelligence gathered from the chat transcripts indicates the involvement of a group of individuals operating within the cybersecurity, darknet, and potentially cryptocurrency sectors. They are communicating via the Tor network, using anonymous email addresses on the .onion domain, and are likely engaging in encrypted communication using PGP (Pretty Good Privacy) for enhanced security. The primary language of communication is Russian, and the conversations revolve around Bitcoin transactions, potentially signaling involvement in illegal activities or cybercrimes.

The group's Priority Intelligence Requirements (PIR) appear to be the secure transfer of Bitcoins, encrypted communication, and the use of VPNs for secure internet connections. The technologies in use are primarily encryption technologies, VPNs, and Bitcoin. The industry or business sectors being targeted remain unclear, but given the context, they may be related to cryptocurrency and possibly illegal activities.

In terms of Tactics, Techniques, and Procedures (TTPs), the group is employing onion routing for secure and anonymous communication, PGP for message encryption, and VPNs for additional security. They are also using Bitcoins for transactions, which is common in illicit activities. Furthermore, the coded language and non-specific URLs shared suggest that they might be using these to lead to malicious sites or payloads.

The group is also discussing operational issues related to cryptology, bot technology, and software performance. There are indications of a potential cybersecurity operation in progress, focusing on a particular target and its backup. The use of coded language, the request for vacation, and the regular reference to operational responsibilities suggest a well-structured group with defined roles and tasks. In conclusion, this group appears to be a potential cyberthreat, possibly involved in illegal activities in the cybersecurity, darknet, and cryptocurrency sectors. They are using advanced technologies to maintain anonymity, secure their communication, and conduct transactions. The exact extent of their operations and the specific targets remain unclear and warrant further investigation.


### 3 month gpt-3.5-turbo:

**uid:** `"test_data/3mon_parsed_chats.txt"`

**Unified Brief:**

Target: Unknown individuals involved in cybercriminal activities, potentially operating on the dark web.

Priority Intelligence Requirements:
1. Identification of individuals involved in cybercrime and illicit activities.
2. Determination of the technologies, industries, and business sectors targeted by the individuals.
3. Identification of tools, tactics, and procedures used by the individuals.

Technologies/Industries/Business Sectors Targeted:
1. Cryptography
2. Debugging
3. Web inject formats
4. Container formats (vhd, vhdx)
5. Code execution from text files
6. Avast software (potential connection to the cybersecurity industry)
7. MSSQLSvc, SIP, HTTP (possibly related to hacking or cybersecurity)
8. RDP connections and FTP servers (common targets for unauthorized access)
9. Closed networks, email servers, and icon files (specific to the dark web activities)
10. PGP encryption and secure communication
11. Cryptocurrencies (Bitcoin)
12. Malware development, loaders, botnets

Tools, Tactics, and Procedures:
1. Use of encrypted email addresses and secure messaging platforms
2. Collaboration among individuals with expertise in encryption and cryptography
3. Trading on closed networks and communication through specific email addresses
4. Use of encryption tools such as GnuPG, WinPT, and other cryptors
5. Testing and improving encryption techniques, including encryption of executable files
6. Stealing data and login credentials through stealers and password grabbers
7. Exploiting vulnerabilities in RDP connections and FTP servers
8. Extracting RDP and SSH account information using stealers
9. Sharing shell access, encrypted messages, and financial transactions
10. Challenges with bot behavior, browser issues, and purchase processes
11. Covert operations using routers and memory exploitation techniques
12. Communication and coordination within the cybercriminal underworld

The overall context of the conversations suggests involvement in illicit activities, including hacking, cybercrime, and potentially trading illegal goods/services on the dark web. The specific industries or business sectors being targeted are not always explicitly mentioned, but there are indications of involvement in the cybersecurity industry, cryptography, financial transactions involving cryptocurrencies, and potentially other illicit activities. The use of encryption and secure communication platforms highlights the importance of maintaining anonymity and secrecy in their operations. Further analysis is required to gain a more comprehensive understanding of the targets' activities and the extent of their involvement in illicit or criminal actions.

### 3 month gpt-4:

**uid:** `"test_data/3mon_parsed_chats.txt"`

**Unified Brief:**

The target group, identified as a likely international Russian-speaking entity, is involved in sophisticated and organized cybercriminal activities. The sectors they primarily target include technology, finance, cybersecurity, logistics, and potentially healthcare and education. Their focal points indicate an emphasis on software development, network management, and encryption, with a keen interest in cryptocurrencies like Bitcoin.

Their Priority Intelligence Requirements (PIRs) include maintaining security and anonymity, conducting potentially illicit financial transactions, and deploying malware. They achieve this through a combination of encrypted and anonymous communication tools such as Tor networks, VPNs, and PGP public key encryption. They also use coded language and Bitcoin for transactions, indicating a high level of operational security.

The group's tools, tactics, and procedures (TTPs) include the use of Tor for anonymous communication, PGP for encryption, and Bitcoin for anonymous transactions. They also potentially utilize malware or botnets for cyber attacks, proxies and IP address manipulation, and services like privnote.com for sharing self-destructive notes. Their tactics involve the use of coded language, secure communication platforms, dynamic infrastructure, spoofed emails, and URL shortening services to mask the true destination of linked content. They are involved in potentially malicious activities such as cyberattacks, hacking, cyber-espionage, and possibly spam distribution, ransomware, and financial fraud. Their discussions suggest a high level of sophistication and organization, indicating a significant threat to the industries they operate in. They also exhibit signs of internal tension and conflict, which may present vulnerabilities.

In summary, the group presents as a highly technical and sophisticated threat, primarily targeting the technology, finance, and cybersecurity sectors. They deploy a range of tools and tactics to maintain security and anonymity while potentially engaging in illicit activities. Further monitoring and investigation are required to fully understand the scope of their operations and potential impact.