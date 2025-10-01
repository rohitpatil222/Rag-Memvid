# app/__init__.py - FIXED
from flask import Flask

# Make sure this file is placed in an 'app' directory,
# e.g., 'app/__init__.py'
def create_app():
    app = Flask(__name__)

    # Import and register the Blueprint
    from .routes import bp
    app.register_blueprint(bp)

    # Optional: Load the MemVid agent at startup
    # Note: rag_agent.py handles lazy loading, so this is optional
    # from field_rag_agent.rag_agent import setup_memvid
    # with app.app_context():
    #     setup_memvid()

    return app