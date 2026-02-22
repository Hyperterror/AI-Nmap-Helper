import sys
import re
import ipaddress
from typing import List
import subprocess
import platform
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()
client = Groq()

def parse_intent(user_input: str):
    ip_match = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", user_input)
    ip_address = None

    if ip_match:
        ip_address = ip_match.group()
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            return None

    if not ip_address:
        return None

    text = user_input.lower()
    if any(word in text for word in ["web", "http", "https", "website"]):
        mode = "web_scan"
    elif any(word in text for word in ["full", "detailed", "all ports"]):
        mode = "full_scan"
    else:
        mode = "quick_scan"

    return {"target": ip_address, "mode": mode}



def parse_nmap_output(stdout: str) -> list:
    """Parse nmap output and extract open ports with services."""
    open_ports = []
    for line in stdout.split('\n'):
        # Look for lines with 'open' status
        if '/tcp' in line and 'open' in line:
            parts = line.split()
            if len(parts) >= 3:
                port_protocol = parts[0]
                state = parts[1]
                service = parts[2] if len(parts) > 2 else 'unknown'
                extra = ' '.join(parts[3:]) if len(parts) > 3 else ''
                open_ports.append({
                    'port_protocol': port_protocol,
                    'service': service,
                    'extra': extra
                })
    return open_ports
def build_nmap_command(intent: dict) -> List[str]:
    target = intent["target"]
    mode = intent["mode"]

    if not target:
        raise ValueError("No valid target IP address found in intent.")
    # Use full path on Windows, simple command on Linux/Kali
    nmap_cmd = r"C:\Program Files (x86)\Nmap\nmap.exe" if platform.system() == "Windows" else "nmap"

    if mode == "web_scan":
        cmd = [nmap_cmd, "-T4", "-p", "80,443,8080", "-sV", target]
    elif mode == "full_scan":
        cmd = [nmap_cmd, "-T4", "-sV", "-sC", target]
    else:
        cmd = [nmap_cmd, "-T4", "-F", target]
    return cmd

def run_nmap_command(cmd: List[str]):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        print("Nmap scan timed out.")
        return None, "Timeout"
    if result.returncode != 0:
        print(f"Nmap scan failed with error: {result.stderr}")
        return None, result.stderr
    return result.stdout, None

def generate_ai_summary(target: str, open_ports: list, mode: str) -> str:
    if not open_ports:
        return (
            f"For {target}: no open ports were found in {mode} mode."
        )

    ports_str = "\n".join(
        f"- {p['port_protocol']} {p['service']}: {p['extra']}"
        for p in open_ports
    )

    prompt = f"""You are a cybersecurity analyst. Based on the nmap scan results, summarize the findings for:
Target: {target}
Mode: {mode}
Open Ports and Services: {ports_str}

Explain in simple language:
1) What these ports/services are usually used for.
2) Which ports are more sensitive from security perspective.
3) 2-3 safe next steps a beginner could try (non-destructive) to learn more about the target.
Use short bullets and simple language suitable for a beginner."""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a concise cybersecurity assistant"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4
    )
    return response.choices[0].message.content.strip()

def main():
    print("==================")
    print("====AI Nmap Helper====")
    print("==================")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("Enter Your Task: ").strip()
        except EOFError:
            break

        if user_input.lower() in ['exit']:
            print("Exiting AI Nmap Helper. Goodbye!")
            break

        if not user_input:
            print("Please enter a valid task.")
            continue

        print(f"Processing task: {user_input}\n")
        parsed_intent = parse_intent(user_input)
        if parsed_intent is None:
            print("Could not extract a valid IP address from your input. Please try again.")
            continue

        try:
            cmd = build_nmap_command(parsed_intent)
        except ValueError as e:
            print(f"Error: {e}")
            continue

        print(f"Generated nmap command: {' '.join(cmd)}\n")
        print(f"Running nmap scan: {' '.join(cmd)}\n")
        stdout, error = run_nmap_command(cmd)

        if error:
            print(f"Error running nmap: {error}")
            continue

        print(f"Nmap scan results:\n{stdout}\n")
        print("\n".join(stdout.splitlines()[:20]))
        print()
        open_ports = parse_nmap_output(stdout)
        summary = generate_ai_summary(parsed_intent["target"], open_ports, parsed_intent["mode"])
        print("====AI Summary====")
        print(summary)
        print("==================")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting gracefully.")
        sys.exit(0)