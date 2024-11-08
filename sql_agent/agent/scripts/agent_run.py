# agent_run.py

import os
import sys

# Adjust the import path to ensure modules can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = current_dir  # Assuming agent_run.py is in agent/scripts/
agent_dir = os.path.dirname(scripts_dir)
sys.path.append(scripts_dir)
sys.path.append(agent_dir)

# Import the main function from main_gather_data.py
from main_gather_data import main as gather_data_main

if __name__ == "__main__":
    print("Starting the agent...")
    gather_data_main()
    print("Agent has completed the data gathering process.")