# field_rag_agent/encode_kb.py
import os
from pathlib import Path
from memvid import MemvidEncoder

KB_DIR = Path("field_rag_agent/kb_files")
ARTIFACTS_DIR = Path("field_rag_agent/artifacts")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

# Helper function that does the core encoding
def _perform_encoding(docs):
    encoder = MemvidEncoder()
    for doc in docs:
        encoder.add_text(doc)

    video_path = ARTIFACTS_DIR / "memory.mp4"
    index_path = ARTIFACTS_DIR / "memory_index.json"

    # build_video requires both video and index files
    encoder.build_video(output_file=str(video_path), index_file=str(index_path))
    print(f"✅ memory.mp4 and memory_index.json written to {ARTIFACTS_DIR}")

# This is the function that routes.py will call
def encode_documents_from_kb_dir():
    """Reads all documents from KB_DIR and encodes them."""
    docs = []
    # Reads documents from field_rag_agent/kb_files
    for txt_file in KB_DIR.glob("*.txt"):
        docs.append(txt_file.read_text())

    if not docs:
        # Create a demo file if kb_files is empty (for setup)
        demo_file = KB_DIR / "demo.txt"
        demo_file.write_text("This is a demo document.")
        docs.append(demo_file.read_text())

    _perform_encoding(docs)
    print("🎉 MemVid encoding complete!")


def main():
    """Used for command-line execution."""
    encode_documents_from_kb_dir()

if __name__ == "__main__":
    main()