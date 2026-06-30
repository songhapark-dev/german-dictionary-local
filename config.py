# config.py
import os
from dotenv import load_dotenv

# .env code
load_dotenv()

# taking key from .env file
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
DB_NAME = "vocab_app.db"