import ttkbootstrap as tb  # Modern theming for Tkinter UI
import tkinter as tk
from ttkbootstrap.constants import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time
import threading
import urllib.parse

# List of Riyadh neighborhoods (used in dropdown)
neighborhoods_list = [
    "الملز", "الروضة", "الشميسي", "العزيزية", "السويدي",
    "الياسمين", "النرجس", "العليا", "الصحافة", "بنبان"
]

# Initializes the Selenium Chrome WebDriver
def initialize_driver():
    options = ChromeOptions()
    options.add_experimental_option("detach", True)  # Keeps the browser open after script ends
    return webdriver.Chrome(options=options)

# Collects data for a single neighborhood and place type
def collect_for_neighborhood(place, neighborhood, collected_data, driver):
    # Format the Google Maps search query
    search_query = f"{place} في حي {neighborhood} الرياض"
    encoded_query = urllib.parse.quote(search_query)
    url = f"https://www.google.com/maps/search/{encoded_query}"
    
    output_box.insert(END, f"\nSearching in: {neighborhood}\n")
    output_box.see(END)

    try:
        driver.get(url)

        # Wait for the scrollable search results to load
        scrollable_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@aria-label, "نتائج عن")]'))
        )

        # Keep scrolling until no new results are loaded
        while True:
            before = len(driver.find_elements(By.XPATH, '//div[contains(@class,"Nv2PK")]'))
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
            time.sleep(2)
            after = len(driver.find_elements(By.XPATH, '//div[contains(@class,"Nv2PK")]'))
            if after == before:
                break

        # Loop through all result cards
        cards = driver.find_elements(By.XPATH, '//div[contains(@class,"Nv2PK")]')
        for idx, card in enumerate(cards):
            try:
                # Scroll to and click each card
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", card)
                ActionChains(driver).move_to_element(card).click().perform()
                time.sleep(2)

                # Extract place name
                name = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//h1[contains(@class,"DUwDvf")]'))
                ).text

                # Extract location/address
                location = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '(//div[contains(@class,"Io6YTe")])[1]'))
                ).text

                # Save the data to the list
                collected_data.append({
                    'Neighborhood': neighborhood,
                    'Name': name,
                    'Location': location
                })

                output_box.insert(END, f"{name} | {location} | Neighborhood: {neighborhood}\n")
                output_box.see(END)

            except Exception as e:
                output_box.insert(END, f"Error: {e}\n")
                output_box.see(END)

    except Exception as e:
        output_box.insert(END, f"Failed in {neighborhood}: {e}\n")
        output_box.see(END)

# Triggered when the user clicks the search button
def run_scraper():
    place = place_entry.get().strip()
    selected_nbh = nbh_combo.get().strip()
    manual_nbh = manual_entry.get().strip()

    neighborhoods = []
    if selected_nbh:
        neighborhoods.append(selected_nbh)
    if manual_nbh:
        neighborhoods.append(manual_nbh)

    if not place or not neighborhoods:
        tb.dialogs.Messagebox.show_warning("Please enter the place name and at least one neighborhood.")
        return

    # Run scraper in a separate thread (prevents UI freezing)
    threading.Thread(target=start_scraping, args=(place, neighborhoods)).start()

# Main scraping logic and CSV saving
def start_scraping(place, neighborhoods):
    driver = initialize_driver()
    data = []

    for nbh in neighborhoods:
        collect_for_neighborhood(place, nbh, data, driver)

    df = pd.DataFrame(data)
    df.drop_duplicates(inplace=True)
    df.to_csv("results.csv", index=False)
    tb.dialogs.Messagebox.ok("Saved", f"{len(data)} results saved in results.csv")
    driver.quit()

# ============ GUI ============ #
app = tb.Window(themename="flatly")  
app.title("Google Maps Data Collection Tool")
app.geometry("750x600")

tb.Label(app, text="🔹 Place name:", font=("Arial", 12)).pack(pady=5)
place_entry = tb.Entry(app, width=50, font=("Arial", 11))
place_entry.pack(pady=5)

tb.Label(app, text="Select a neighborhood (optional):").pack(pady=5)
nbh_combo = tb.Combobox(app, values=neighborhoods_list, width=40, font=("Arial", 11))
nbh_combo.pack(pady=5)

tb.Label(app, text="Or type a neighborhood manually:").pack(pady=5)
manual_entry = tb.Entry(app, width=40, font=("Arial", 11))
manual_entry.pack(pady=5)

tb.Button(app, text="Start Search", bootstyle=SUCCESS, command=run_scraper).pack(pady=10)

output_box = tk.Text(app, height=25, font=("Consolas", 10))
output_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

app.mainloop()
