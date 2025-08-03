import ttkbootstrap as tb # type: ignore
import tkinter as tk
from ttkbootstrap.constants import * # type: ignore
from selenium import webdriver # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore
from selenium.webdriver.chrome.options import Options as ChromeOptions # type: ignore
from selenium.webdriver.common.action_chains import ActionChains # type: ignore
import pandas as pd # type: ignore
import time
import threading
import urllib.parse

# أحياء الرياض (مثال)
neighborhoods_list = [
    "الملز", "الروضة", "الشميسي", "العزيزية", "السويدي",
    "الياسمين", "النرجس", "العليا", "الصحافة", "بنبان"
]

def initialize_driver():
    options = ChromeOptions()
    options.add_experimental_option("detach", True)
    return webdriver.Chrome(options=options)

def collect_for_neighborhood(place, neighborhood, collected_data, driver):
    search_query = f"{place} في حي {neighborhood} الرياض"
    encoded_query = urllib.parse.quote(search_query)
    url = f"https://www.google.com/maps/search/{encoded_query}"
    output_box.insert(END, f"\n البحث في: {neighborhood}\n")
    output_box.see(END)

    try:
        driver.get(url)

        scrollable_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@aria-label, "نتائج عن")]'))
        )

        while True:
            before = len(driver.find_elements(By.XPATH, '//div[contains(@class,"Nv2PK")]'))
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
            time.sleep(2)
            after = len(driver.find_elements(By.XPATH, '//div[contains(@class,"Nv2PK")]'))
            if after == before:
                break

        cards = driver.find_elements(By.XPATH, '//div[contains(@class,"Nv2PK")]')
        for idx, card in enumerate(cards):
            try:
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", card)
                ActionChains(driver).move_to_element(card).click().perform()
                time.sleep(2)

                name = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//h1[contains(@class,"DUwDvf")]'))
                ).text

                location = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '(//div[contains(@class,"Io6YTe")])[1]'))
                ).text

                collected_data.append({
                    'Neighborhood': neighborhood,
                    'Name': name,
                    'Location': location
                })

                output_box.insert(END, f" {name} | {location} | حي: {neighborhood}\n")
                output_box.see(END)

            except Exception as e:
                output_box.insert(END, f" خطأ: {e}\n")
                output_box.see(END)

    except Exception as e:
        output_box.insert(END, f" فشل في {neighborhood}: {e}\n")
        output_box.see(END)

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
        tb.dialogs.Messagebox.show_warning("يرجى إدخال اسم المكان واسم الحي أو اختياره.")
        return

    threading.Thread(target=start_scraping, args=(place, neighborhoods)).start()

def start_scraping(place, neighborhoods):
    driver = initialize_driver()
    data = []

    for nbh in neighborhoods:
        collect_for_neighborhood(place, nbh, data, driver)

    df = pd.DataFrame(data)
    df.drop_duplicates(inplace=True)
    df.to_csv("results.csv", index=False)
    tb.dialogs.Messagebox.ok("تم الحفظ", f"تم جمع {len(data)} نتيجة في ملف results.csv")
    driver.quit()

# ============ واجهة الاستخدام ============ #
app = tb.Window(themename="flatly")  
app.title("أداة جمع بيانات من Google Maps")
app.geometry("750x600")

tb.Label(app, text="🔹 اسم المكان:", font=("Arial", 12)).pack(pady=5)
place_entry = tb.Entry(app, width=50, font=("Arial", 11))
place_entry.pack(pady=5)

tb.Label(app, text=" اختر حي من القائمة (اختياري):").pack(pady=5)
nbh_combo = tb.Combobox(app, values=neighborhoods_list, width=40, font=("Arial", 11))
nbh_combo.pack(pady=5)

tb.Label(app, text=" أو اكتب اسم حي يدويًا:").pack(pady=5)
manual_entry = tb.Entry(app, width=40, font=("Arial", 11))
manual_entry.pack(pady=5)

tb.Button(app, text=" ابدأ البحث", bootstyle=SUCCESS, command=run_scraper).pack(pady=10)

output_box = tk.Text(app, height=25, font=("Consolas", 10))
output_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

app.mainloop()

