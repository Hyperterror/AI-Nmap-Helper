# AI Nmap Helper

A simple terminal-based assistant that combines **Nmap** with a **local AI helper**.  
You describe a security task in natural language, the tool chooses a safe Nmap scan for a private IP, runs it, parses the results, and prints an easy-to-understand security summary.

This project is designed as a minimal, educational example of **agentic cyber-defense**:  
> intent → tool selection → command execution → result parsing → AI explanation.

---

## Features

- 🖥️ **CLI-based** — runs entirely in the terminal.
- 🔍 **Intent → Nmap mapping**  
  - Understands simple requests like “scan 192.168.1.10 for web ports”.
  - Maps them to one of a few safe scan profiles (quick / full / web).
- 🌐 **Controlled targets only**  
  - Only allows scanning of private IP ranges and localhost (e.g. `192.168.x.x`, `10.x.x.x`, `127.0.0.1`).
- 📊 **Parsed Nmap output**  
  - Extracts open ports, protocol, service name, and extra info from Nmap text output.
- 🤖 **AI-generated explanation (via Groq)**  
  - Uses a Groq-hosted LLM to summarize what the open ports mean and suggest simple, non-destructive next steps.
- 🧩 **Easy to extend**  
  - Add more scan modes, tools, or richer parsing as needed.

---

## Architecture (High Level)

1. **Input layer (CLI)**  
   - Reads a natural-language task from the user.

2. **Intent parsing**  
   - Extracts the first IPv4 address.
   - Classifies the scan into one of:
     - `quick_scan`
     - `full_scan`
     - `web_scan`

3. **Command planner**  
   - Validates the IP is in a private range.
   - Maps mode → safe Nmap command (e.g. quick scan, full + scripts, web-only ports).

4. **Execution & parsing**  
   - Runs Nmap via `subprocess`.
   - Parses its text output to find open ports and associated services.

5. **AI summarizer**  
   - Sends the structured list of open ports to a Groq LLM.
   - Returns a short, beginner-friendly security summary.

---

## Requirements

- OS: Kali Linux or any modern Linux distribution.
- Tools:
  - `python3` (3.8+ recommended)
  - `nmap`
- Python packages:
  - `groq` (Python client for the Groq API)
- A Groq API key (free tier available).

---

## Installation

```bash
# Clone the repository
git clone https://github.com/Hyperterror/AI-Nmap-Helper.git
cd AI-Nmap-Helper

# (Optional) Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirement.txt

nmap --version
# If not installed:
# sudo apt update && sudo apt install -y nmap

export GROQ_API_KEY="your_groq_api_key_here"
Make sure Nmap is installed:

Groq API Setup
Create or log into your account at https://console.groq.com.

Generate an API key.

Export it in your shell:

bash
export GROQ_API_KEY="your_groq_api_key_here"
(You can also use a .env file or your shell profile, but an environment variable is the simplest.)

Usage
Run the helper:

bash
python ai_nmap_helper.py
You’ll see something like:

text
=== AI Nmap Helper ===
Note: Only scan networks you own or are authorized to test.
For safety, this tool only allows private IP ranges.

Enter your security task:
Example commands
Quick localhost scan:

text
Enter your security task: Scan 127.0.0.1 quickly and explain
Web-focused scan on a LAN host:

text
Enter your security task: Scan 192.168.1.10 for web ports and tell me what they mean