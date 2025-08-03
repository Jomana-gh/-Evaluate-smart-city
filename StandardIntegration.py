import streamlit as st
import pandas as pd

# Load data
file_path = 'final_merged_riyadh_data.xlsx'
data = pd.read_excel(file_path)

# Sidebar for user input
st.sidebar.title("اختيار المعايير لترتيب الأحياء")
selected_metric = st.sidebar.selectbox("اختر المعيار", 
                                      ['HCI', 'PublicStation', 'PopulationDensity', 'CDD', 'HDD'])

# Clean column names by stripping spaces
data.columns = data.columns.str.strip()

# Ensure that the necessary columns are treated as numeric
data['PublicStation'] = pd.to_numeric(data['PublicStation'], errors='coerce')
data['PopulationDensity'] = pd.to_numeric(data['PopulationDensity'], errors='coerce')
data['CDD'] = pd.to_numeric(data['CDD'], errors='coerce')  # Changed CoolingScore to CDD
data['HDD'] = pd.to_numeric(data['HDD'], errors='coerce')  # Adding the new HDD metric

# Function to rank neighborhoods based on selected metric
def rank_neighborhoods(metric):
    # Sort based on the selected metric
    sorted_data = data.sort_values(by=metric, ascending=False).reset_index(drop=True)
    
    # Calculate percentiles to define classification
    high_threshold = sorted_data[metric].quantile(0.66)
    low_threshold = sorted_data[metric].quantile(0.33)

    # Assign categories based on percentile thresholds
    def categorize(x):
        if x >= high_threshold:
            return 'High'
        elif x <= low_threshold:
            return 'Low'
        else:
            return 'Medium'

    sorted_data['Classification'] = sorted_data[metric].apply(categorize)
    
    return sorted_data

# Display the sorted and categorized neighborhoods in the sidebar
sorted_data = rank_neighborhoods(selected_metric)
st.sidebar.write(f"Ranking based on {selected_metric}")
st.sidebar.write(sorted_data[['Neighborhood', selected_metric, 'Classification']])

# Display map with markers based on the ranking
import folium

# Initialize map
m = folium.Map(location=[24.7136, 46.6753], zoom_start=12)

# Add markers to map
for _, row in sorted_data.iterrows():
    color = 'green' if row['Classification'] == 'High' else 'blue' if row['Classification'] == 'Medium' else 'red'
    folium.Marker([row['Latitude_x'], row['Longitude_x']], 
                  popup=f"{row['Neighborhood']} - {row[selected_metric]}",
                  icon=folium.Icon(color=color)).add_to(m)

# Display the map
st.write("الخريطة مع تصنيف الأحياء:")
st.components.v1.html(m._repr_html_(), width=700, height=500)