# Navigate to project folder
cd C:\Users\hp\FlaskDeploymentProject\field_rag_agent

# Create venv if not exists
if (-not (Test-Path "venv")) { python -m venv venv }

# Activate venv
.\venv\Scripts\Activate

# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r ..\requirements.txt

Write-Host "✅ Virtual environment ready."

# Optional: Run AI setup
python setup_env.py
python encode_kb.py

# Run Flask app
cd ..
$env:FLASK_APP="app"
$env:FLASK_ENV="development"
flask run
