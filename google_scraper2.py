import ttkbootstrap as tb
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

def initialize_driver():
    options = ChromeOptions()
    options.add_experimental_option("detach", True)
    return webdriver.Chrome(options=options)

def collect_from_link(link, collected_data, driver):
    output_box.insert(tk.END, f"\n  جارٍ البحث في الرابط...\n", "right")
    output_box.see(tk.END)

    try:
        driver.get(link)

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

                neighborhood = extract_neighborhood_from_address(location)

                collected_data.append({
                    'Neighborhood': neighborhood,
                    'Name': name,
                    'Location': location
                })

                output_box.insert(tk.END, f"{name} | {location} | حي: {neighborhood}\n", "right")
                output_box.see(tk.END)

            except Exception as e:
                output_box.insert(tk.END, f" خطأ: {e}\n", "right")
                output_box.see(tk.END)

    except Exception as e:
        output_box.insert(tk.END, f" فشل في الرابط: {e}\n", "right")
        output_box.see(tk.END)

def extract_neighborhood_from_address(address):
    # نحاول استخراج اسم الحي من العنوان بناءً على التنسيق
    parts = address.split(',')
    if parts:
        return parts[0].strip()
    return "غير معروف"

def run_scraper():
    link = link_entry.get().strip()

    if not link.startswith("http"):
        tb.dialogs.Messagebox.show_warning("يرجى إدخال رابط صحيح لنتائج البحث من خرائط Google")
        return

    threading.Thread(target=start_scraping, args=(link,), daemon=True).start()

def start_scraping(link):
    driver = initialize_driver()
    data = []

    collect_from_link(link, data, driver)

    df = pd.DataFrame(data)
    df.to_csv("results.csv", index=False)
    app.after(0, lambda: tb.dialogs.Messagebox.ok("تم الحفظ", f"تم جمع {len(data)} نتيجة في ملف results.csv"))
    driver.quit()

# ============ واجهة الاستخدام ============ #
app = tb.Window(themename="flatly")
app.title("أداة جمع بيانات من Google Maps")
app.geometry("750x600")

tb.Label(app, text=" أدخل رابط من خرائط Google:", font=("Arial", 12)).pack(pady=5)
link_entry = tb.Entry(app, width=70, font=("Arial", 11))
link_entry.pack(pady=5)

tb.Button(app, text=" ابدأ البحث", bootstyle=SUCCESS, command=run_scraper).pack(pady=10)

output_box = tk.Text(app, height=25, font=("Consolas", 10))
output_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
output_box.tag_configure("right", justify='right')

app.mainloop()
