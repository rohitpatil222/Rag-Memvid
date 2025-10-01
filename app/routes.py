# app/routes.py
from flask import Blueprint, render_template, request
# Import RAG and Encoding functions
from field_rag_agent.rag_agent import get_rag_response, setup_memvid
from field_rag_agent.encode_kb import encode_documents_from_kb_dir
import time
from pathlib import Path

# Create a Blueprint named 'bp'
bp = Blueprint('main', __name__)
KB_DIR = Path("field_rag_agent/kb_files")

@bp.route("/", methods=["GET", "POST"])
def index():
    output_message = ""
    
    if request.method == "POST":
        
        # --- 1. Handle Query Form Submission ---
        if 'query_action' in request.form:
            user_query = request.form.get("query_text")
            if user_query:
                try:
                    # Call your RAG pipeline
                    answer = get_rag_response(user_query)
                    output_message = f"**RAG Answer:** {answer}"
                except Exception as e:
                    output_message = f"<span class='error'>❌ Error during RAG query: {str(e)}</span>"
            else:
                output_message = "<span class='error'>Please enter a question to query the RAG system.</span>"

        # --- 2. Handle Add Text Form Submission ---
        elif 'add_doc_action' in request.form:
            new_content = request.form.get("doc_content")
            
            if new_content and len(new_content) > 5:
                try:
                    # Write the new content to a unique file
                    filename = f"runtime_doc_{int(time.time())}.txt"
                    file_path = KB_DIR / filename
                    file_path.write_text(new_content)
                    
                    # Re-encode the entire knowledge base (SLOW STEP: blocks response!)
                    encode_documents_from_kb_dir()
                    
                    # Re-initialize the RAG agent to load the new artifacts
                    setup_memvid()
                    
                    output_message = f"<span class='success'>✅ **Success!** Document added and Knowledge Base updated. (File: {filename})</span>"
                    
                except Exception as e:
                    output_message = f"<span class='error'>❌ Failed to add document or re-encode: {str(e)}</span>"
            else:
                output_message = "<span class='error'>Please enter documentation content (min 5 characters) to add to the knowledge base.</span>"
    
    # Render the template, passing the output message (safe allows HTML tags for styling)
    return render_template("index.html", output=output_message)