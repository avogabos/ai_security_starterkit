import os
import sys

# Adjust the import path to ensure modules can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = current_dir  # Assuming agent_run.py is in agent/scripts/
agent_dir = os.path.dirname(scripts_dir)
sys.path.append(scripts_dir)
sys.path.append(agent_dir)

# Import the main function from core_agent.py
from core_agent import main as agent_main

if __name__ == "__main__":
    agent_main()
    print("How did I do?")
