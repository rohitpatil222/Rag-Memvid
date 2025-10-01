# run.py (FIXED CONTENT)
from app import create_app

# Create the application instance
app = create_app()

if __name__ == "__main__":
    # Flask's built-in run command is used here for direct execution
    app.run(host="127.0.0.1", port=5000, debug=True)