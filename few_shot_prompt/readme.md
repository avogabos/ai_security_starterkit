# Few Shot Prompt testing for Security Analysis

Hello! Welcome to this walkthrough on how to use a simple few-shot prompt for security analysis using Large Language Models (LLMs). If you are new to security automation with AI you're in the right place or curious of how to incorporate a few shot prompt into an existing workflow you are in the right place.

This guide covers two scripts. The first introduces the use of a simple few-shot prompt for testing purposes. The second expands upon the first, allowing for the analysis of log data in a more extensive manner.

## 🤖 What's the Purpose?
In the field of security operations, iteration is key. Before deploying AI-powered security solutions at scale, it's essential to test, iterate, and refine the tasks that we are automating. This Python script serves as a basic tool to help you do just that. Instead of a full-fledged application, think of this as your sandbox for rapid testing and iteration.

**fs_test:** This Python script serves as a basic tool for quick testing and iteration using OpenAI's API. It allows you to use an existing few-shot prompt in a markdown document and get a JSON-formatted response analyzing the command. 

**fs_log_enrich**: The second script builds on the first. Instead of individual test commands, this script allows users to input an entire log data file. The output is saved in a structured JSON file for easy consumption and further analysis.

## 🚀 Quick Start
**Pre-requisites**
1. Python environment (3.x recommended).
2. OpenAI account with an API key.
3. Curiosity and an experimental mindset!

**Steps to Get Going**
API Key Setup: Ensure you've set up your OpenAI API key as an environment variable.

```bash
export OPENAI_API_KEY=YOUR_API_KEY
```

**Dependencies:** Install the openai Python library.

```bash
pip install openai
```

**Run & Experiment:** Execute the script and provide different test commands when prompted.

```bash
python YOUR_SCRIPT_NAME.py
```
**Analyze the Output:** Based on the provided few-shot prompt, the script will give you a JSON-formatted response detailing the analysis of the command.

## 📖 Python Script
To better understand how the script let's look at the main components:

1. **Environment Variable Setup:** Both scripts use an environment variable to retrieve the OpenAI API key.
2. **Reading the Document:** Both read the few-shot prompt from a markdown document.
3. **Interacting with OpenAI:** Both use OpenAI's API to process a prompt (either a user command or a log data file) using a few-shot approach.
4. **Extended Data Input in fs_log_analysis:** While the `fs_test.py` gets individual test commands from the user, `fs_log_analysis.py` prompts users for a path to a log data file. This file contains multiple commands or sequences to be analyzed.
5. **Saving Output as JSON (fs_log_analysis):** `fs_log_analysis.py` structures the output from OpenAI into JSON format and saves it with a naming convention based on the input file.

## 🧠 About the Few-Shot Prompt
The few-shot prompt is crucial. It's like teaching the AI how to approach the problem. For our purposes, the few shot prompt included in this example contains:

* Role & Objective: Directs the AI to think and act as a security expert.
* Analysis Context & Operating Environment: Gives the AI additional information about the environment.
* Security Tools and Platforms: Informs the AI of the tools at its disposal.

## 💡 Tips for Effective Iteration
1. Refine the Prompt: Adjust and refine based on outputs. If the AI isn't understanding certain nuances, try making the prompt clearer.
2. Diverse Testing: The more diverse commands you test, the better you can gauge the model's accuracy - make sure that the few-shot prompt contains commands which you are likely to observe in your environment.
3. Feedback Loop: Keep track of the model's incorrect outputs and think about how to adjust your prompt to fix these - remember the more information you provide the model the better it can reason, however you will begin to experience diminishing returns if you overload your context window with information outside of the context of the task you are seeking to perform.

## 📝 Examples fs_test

**Example 1:**

```bash
Enter your test data: $encoded="SGVsbG8gV29ybGQ="; $decoded=$(echo $encoded | base64 --decode); $dir_name="./tmp_$(date +%N)"; mkdir $dir_name && cd $dir_name; $file_name="data_$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 13).txt"; echo $decoded > $file_name; cat $file_name | rev; rm -rf $dir_name;


Response from model:
 {
  "Summary": "The command is a series of tasks which base64 decodes an encoded string, dynamically create a temporary directory, create a random text file inside the directory, save the decoded string to the file, reverse the string contents, display it, and eventually delete the directory.",
  "Classification": "Benign",
  "Explanation": "This series of commands appears to be a script for a benign operation. The 'base64' command is used for decoding a base64 encoded string. '$dir_name' is a variable set to a directory name dynamically using the date command. 'mkdir' and 'cd' commands are used to create and change into said directory. '$file_name' variable is set dynamically to a file name including a random string generated by 'head /dev/urandom | tr -dc A-Za-z0-9 | head -c 13'. The 'echo' command writes the decoded string into the file. The 'cat' with 'rev' command reads and reverses the content of the file. Finally, 'rm -rf $dir_name' is used to remove the directory and its contents. While some individual commands could be misused in harmful ways, in this context they are being used for benign operations such as encoding/decoding strings, file creation, reading, and deletion.",
  "Recommendations": "N/A"
}
```

**Example 2:**

```bash
Enter your test data: $t="R";$c="whoami.exe";schtasks /create /tn $t /tr $c /sc once /st 00:00 /ru SYSTEM;schtasks /run /tn $t;schtasks /delete /tn $t /f

Response from model:
 {
  "Summary": "This command creates a scheduled task to run 'whoami.exe' as SYSTEM, initiates the scheduled task, then deletes the task.",
  "Classification": "Malicious",
  "Explanation": "This is a series of 'schtasks' commands to create, run, and delete a task that will execute 'whoami.exe' as the SYSTEM user at a scheduled time, in this case, at '00:00'. The '/ru SYSTEM' option means the task runs with SYSTEM privileges, the highest level of permissions. 'whoami.exe' is a command-line utility that outputs the username of the user running the command; if run as SYSTEM, it signifies an escalation of privileges which is a common technique seen in attacks. The creation and subsequent deletion of the task after running could be an attempt to erase traces of the malicious activity.",
  "Recommendations": [
        "1. Document the observed malicious activity in 'Jira' and make sure to flag it as a major security incident. Include details such as the commands used, user, timestamps, and system.",
        "2. Isolate the compromised system to prevent any further malicious activities. Use Nessus or similar tools to scan the machine for any other potential threats or alterations.",
        "3. Use 'Splunk' and 'SentinelOne' to look for similar patterns of actions across the organization's environment, focusing on other occurrences of the 'schtasks' command with SYSTEM privileges."
  ]
}
```

## 📝 Examples fs_log_enrich

```json
 {
    "DESKTOP_101": {
        "User Status": "likely benign",
        "Overview": "User listed the contents of a directory and deleted temporary files which is common user behavior.",
        "Advanced Assessment": "N/A",
    },
    "LAPTOP_XYZ": {
        "User Status": "likely benign",
        "Overview": "User copied a local file and opened a common email, indicating normal behavior. SSH command may be part of their job responsibility.",
        "Advanced Assessment": "N/A",
    },
    "SALES_PC": {
        "User Status": "likely benign",
        "Overview": "Visited sales related web pages, expected and normal behavior for a sales PC.",
        "Advanced Assessment": "N/A",
    },
    "MACHINE_ABC": {
        "User Status": "likely compromised",
        "Overview": "Suspicious commands were executed that seem to expose sensitive information and also modify startup scripts.",
        "Advanced Assessment": {
            "analysis context": "Printing the private key and appending to .bashrc file is uncommon and could lead to potential compromise.",
            "log details": [
                {
                    "Timestamp": "2023-09-03 14:12:50",
                    "Command": "cat ~/.ssh/id_rsa"
                },
                {
                    "Timestamp": "2023-09-03 14:14:00",
                    "Command": "echo “/var/tmp/utility” >> ~/.bashrc"
                }
            ],
        },
    },
    "HR_DESK": {
        "User Status": "potentially compromised",
        "Overview": "Downloading a file using curl and execution of shell commands may not be common for HR computers.",
        "Advanced Assessment": {
            "analysis context": "Downloading files using command line tools and listing directories on an HR machine could indicate a potential compromise.",
            "log details": [
                {
                    "Timestamp": "2023-09-03 14:13:40",
                    "Command": "curl -o /tmp/hr_guide http://internal-hr/guide"
                },
                {
                    "Timestamp": "2023-09-03 15:11:10",
                    "Command": "curl -o /tmp/employee_data http://internal-db/employees"
                },
                {
                    "Timestamp": "2023-09-03 15:21:00",
                    "Command": "ls /home/user/Documents/"
                }
            ],
        },
    },
    "DEV_SRV02": {
        "User Status": "likely benign",
        "Overview": "Routine backup, file editing, and git operation on a server.",
        "Advanced Assessment": "N/A",
    },
    "API_NODE": {
        "User Status": "likely benign",
        "Overview": "Installation of an npm package, starting an npm application and deployment-related activities, which indicates usual behavior for a development server.",
        "Advanced Assessment": "N/A",
    },
    "SERVER_404": {
        "User Status": "likely benign",
        "Overview": "Listing log directories and performing Docker operations, which could indicate normal server maintenance.",
        "Advanced Assessment": "N/A",
    },
    "WEB_SERVER": {
        "User Status": "potentially compromised",
        "Overview": "Downloading files using wget which could be a sign of malicious activity.",
        "Advanced Assessment": {
            "analysis context": "The download of scripts on a server can introduce malware or other malicious activities.",
            "log details": [
                {
                    "Timestamp": "2023-09-03 14:18:00",
                    "Command": "wget http://192.168.2.8:8001/updates.sql -O /tmp/updates.sql"
                },
                {
                    "Timestamp": "2023-09-03 15:09:00",
                    "Command": "wget http://192.168.2.11:8011/config_v2.tar.gz -O /tmp/config_v2.tar.gz"
                }
            ],
        },
    },
    "MACHINE_DEF": {
        "User Status": "likely compromised",
        "Overview": "The user viewed sensitive log files and lists user accounts, which could indicate reconnaissance activity.",
        "Advanced Assessment": {
            "analysis context": "Reviewing authentication logs and the /etc/passwd file is uncommon and might suggest malicious activity.",
            "log details": [
                {
                    "Timestamp": "2023-09-03 14:20:20",
                    "Command": "tail -n 100 /var/log/auth.log"
                },
                {
                    "Timestamp": "2023-09-03 14:21:50",
                    "Command": "cat /etc/passwd"
                }
            ],
        },
        "Recommendations": "Reevaluate permissions, change user passwords and audit this system's activities."
    },
    "HR_PC": {
      "User Status": "potentially compromised",
      "Overview": "ToEnd-user machine associated with HR is seen to be using curl to download files which is uncommon for non-technical users.",
      "Advanced Assessment": {
          "analysis context": "End-user machine associated with HR is behaving in a manner that is typically associated with technical roles, this is a suspicious activity.",
           "log details": {
               "Timestamp": "2023-09-03 14:05:30",
               "Command": "curl -o /tmp/hr_guide http://internal-hr/guide"
           },
       },
       "Recommendations": "Investigate the HR_PC for potential compromise and raise the security awareness of the staff operating this machine."
   }
}
```

## 🌱 Conclusion & Next Steps
You're all set to start iterating! Remember, the goal isn't just to get the model to do every aspect of your work, but to focus on discrete tasks that can be tailored to your specific circumstance. Once you're confident with the results you are recieving, you can then think about scaling or integrating it into larger security automation workflows.
