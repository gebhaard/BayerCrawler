import json
import os
import re
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

with open("projects.json", "r", encoding="utf-8") as f:
    project_dict = json.load(f)
    f.close()

project_list = {key: val["short"] for key, val in project_dict.items()}

print("You can choose from the following projects:")
for key, val in project_list.items():
    print(f"\tFor {key}, enter {val}")

project = input("Please enter the chosen project name: ").upper()
project = project

for key, value in project_dict.items():
    if project == value["short"]:
        url = value["url"]
        merger = value["merger"]
        short = value["short"]
        break

if project != value["short"]:
    print("Choose a valid project! Choose from the list above.")

else:
    pass

# Set up Selenium WebDriver
driver = webdriver.Chrome()  # Make sure ChromeDriver is in your PATH
driver.get(url)

# Click the "Load More" button until it disappears
while True:
    try:
        load_more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".g-loadmore .w-btn"))
        )
        load_more_button.click()
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element((By.CSS_SELECTOR, ".g-preloader"))
        )
    except Exception:
        break

# Get the page source after all items are loaded
r = driver.page_source
driver.quit()

soup = BeautifulSoup(r, "html.parser")

# Extract data from each card
cards = soup.find_all("article", class_="w-grid-item")
data = []

for idx, card in enumerate(cards):
    if not re.search(r"\bingatlan\b", card["class"][3]):
        continue
    print(f"Processing card {idx + 1} of {len(cards)}...", end="\r")
    try:
        azonosito = (
            card.find(
                "div", class_=re.compile(r"\bw-post-elm\b.*\busg_post_custom_field_7\b")
            )
            .find("span", class_=re.compile(r"\bw-post-elm-value\b"))
            .text.strip()
        )
        szobak = (
            card.find(
                "div", class_=re.compile(r"\bw-post-elm\b.*\busg_post_custom_field_4\b")
            )
            .find("span", class_=re.compile(r"\bw-post-elm-value\b"))
            .text.strip()
        )
        ar = (
            card.find(
                "div", class_=re.compile(r"\bw-post-elm\b.*\busg_post_custom_field_3\b")
            )
            .find("span", class_=re.compile(r"\bw-post-elm-value\b"))
            .text.strip()
        )
        terulet = (
            card.find(
                "div", class_=re.compile(r"\bw-post-elm\b.*\busg_post_custom_field_5\b")
            )
            .find("span", class_=re.compile(r"\bw-post-elm-value\b"))
            .text.strip()
        )
        emelet = (
            card.find(
                "div", class_=re.compile(r"\bw-post-elm\b.*\busg_post_custom_field_6\b")
            )
            .find("span", class_=re.compile(r"\bw-post-elm-value\b"))
            .text.strip()
        )
        img_tag = card.find(
            "img",
            class_=re.compile(
                r"\battachment-large\b.*\bsize-large\b.*\bwp-post-image\b"
            ),
        )
        if img_tag:
            img_link = img_tag["src"]
            if img_link.startswith("data:image/svg+xml"):
                img_link = img_tag.get("data-lazy-src", img_link)
        else:
            img_link = "None"

        data.append(
            {
                "Azonosító": azonosito,
                "Szobák": szobak,
                "Ár": ar,
                "Terület": terulet,
                "Emelet": emelet,
                "Kép link": '=HYPERLINK("' + img_link + '")',
            }
        )
    except Exception as e:
        print(f"Error processing card {idx + 1}: {e}")
        continue

# Convert to DataFrame
df = pd.DataFrame(data)

datetime_now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
os.makedirs("export", exist_ok=True)
df.to_excel(f"export/BayerProperty_{short}_Export_{datetime_now}.xlsx", index=False)
