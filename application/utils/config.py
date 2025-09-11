from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
email = os.getenv("email")
password = os.getenv("password")
API_TOKEN = os.getenv("API_TOKEN")
ACTOR_ID = os.getenv("ACTOR_ID")

API_URL = f"https://api.apify.com/v2/acts/{ACTOR_ID}/run-sync-get-dataset-items?token={API_TOKEN}"


MODEL_1 = "gpt-5-nano-2025-08-07"
MODEL = "gpt-5-mini-2025-08-07"
MODEL_3 = "gpt-5-2025-08-07"

TEMPERATURE = 0.2


