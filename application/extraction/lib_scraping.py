from linkedin_api import Linkedin
import pandas as pd
import re
from utils import config as Config

# --- LOGIN ---

# Authenticate
api = Linkedin(Config.email, Config.password)

def extract_profile_data(profile_url):

    # --- YOUR PROFILE LINK ---
    profile_url = "https://www.linkedin.com/in/muhammad-usman-ali-251139129"

    # Extract username from URL (everything after '/in/')
    username = re.search(r"linkedin\.com/in/([^/]+)/?", profile_url)
    if username:
        username = username.group(1)
    else:
        raise ValueError("Invalid LinkedIn profile URL")

    # --- SCRAPE PROFILE ---
    profile = api.get_profile(username)

    # Extract fields
    data = {
        "name": profile.get("firstName", "") + " " + profile.get("lastName", ""),
        "headline": profile.get("headline", ""),
        "summary": profile.get("summary", ""),
        "experience": profile.get("experience", []),
        "education": profile.get("education", []),
        "skills": profile.get("skills", [])
    }

    print("\n--- Extracted Profile Data ---")
    print(data)

    return data

    # # --- Save to CSV ---
    # df = pd.DataFrame([data])
    # df.to_csv("linkedin_profile.csv", index=False)
    # print("✅ Profile data saved to linkedin_profile.csv")
