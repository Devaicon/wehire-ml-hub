import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


VERIFY_LOGIN_ID = "global-nav__primary-link"
REMEMBER_PROMPT = "remember-me-prompt__form-primary"


def login(driver, email, password):
    driver.get("https://www.linkedin.com/login")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
    driver.find_element(By.ID, "username").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "password").submit()

    try:
        code_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "input__email_verification_pin"))
        )
        print("[INFO] LinkedIn requires verification code.")

        # Ask user to enter code manually in terminal
        code = input("Enter the LinkedIn verification code: ")

        code_input.send_keys(code)
        code_input.submit()
        print("[INFO] Verification code submitted.")

    except:
        print("[INFO] No verification code required.")

    time.sleep(3)
    try:
        code_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "input__email_verification_pin"))
        )
        print("[INFO] Waiting for LinkedIn verification code in email...")
        code = None
        for _ in range(10):  # Try for up to ~50 seconds
            code = fetch_linkedin_code(email, password)
            if code:
                break
            time.sleep(5)
        if not code:
            raise Exception("Verification code not found in email.")
        code_input.send_keys(code)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        print("[INFO] Verification code submitted.")
        time.sleep(3)
    except Exception as e:
        print(f"[INFO] No verification prompt or error: {e}")


from selenium.common.exceptions import NoSuchElementException


def get_element_text_or_none(driver, by, value):
    """
    Tries to find an element by given locator and return its text.
    Returns None if element is not found.
    """
    try:
        return driver.find_element(by, value).text.strip()
    except NoSuchElementException:
        return None


def extract_experience(driver):
    print("\n--- EXPERIENCE ---")

    # Wait for the Experience section
    try:
        exp_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//section[contains(., 'Experience')]")
            )
        )
    except:
        print("[ERROR] Experience section not found.")
        return

    # Find all experience list items
    experience_items = driver.find_elements(
        By.XPATH,
        "//section[contains(@class, 'experience') or contains(., 'Experience')]//li[contains(@class, 'artdeco-list__item')]",
    )

    for idx, item in enumerate(experience_items):
        try:
            title = item.find_element(
                By.XPATH, ".//div[contains(@class, 't-bold')]"
            ).text.strip()
        except:
            title = None

        try:
            company = item.find_element(
                By.XPATH, ".//span[contains(text(),'·')]"
            ).text.strip()
        except:
            company = None

        try:
            date_range = item.find_element(
                By.XPATH, ".//span[contains(@class,'pvs-entity__caption-wrapper')]"
            ).text.strip()
        except:
            date_range = None

        try:
            location = item.find_elements(By.XPATH, ".//span")[3].text.strip()
        except:
            location = None

        print(f"\nRole #{idx + 1}")
        print(f"Title    : {title}")
        print(f"Company  : {company}")
        print(f"Duration : {date_range}")
        print(f"Location : {location}")


def extract_education(driver):
    education_list = []

    # Scroll into education section to ensure it's loaded
    try:
        edu_section = driver.find_element(
            By.XPATH, "//section[.//h2[contains(., 'Education')]]"
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", edu_section)
    except:
        print("Education section not found.")
        return []

    # Now find all education entries (each <li>)
    edu_blocks = edu_section.find_elements(
        By.XPATH, ".//li[contains(@class, 'artdeco-list__item')]"
    )

    print(f"[DEBUG] Found {len(edu_blocks)} education blocks")

    for block in edu_blocks:
        try:
            school = block.find_element(
                By.XPATH,
                ".//span[contains(@aria-hidden, 'true') and contains(text(), '')]",
            ).text.strip()
        except:
            school = None

        try:
            degree_field = block.find_element(
                By.XPATH, ".//span[contains(@class, 't-14') and contains(text(), ',')]"
            ).text.strip()
        except:
            degree_field = None

        try:
            dates = block.find_element(
                By.XPATH, ".//span[contains(@class,'t-black--light')]/span"
            ).text.strip()
        except:
            dates = None

        try:
            grade = block.find_element(
                By.XPATH, ".//span[contains(text(), 'Grade')]"
            ).text.strip()
        except:
            grade = None

        # Specializations or extra details
        try:
            details = block.find_elements(
                By.XPATH,
                ".//div[contains(@class,'inline-show-more-text--is-collapsed')]/span",
            )
            description = None
            for el in details:
                if "Grade" not in el.text:
                    description = el.text.strip()
                    break
        except:
            description = None

        education_list.append(
            {
                "school": school,
                "degree_field": degree_field,
                "dates": dates,
                "grade": grade,
                "description": description,
            }
        )

        print("==== Education Entry ====")
        print(f"School      : {school}")
        print(f"Degree      : {degree_field}")
        print(f"Dates       : {dates}")
        print(f"Grade       : {grade}")
        print(f"Description : {description}")
        print("=========================\n")

    return education_list


def extract_projects(driver):
    projects_text = ""
    time.sleep(2)

    try:
        # Scroll to the projects section
        projects_section = driver.find_element(
            By.XPATH, "//section[.//h2//span[text()='Projects']]"
        )
        driver.execute_script("arguments[0].scrollIntoView();", projects_section)
        time.sleep(1)

        project_items = projects_section.find_elements(
            By.XPATH, ".//li[contains(@class, 'artdeco-list__item')]"
        )

        for idx, item in enumerate(project_items):
            try:
                title = item.find_element(
                    By.XPATH, ".//div[contains(@class, 't-bold')]//span[1]"
                ).text.strip()
            except:
                title = "N/A"

            try:
                date_range = item.find_element(
                    By.XPATH, ".//span[contains(@class, 't-14')]//span[1]"
                ).text.strip()
            except:
                date_range = "N/A"

            try:
                associated_with = item.find_element(
                    By.XPATH, ".//div[contains(text(),'Associated')]"
                ).text.strip()
            except:
                associated_with = "N/A"

            try:
                description = item.find_element(
                    By.XPATH,
                    ".//div[contains(@class,'inline-show-more-text')]//span[1]",
                ).text.strip()
            except:
                description = "N/A"

            projects_text += f"\nProject #{idx + 1}\n"
            projects_text += f"Title          : {title}\n"
            projects_text += f"Duration       : {date_range}\n"
            projects_text += f"Associated With: {associated_with}\n"
            projects_text += f"Description    : {description}\n"

    except Exception as e:
        projects_text += f"\n[!] Projects section not found: {str(e)}\n"

    return projects_text


def extract_skills(driver):
    skills_text = ""
    time.sleep(2)

    try:
        # Scroll to skills section
        skills_section = driver.find_element(
            By.XPATH, "//section[.//h2//span[text()='Skills']]"
        )
        driver.execute_script("arguments[0].scrollIntoView();", skills_section)
        time.sleep(1)

        # Find all skill list items
        skill_items = skills_section.find_elements(
            By.XPATH, ".//li[contains(@class, 'pvs-list__paged-list-item')]"
        )

        for idx, item in enumerate(skill_items):
            # Extract skill name
            try:
                skill_name = item.find_element(
                    By.XPATH, ".//a[@data-field='skill_page_skill_topic']//span[1]"
                ).text.strip()
            except:
                skill_name = "N/A"

            # Extract endorsement count (if any)
            try:
                endorsement = item.find_element(
                    By.XPATH,
                    ".//div[contains(@class, 'hoverable-link-text') and contains(@class, 't-14')]//span[1]",
                ).text.strip()
            except:
                endorsement = "No endorsements"

            skills_text += f"Skill #{idx + 1}: {skill_name} ({endorsement})\n"

    except Exception as e:
        skills_text += f"[!] Skills section not found or error occurred: {e}\n"

    return skills_text


def extract_profile_info(driver):
    time.sleep(3)  # Let profile load
    full_profile_text = "\n=== PROFILE INFO ===\n"

    name = get_element_text_or_none(
        driver,
        By.XPATH,
        "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[1]/div[1]/span/a/h1",
    )
    title = get_element_text_or_none(
        driver, By.CSS_SELECTOR, "div.text-body-medium.break-words"
    )
    location = get_element_text_or_none(
        driver,
        By.XPATH,
        "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[2]/span[1]",
    )

    time.sleep(1)
    about = get_element_text_or_none(
        driver,
        By.XPATH,
        "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[3]/div[3]/div/div/div/span[1]",
    )

    full_profile_text += f"Name: {name}\n"
    full_profile_text += f"Title: {title}\n"
    full_profile_text += f"Location: {location}\n"

    full_profile_text += "\n--- ABOUT ---\n"
    full_profile_text += f"About: {about}\n"

    # Scroll to load sections
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    full_profile_text += "\n--- EXPERIENCE ---\n"
    experience_text = ""

    time.sleep(1)

    experience_items = driver.find_elements(
        By.XPATH,
        "//section[contains(@class, 'experience') or contains(., 'Experience')]//li[contains(@class, 'artdeco-list__item')]",
    )

    for idx, item in enumerate(experience_items):
        try:
            title = item.find_element(
                By.XPATH, ".//div[contains(@class, 't-bold')]"
            ).text.strip()
        except:
            title = None

        try:
            company = item.find_element(
                By.XPATH, ".//span[contains(text(),'·')]"
            ).text.strip()
        except:
            company = None

        try:
            date_range = item.find_element(
                By.XPATH, ".//span[contains(@class,'pvs-entity__caption-wrapper')]"
            ).text.strip()
        except:
            date_range = None

        try:
            location = item.find_elements(By.XPATH, ".//span")[3].text.strip()
        except:
            location = None

        experience_text += f"\nRole #{idx + 1}\n"
        experience_text += f"Title    : {title}\n"
        experience_text += f"Company  : {company}\n"
        experience_text += f"Duration : {date_range}\n"
        experience_text += f"Location : {location}\n"

    full_profile_text += experience_text

    time.sleep(1)

    full_profile_text += "\n--- EDUCATION ---\n"
    education_list = extract_education(driver)

    for idx, edu in enumerate(education_list):
        full_profile_text += f"\nEducation #{idx + 1}\n"
        full_profile_text += f"School      : {edu['school']}\n"
        full_profile_text += f"Degree      : {edu['degree_field']}\n"
        full_profile_text += f"Dates       : {edu['dates']}\n"
        full_profile_text += f"Grade       : {edu['grade']}\n"
        full_profile_text += f"Description : {edu['description']}\n"

    time.sleep(1)

    full_profile_text += "\n--- PROJECTS ---\n"
    full_profile_text += extract_projects(driver)

    time.sleep(3)

    try:
        print(">>>>")
        # Find all <a> elements with class 'optional-action-target-wrapper'
        links = driver.find_elements(
            By.CSS_SELECTOR, "a.optional-action-target-wrapper"
        )

        # Loop through and click the one that starts with "Show all" and links to skills
        clicked = False
        for link in links:
            text = link.text.strip()
            href = link.get_attribute("href")
            if text.startswith("Show all") and "/details/skills" in href:
                link.click()
                clicked = True
                print("✅ Clicked the Show all skills link!")
                break

        if not clicked:
            print("⚠️ Could not find the Show all skills link.")

        # Optionally wait to see the result
        time.sleep(5)

        element = driver.find_element(
            By.XPATH,
            "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section/div[2]/div[2]",
        )
        print(element.text)

        full_profile_text += "\n--- SKILLS ---\n"
        full_profile_text += element.text
    except:
        print(".........")

    return full_profile_text


import imaplib
import email
import re


def fetch_linkedin_code(email_user, email_pass):
    # Connect to Gmail IMAP
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(email_user, email_pass)
    mail.select("inbox")
    # Search for LinkedIn verification emails
    result, data = mail.search(
        None, '(FROM "security-noreply@linkedin.com" SUBJECT "verification code")'
    )
    ids = data[0].split()
    if not ids:
        return None
    latest_id = ids[-1]
    result, data = mail.fetch(latest_id, "(RFC822)")
    raw_email = data[0][1]
    msg = email.message_from_bytes(raw_email)
    # Get email body
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode()
                break
    else:
        body = msg.get_payload(decode=True).decode()
    # Extract 6-digit code
    match = re.search(r"\b(\d{6})\b", body)
    if match:
        return match.group(1)
    return None


def get_linkedin_profile_text(profile_url):
    chromedriver_path = "/usr/local/bin/chromedriver"

    # ✅ Add headless option
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless=new")   # modern headless mode

    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)

    from security import config

    login(driver, config.email, config.password)
    print("[INFO] Logged in successfully.")
    driver.save_screenshot("full_page.png")
    time.sleep(5)

    driver.get(profile_url)
    print(f"[INFO] Navigated to profile: {profile_url}")

    time.sleep(5)

    # Get main element
    element = driver.find_element(
        "xpath", "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main"
    )

    # Get excluded element text
    exclude_element = driver.find_element(
        "xpath",
        "/html/body/div[6]/div[3]/div/div/div[2]/div/div/main/section[5]/div[4]",
    )

    # Remove excluded text from the full text
    full_profile_text = element.text.replace(exclude_element.text, "")

    # try:
    #     WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.TAG_NAME, "main"))
    #     )
    #     print("[INFO] Profile page loaded.")
    # except:
    #     print("[WARNING] Profile page may not have fully loaded.")

    # # ⬇️ Call and capture text
    # full_profile_text = extract_profile_info(driver)

    # print("[INFO] Profile saved to linkedin_profile.txt")

    print("full_profile_text: ", full_profile_text)

    return full_profile_text


if __name__ == "__main__":
    profile_url = "https://www.linkedin.com/in/muhammad-usman-ali-251139129"
    get_linkedin_profile_text(profile_url)
