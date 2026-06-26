from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import pymongo

# 1. Connected to local mongodb instance
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["linked_in_db"]
collection = db["jobs"]
encoded_keyword = input("Enter the role which you want to search:")

options = webdriver.ChromeOptions()
profile_dir = r"C:\Users\Admin\.vscode\linkedin_browser_profile"
options.add_argument(f"user-data-dir={profile_dir}")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
options.add_experimental_option("excludeSwitches",["enableAutomation"])
options.add_experimental_option("useAutomationExtension",False)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",{
    "source":"delete Navigator.prototype.webdriver;"
})
driver.get(f'https://www.linkedin.com/jobs/search/?keywords="{encoded_keyword}"&location=remotely')
time.sleep(5)

url_data = []
job_data = []

container = driver.find_elements(By.XPATH,"//div[contains(@class,'job-card-container--clickable')]")
for job in container:
    job_link = job.find_element(By.XPATH,".//a")
    job_url = job_link.get_attribute("href")
    job_title = job.find_element(By.XPATH,".//span//strong").text
    url_data.append(job_url)
    job_data.append(job_title)
    time.sleep(0.5)

driver.quit()
# Create a structured dictionary payload
for title, link in zip(job_data,url_data):
    # building a clean payload for a single job

    payload = {
        "title":title,
        "link":link
        }
    # Prevent duplicates by updating if it exists or inserting if it doesn't
    collection.update_one(
        {"url":link} ,      # 1st dict: Search filter
        {"$set":payload},   # 2nd dict: What to update/insert
        upsert = True       # Create document if it doesn't exist
    )
print ("Saved data sucessfully!!!")
