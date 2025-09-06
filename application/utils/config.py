from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
email = os.getenv("email")
password = os.getenv("email")

MODEL = "gpt-5-nano-2025-08-07"

TEMPERATURE = 0.2


