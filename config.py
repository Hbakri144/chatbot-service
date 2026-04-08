import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_USER = os.getenv("API_USER")
API_PASS = os.getenv("API_PASS")

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "aya"
