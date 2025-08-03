# Riyadh Neighborhoods Dashboard

A data-driven interactive dashboard to visualize and rank neighborhoods in Riyadh based on selected indicators such as:

- Human-Centered Index (HCI)
- Number of Public Stations
- Population Density
- Cooling Degree Days (CDD)
- Heating Degree Days (HDD)

---

##  Goal

This tool helps urban planners, researchers, and decision-makers analyze Riyadh neighborhoods and understand how they align with smart city standards using various environmental and infrastructural indicators.

---

##  Dataset

Combined Excel dataset: `final_merged_riyadh_data.xlsx`

**Columns:**

- `Neighborhood`: Name of the district
- `Latitude`, `Longitude`: Coordinates
- `HCI`: Human-Centered Index
- `PublicStation`: Number of public service stations
- `PopulationDensity`
- `CDD`: Cooling Degree Days
- `HDD`: Heating Degree Days

---

##  Files Overview

The project consists of two main components:

### 1.  Streamlit Dashboard – `StandardIntegration.py`

- Built with Python and **Streamlit**.
- Uses `folium` via `streamlit-folium` to render interactive maps.
- Supports filtering and ranking based on multiple indicators.
- Works as a standalone interface for quick exploration.

---

### 2.  React + Flask Interactive Web App

#### 2.1  Backend – Flask API (`app.py`)

- Serves as the **backend data provider** for the React app.
- Loads and processes the main dataset.
- Computes rankings and handles metric-based filtering.
- Supplies GeoJSON-like neighborhood data (lat/lon) for mapping.

#### 2.2  Frontend – React (`frontend/`)

- Built with **ReactJS** and **Mapbox GL JS**.
- Main files:
  - `MapComponent.jsx`:  
    - Renders interactive map with neighborhood markers.  
    - Displays popups, handles filtering and user interactions.
  - `app.js`:  
    - Entry point of the app.  
    - Handles app state and renders the map component.

---

