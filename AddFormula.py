import streamlit as st
import pandas as pd
import folium

# Load data
file_path = 'final_merged_riyadh_data.xlsx'
data = pd.read_excel(file_path)

# Clean column names by stripping spaces
data.columns = data.columns.str.strip()

# Ensure that the necessary columns are treated as numeric
data['Area_km2'] = pd.to_numeric(data['Area_km2'], errors='coerce').fillna(0)
data['Population_x'] = pd.to_numeric(data['Population_x'], errors='coerce').fillna(0)

# Sidebar for user input
st.sidebar.title("اختيار المعايير لترتيب الأحياء")
available_metrics = ['HCI', 'PublicStation', 'PopulationDensity', 'CDD', 'HDD', 'Custom Metric']

# Step 1: Add the custom metric to the available metrics list after it is calculated
selected_metric = st.sidebar.selectbox("اختر المعيار", available_metrics)

# Ensure that the necessary columns are treated as numeric and handle missing values
data['PublicStation'] = pd.to_numeric(data['PublicStation'], errors='coerce').fillna(0)
data['PopulationDensity'] = pd.to_numeric(data['PopulationDensity'], errors='coerce').fillna(0)
data['CDD'] = pd.to_numeric(data['CDD'], errors='coerce').fillna(0)
data['HDD'] = pd.to_numeric(data['HDD'], errors='coerce').fillna(0)

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

# Display table with rankings for basic metrics in the sidebar under the selection
if selected_metric != 'Custom Metric':
    st.sidebar.write(f"**جدول ترتيب الأحياء بناءً على {selected_metric}:**")
    ranked_data = rank_neighborhoods(selected_metric)
    st.sidebar.dataframe(ranked_data[['Neighborhood', selected_metric, 'Classification']])

# Add functionality for user to input a custom formula for a new metric
if selected_metric == 'Custom Metric':
    st.sidebar.subheader("أدخل معايير جديدة")
    equation_name = st.sidebar.text_input("اسم المعيار:")
    
    # Display available columns for the user to choose from
    available_columns = data.columns.tolist()
    
    # Step 1: Let the user choose the operation (Divide, Multiply, Add, Subtract)
    operation = st.sidebar.selectbox("اختر العملية الحسابية", ["قسمة", "ضرب", "جمع", "طرح"])
    
    # Step 2: Let the user select columns to be used in the operation
    selected_columns = st.sidebar.multiselect("اختر الأعمدة للاستخدام في المعادلة", available_columns)

    # Step 3: Let the user input a constant number for multiplication or division (Optional)
    use_constant = st.sidebar.checkbox("استخدام قيمة ثابتة (مثل ضرب أو قسمة على 100)", value=False)
    constant_value = st.sidebar.number_input("إدخل قيمة ثابتة للقسمة أو الضرب", min_value=0, value=100) if use_constant else 1

    equation_input = ""
    
    # Step 4: Automatically generate and apply the formula
    if len(selected_columns) == 2:
        col1, col2 = selected_columns[0], selected_columns[1]
        
        if operation == "قسمة":
            equation_input = f"({col1} / {col2}) / {constant_value}" if use_constant else f"({col1} / {col2})"
        elif operation == "ضرب":
            equation_input = f"({col1} * {col2}) * {constant_value}" if use_constant else f"({col1} * {col2})"
        elif operation == "جمع":
            equation_input = f"{col1} + {col2}"
        elif operation == "طرح":
            equation_input = f"{col1} - {col2}"

        st.sidebar.write(f"المعادلة التي تم إنشاؤها: {equation_input}")
        
        # Check if user entered the formula
        try:# Replace column names with the values from the dataframe dynamically
            def evaluate_row(row):
                equation = equation_input
                # Replace column names in the equation with their values from the row
                equation = equation.replace(col1, str(row[col1]))
                equation = equation.replace(col2, str(row[col2]))
                try:
                    return eval(equation)
                except Exception as e:
                    return None
            
            # Apply the custom equation to the dataframe
            data['CustomMetric'] = data.apply(evaluate_row, axis=1)
            
            # Rank neighborhoods based on the new custom metric
            custom_sorted_data = rank_neighborhoods('CustomMetric')

            # Add the new custom metric to the available metrics list
            available_metrics.append(equation_name)
            selected_metric = equation_name  # Automatically select the new custom metric
            
            st.sidebar.write(f"نتيجة {equation_name}:")
            st.sidebar.write(custom_sorted_data[['Neighborhood', 'CustomMetric', 'Classification']])
            
            # Display the custom metric map
            st.write(f"الخريطة مع تصنيف {equation_name} للأحياء:")
            
            # Initialize map
            m = folium.Map(location=[24.7136, 46.6753], zoom_start=12)

            # Add markers to map for custom metric
            for _, row in custom_sorted_data.iterrows():
                color = 'green' if row['Classification'] == 'High' else 'blue' if row['Classification'] == 'Medium' else 'red'
                folium.Marker([row['Latitude_x'], row['Longitude_x']], 
                              popup=f"{row['Neighborhood']} - {row['CustomMetric']}",
                              icon=folium.Icon(color=color)).add_to(m)

            # Display the map
            st.components.v1.html(m._repr_html_(), width=700, height=500)

        except Exception as e:
            st.sidebar.write(f"حدث خطأ في المعادلة: {str(e)}")

# Display map with markers based on selected metric
else:
    st.write(f"الخريطة مع تصنيف {selected_metric} للأحياء:")
    sorted_data = rank_neighborhoods(selected_metric)
    
    m = folium.Map(location=[24.7136, 46.6753], zoom_start=12)

    for _, row in sorted_data.iterrows():
        color = 'green' if row['Classification'] == 'High' else 'blue' if row['Classification'] == 'Medium' else 'red'
        folium.Marker([row['Latitude_x'], row['Longitude_x']], 
                      popup=f"{row['Neighborhood']} - {row[selected_metric]}",
                      icon=folium.Icon(color=color)).add_to(m)

    st.components.v1.html(m._repr_html_(), width=700, height=500)