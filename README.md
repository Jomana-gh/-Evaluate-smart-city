# -Evaluate-smart-city
# Riyadh Neighborhood Data Scraper 

##  Project Goal

To automate the collection of place data  from Riyadh neighborhoods, and analyze them against international standards for urban development and smart cities.

##  Project Structure

This repository includes two main tools:

### 1. `google_scraper_1.py` — Search by Place & Neighborhood
- GUI tool that allows the user to input a **place type** (e.g., hospital, school) and **select or write a Riyadh neighborhood**.
- Launches a Chrome browser, searches Google Maps, scrolls through results, and extracts:
  - Name
  - Location
  - Neighborhood
- Results are saved to `results.csv`.

### 2. `google_scraper_2.py` — Search by Google Maps Link
- GUI tool that accepts a direct **Google Maps search link**.
- Automatically scrolls and extracts data as above.
- Tries to **infer the neighborhood** from the location string.
