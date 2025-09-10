import requests
from utils import config as Config
def extract_profile_data(profile_url: str) -> dict:
    """
    Fetch full LinkedIn profile data using Apify LinkedIn Profile Data Extractor.

    Args:
        profile_url (str): LinkedIn profile URL (e.g., https://www.linkedin.com/in/example)

    Returns:
        dict: Extracted profile data (full JSON response)
    """
    input_data = {
        "profile": profile_url,   # 👈 FIXED: actor expects "profile", not "profileUrls"
        "proxy": {"useApifyProxy": True, "apifyProxyCountry": "US"}
    }

    response = requests.post(Config.API_URL, json=input_data)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return {
            "error": f"Request failed with {response.status_code}",
            "details": response.text
        }



# # Example usage
# if __name__ == "__main__":
#     url = "https://www.linkedin.com/in/muhammad-usman-ali-251139129"
#     profile_data = get_linkedin_profile_data(url)
#     print(profile_data)
