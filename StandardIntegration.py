import streamlit as st
import pandas as pd
import folium

# Load data from Excel file
file_path = 'final_merged_riyadh_data.xlsx'
data = pd.read_excel(file_path)

# Sidebar for user input - select ranking metric
st.sidebar.title("Select Criteria to Rank Neighborhoods")
selected_metric = st.sidebar.selectbox("Choose metric", 
                                       ['HCI', 'PublicStation', 'PopulationDensity', 'CDD', 'HDD'])

# Clean column names by stripping spaces (if any)
data.columns = data.columns.str.strip()

# Convert columns to numeric to avoid errors during sorting or calculations
data['PublicStation'] = pd.to_numeric(data['PublicStation'], errors='coerce')
data['PopulationDensity'] = pd.to_numeric(data['PopulationDensity'], errors='coerce')
data['CDD'] = pd.to_numeric(data['CDD'], errors='coerce')  # Cooling Degree Days
data['HDD'] = pd.to_numeric(data['HDD'], errors='coerce')  # Heating Degree Days

# Function to rank neighborhoods based on the selected metric
def rank_neighborhoods(metric):
    
    # Sort neighborhoods descendingly by metric
    sorted_data = data.sort_values(by=metric, ascending=False).reset_index(drop=True)
    
    # Calculate thresholds for classification
    high_threshold = sorted_data[metric].quantile(0.66)
    low_threshold = sorted_data[metric].quantile(0.33)
    
    # Classification function based on thresholds
    def categorize(value):
        if value >= high_threshold:
            return 'High'
        elif value <= low_threshold:
            return 'Low'
        else:
            return 'Medium'
    
    # Apply classification to the metric column
    sorted_data['Classification'] = sorted_data[metric].apply(categorize)
    
    return sorted_data

# Rank the neighborhoods using the selected metric
sorted_data = rank_neighborhoods(selected_metric)

# Display ranking table in the sidebar
st.sidebar.write(f"Ranking based on {selected_metric}")
st.sidebar.write(sorted_data[['Neighborhood', selected_metric, 'Classification']])

# Create a Folium map centered on Riyadh coordinates
m = folium.Map(location=[24.7136, 46.6753], zoom_start=12)

# Add markers for each neighborhood on the map
for _, row in sorted_data.iterrows():
    # Choose marker color based on classification
    if row['Classification'] == 'High':
        color = 'green'
    elif row['Classification'] == 'Medium':
        color = 'blue'
    else:
        color = 'red'
    
    # Add marker with popup showing neighborhood name and metric value
    folium.Marker(
        [row['Latitude_x'], row['Longitude_x']],
        popup=f"{row['Neighborhood']} - {row[selected_metric]}",
        icon=folium.Icon(color=color)
    ).add_to(m)

# Display the map in Streamlit app
st.write("Map showing neighborhoods classification:")
st.components.v1.html(m._repr_html_(), width=700, height=500)
