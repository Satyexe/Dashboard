# File: scrape_certin_links.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import csv
import time

def get_advisory_links():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in background
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.cert-in.org.in/s2cMainServlet?pageid=PUBADVLIST")

    time.sleep(5)  # wait for JS to load

    links = []
    elements = driver.find_elements(By.XPATH, '//a[contains(@href, "pageid=PUBADVVIEW")]')

    for el in elements:
        href = el.get_attribute('href')
        if href not in links:
            links.append(href)

    driver.quit()
    return links

def save_links_to_csv(links, filename="certin_advisory_links.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Advisory URL'])
        for link in links:
            writer.writerow([link])
    print(f"[✅] Saved {len(links)} advisory links to {filename}")

if __name__ == "__main__":
    links = get_advisory_links()
    save_links_to_csv(links)
