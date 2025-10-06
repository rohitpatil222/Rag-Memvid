Field RAG Assistant: Offline Knowledge Base (Ollama + MemVid)
This project implements a Retrieval-Augmented Generation (RAG) system designed for low-resource, field environments. It uses MemVid for extremely efficient, compressed storage of the knowledge base and Ollama to serve a small, powerful language model (Qwen2:1.5b) for inference.
This setup ensures that technical support staff can query detailed documentation and safety procedures even without a consistent internet connection.
Key Technologies
* Framework: Flask (Web UI)
* LLM Runtime: Ollama
* Model: qwen2:1.5b (Configurable in field_rag_agent/rag_agent.py)
* RAG Tool: MemVid (for Knowledge Base compression and retrieval)
Project Structure
.
├── app/
│   ├── routes.py           # Flask routes for serving the UI and handling queries
│   └── __init__.py         # Flask app creation
├── templates/
│   └── index.html          # Frontend UI for Q&A and adding documentation
├── field_rag_agent/
│   ├── kb_files/           # Your raw technical documents (.txt files go here)
│   ├── artifacts/          # Generated MemVid files (memory.mp4, memory_index.json)
│   ├── encode_kb.py        # Script to process kb_files and generate MemVid artifacts
│   └── rag_agent.py        # Core logic: MemVid loading, context retrieval, and Ollama call
└── run.py                  # Entry point to start the Flask server

Setup and Installation
Follow these steps to get the system running locally.
Prerequisites
1. Python 3.10+
2. Ollama: Must be installed and running on your system.
3. FFmpeg: Required by the memvid library for video encoding/decoding.
Step 1: Clone the Repository & Setup Environment
# Clone this repository (assuming you have created and linked it)
# git clone [https://github.com/rohitpatil222/Field-RAG-Agent.git](https://github.com/rohitpatil222/Field-RAG-Agent.git)
# cd Field-RAG-Agent

# Create and activate a Python virtual environment (recommended)
python -m venv venv
./venv/Scripts/activate  # On Windows PowerShell: .\venv\Scripts\activate

Step 2: Install Python Dependencies
The core packages (flask, memvid, requests, etc.) need to be installed.
# This command assumes you have a requirements.txt file or run a setup script
# If using a setup script provided earlier:
python setup_env.py

Step 3: Pull the Ollama Model
Before running the application, ensure the required Qwen2 model is available via Ollama.
ollama pull qwen2:1.5b

Step 4: Encode the Knowledge Base (KB)
The RAG system cannot run until the source documents in field_rag_agent/kb_files/ are encoded into the compressed memory.mp4 and memory_index.json artifacts.
python field_rag_agent/encode_kb.py

Note: Run this command any time you add, modify, or delete documents from the kb_files directory.
Running the Application
After encoding, you can start the Flask server:
# 1. Set the Flask application entry point (PowerShell command)
$env:FLASK_APP='app'

# 2. Run the application
flask run

Alternatively, you can run the run.py script:
python run.py

The application will be accessible at: http://127.0.0.1:5000
How to Test the RAG
To confirm the RAG is working, you must ask questions that require the knowledge stored in your documentation (e.g., about "Padding" or "Error Code 4047"), as the LLM alone won't know the answer.
* Query Example: How does zero-padding mitigate edge noise?
* Expected RAG Answer: An answer based directly on the retrieved document chunk: "Padding strategically employs zero-padding to normalize image dimensions and mitigate edge noise."