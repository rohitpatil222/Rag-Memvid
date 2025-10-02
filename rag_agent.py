# field_rag_agent/rag_agent.py - FIXED
import os
import sys
import json
import time
from pathlib import Path

# Paths and model
ARTIFACTS_DIR = Path(__file__).parent / "artifacts"
VIDEO_FILE = ARTIFACTS_DIR / "memory.mp4"
INDEX_FILE = ARTIFACTS_DIR / "memory_index.json"
# Change the model variable
OLLAMA_MODEL = "qwen2:0.5b" # Replace with your chosen model
RETRIEVAL_K = 1  # top-k chunks

# MemVid import
try:
    from memvid import MemvidChat
except Exception as e:
    print("❌ Could not import MemVid. Install memvid package.")
    # Use sys.exit(1) or re-raise if fatal, but for robustness keep 'raise e'
    raise e

# Ollama SDK or HTTP
OLLAMA_PKG_AVAILABLE = True
try:
    import ollama
except Exception:
    OLLAMA_PKG_AVAILABLE = False
import requests


# ---------------- Helper Functions ---------------- #
def check_artifacts():
    missing = []
    for p in (VIDEO_FILE, INDEX_FILE):
        if not p.exists():
            missing.append(str(p))
    if missing:
        raise FileNotFoundError(f"Missing artifacts: {missing}. Please run 'python encode_kb.py'.")


def load_memvid_agent():
    """Load MemVid memory agent once."""
    check_artifacts()
    agent = MemvidChat(video_file=str(VIDEO_FILE), index_file=str(INDEX_FILE))
    return agent
# In field_rag_agent/rag_agent.py

# ... (RETRIEVAL_K = 5 or 15)

def retrieve_context(memvid_agent, query, k=RETRIEVAL_K):
    """Retrieve top-k relevant chunks from MemVid."""
    try:
        raw = None
        # Tries to call with k, if MemvidChat supports it.
        try:
            raw = memvid_agent.search_context(query, k=k)
        except TypeError:
            # Fallback for older/different memvid versions that don't take 'k'
            print("⚠️ Memvid.search_context does not support 'k'. Using default retrieval.")
            raw = memvid_agent.search_context(query)

        # CRITICAL FIX: Ensure 'raw' is iterable and not empty/None
        if not raw or raw == []:
            return ""

        if isinstance(raw, str):
            return raw
        elif isinstance(raw, (list, tuple)):
            parts = []
            
            # Use 'raw' directly, as the Memvid library handles the internal 'top_k' based on config.
            results = raw
            
            for chunk in results:
                if isinstance(chunk, dict):
                    # Robustly extract text and source metadata
                    text = chunk.get("text") or chunk.get("content") or str(chunk)
                    # Note: Memvid often doesn't embed the original filename in metadata
                    # We will rely on the text being enough.
                    parts.append(text)
                else:
                    parts.append(str(chunk))
            return "\n\n--- CONTEXT CHUNKS ---\n\n" + "\n\n".join(parts)
        else:
            print(f"⚠️ Memvid returned unexpected type: {type(raw)}")
            return ""
    except Exception as e:
        print("⚠️ Retrieval error during search_context:", e)
        # Log the exception, but return an empty string to prevent LLM crash
        return ""

def call_ollama_with_prompt(prompt: str) -> str:
    """Query Ollama model using SDK or HTTP."""
    # ... (rest of the function remains the same as it was already robust) ...
    if OLLAMA_PKG_AVAILABLE:
        try:
            resp = ollama.chat(
                model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}], stream=False
            )
            if isinstance(resp, dict) and "message" in resp and isinstance(resp["message"], dict):
                return resp["message"].get("content", "").strip()
            return str(resp)
        except Exception as e:
            return f"❌ Ollama SDK error: {e}"
    else:
        try:
            url = "http://localhost:11434/api/chat"
            payload = {"model": OLLAMA_MODEL, "messages": [{"role": "user", "content": prompt}]}
            r = requests.post(url, json=payload, timeout=30)
            r.raise_for_status()
            data = r.json()
            if "choices" in data and len(data["choices"]) > 0:
                c = data["choices"][0]
                if isinstance(c, dict):
                    if "message" in c and isinstance(c["message"], dict):
                        return c["message"].get("content", "").strip()
                    if "content" in c:
                        return c.get("content", "").strip()
            if "message" in data and isinstance(data["message"], dict):
                return data["message"].get("content", "").strip()
            return json.dumps(data)[:1000]
        except Exception as e:
            return f"❌ Ollama HTTP call failed: {e}"


# ---------------- Public API ---------------- #
_memvid_agent = None  # singleton


def setup_memvid():
    """Call once at app startup to load memory."""
    global _memvid_agent
    if _memvid_agent is None:
        _memvid_agent = load_memvid_agent()
        print("✅ MemVid agent loaded successfully.")


def get_rag_response(user_query: str) -> str:
    """Main function for Flask or other API calls."""
    global _memvid_agent
    if _memvid_agent is None:
        setup_memvid()

    context = retrieve_context(_memvid_agent, user_query)
    if not context.strip():
        return "I couldn't find relevant documentation in the offline knowledge base for that query."

    rag_prompt = f"""
You are an expert Field Engineering assistant. Answer the user's question ONLY using the information
contained in the CONTEXT below. If the context does not contain the answer, say:
"I cannot answer that question based on the provided documents."

--- CONTEXT START ---
{context}
--- CONTEXT END ---

USER QUESTION: {user_query}
"""
    return call_ollama_with_prompt(rag_prompt)