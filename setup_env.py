# setup_env.py - FIXED
#!/usr/bin/env python3
"""
setup_env.py
- Installs required Python packages into the current Python environment.
- Performs local checks for: ffmpeg, Ollama server reachability and the specified model.
- Meant to run ONCE by IT/ML before packaging for field laptops.
"""
import subprocess
import sys
import os
import shutil

REQUIRED_PKGS = [
    "memvid",      # MemVid encoder / runtime (assumed available on pip)
    "PyPDF2",      # PDF text extraction
    "requests",    # HTTP checks for Ollama fallback
    "tqdm",        # Progress bars
    "python-dotenv", # Useful for loading environment variables
]

OLLAMA_CHECK_URL = "http://localhost:11434/api/tags"  # conservative check used earlier
# Standardize model name to match rag_agent.py
# Update the list of expected models for the environment check
OLLAMA_MODEL_NAMES = ["qwen2:0.5b" ] # Add the new model
def run(cmd, check=True):
    print("↪", " ".join(cmd))
    return subprocess.run(cmd, check=check)

def pip_install(packages):
    print("Installing pip packages:", packages)
    try:
        run([sys.executable, "-m", "pip", "install", *packages])
        print("✅ pip packages installed.")
    except subprocess.CalledProcessError as e:
        print("❌ pip installation failed:", e)
        sys.exit(1)

def check_ffmpeg():
    print("\n--- Checking ffmpeg ---")
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        print(f"✅ ffmpeg found at: {ffmpeg}")
    else:
        print("❌ ffmpeg not found in PATH. Please install ffmpeg and ensure 'ffmpeg' is on PATH.")
        print("Examples: apt install ffmpeg  OR  brew install ffmpeg  OR download from ffmpeg.org")
        sys.exit(1)

def check_ollama():
    print("\n--- Checking Ollama server and model ---")
    try:
        import requests
        resp = requests.get(OLLAMA_CHECK_URL, timeout=5)
        if resp.status_code != 200:
            print(f"⚠️ Unexpected response from Ollama: HTTP {resp.status_code}")
            print("Ensure the Ollama desktop app is running and the API port hasn't changed.")
            sys.exit(1)
        payload = resp.json()
        
        models = []
        if isinstance(payload, dict):
            if "models" in payload and isinstance(payload["models"], list):
                models = [m.get("name", "") for m in payload["models"] if isinstance(m, dict)]
            elif "tags" in payload and isinstance(payload["tags"], list):
                models = [t for t in payload["tags"]]
        
        # Check if the required model is present
        required_model = OLLAMA_MODEL_NAMES[0] # qwen2:1.5b
        if any(m == required_model for m in models):
            print(f"✅ Found {required_model} available locally.")
        else:
            print(f"⚠️ {required_model} not found in Ollama. Please run: 'ollama pull {required_model}' and try again.")
            # Do not exit hard here, allowing a user to proceed and hit the failure later

    except Exception as e:
        print("❌ Could not reach Ollama API on http://localhost:11434.")
        print("Make sure the Ollama app is running and port 11434 is accessible.")
        print("Error:", e)
        sys.exit(1)

def main():
    print("=== Environment Setup for field_rag_agent ===")
    pip_install(REQUIRED_PKGS)
    check_ffmpeg()
    check_ollama()
    print("\n🎉 Environment checks passed. You can now run 'python encode_kb.py'.")

if __name__ == "__main__":
    main()