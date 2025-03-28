import streamlit as st
import pandas as pd
import requests
from PIL import Image

# Set page configuration
st.set_page_config(
    page_title="Food Calories Finder",
    page_icon="🍎",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #f0f2f6;
    }
    .stButton>button:hover {
        background-color: #e0e2e6;
    }
    .nutrition-card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #ffffff;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Add title and description
st.title("Food Calories Finder 🍎")
st.write("Find nutritional information for any food item!")

# Create user input section with improved styling
with st.sidebar:
    st.markdown("""<div class='nutrition-card'>""", unsafe_allow_html=True)
    st.header("Personal Information")
    height = st.number_input("Enter your height (cm)", min_value=100, max_value=250, value=170)
    weight = st.number_input("Enter your weight (kg)", min_value=30, max_value=200, value=70)
    st.markdown("</div>", unsafe_allow_html=True)

    # Calculate BMI
    bmi = weight / ((height/100) ** 2)
    st.markdown(f"""<div class='nutrition-card' style='margin-top: 1rem;'>
        <h4>Your BMI: {bmi:.1f}</h4>""", unsafe_allow_html=True)

    # BMI Category
    bmi_category = "Normal weight"
    if bmi < 18.5:
        bmi_category = "Underweight"
    elif bmi >= 25:
        bmi_category = "Overweight"
    st.markdown(f"""<p>BMI Category: {bmi_category}</p></div>""", unsafe_allow_html=True)

# Create the search interface with serving size input
col1, col2 = st.columns([2, 1])
with col1:
    search_query = st.text_input("Enter food item name", "")
with col2:
    serving_size = st.number_input("Serving size (grams)", min_value=1, max_value=1000, value=100)

# USDA Food Data Central API configuration
USDA_API_KEY = st.secrets.get("USDA_API_KEY", "AyzLwaHsTj5iwPUZIlu96gi13BPMXviTSDU14MCt")

if search_query:
    try:
        # Call USDA Food Data Central API
        api_url = 'https://api.nal.usda.gov/fdc/v1/foods/search'
        params = {
            'api_key': USDA_API_KEY,
            'query': search_query,
            'pageSize': 5,
            'dataType': ['Survey (FNDDS)']
        }
        
        response = requests.get(api_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('foods'):
                # Create two columns for layout
                results_col, info_col = st.columns([1, 2])
                
                with results_col:
                    st.markdown("""<div class='nutrition-card'>""", unsafe_allow_html=True)
                    st.subheader("Search Results")
                    # Display foods
                    for item in data['foods'][:5]:
                        if st.button(f"📍 {item['description'].title()}", key=f"food_{item['fdcId']}"):
                            food = item
                            nutrients = food.get('foodNutrients', [])
                            
                            with info_col:
                                st.markdown("""<div class='nutrition-card'>""", unsafe_allow_html=True)
                                st.subheader("Nutritional Information")
                                st.write(f"**{food['description'].title()}**")
                                st.write(f"Selected Serving Size: {serving_size}g")
                                
                                # Calculate serving size ratio
                                ratio = serving_size / 100.0
                                
                                # Extract and adjust nutrient values
                                calories = next((n['value'] for n in nutrients if n['nutrientName'] == 'Energy'), 0) * ratio
                                protein = next((n['value'] for n in nutrients if n['nutrientName'] == 'Protein'), 0) * ratio
                                fat = next((n['value'] for n in nutrients if n['nutrientName'] == 'Total lipid (fat)'), 0) * ratio
                                carbs = next((n['value'] for n in nutrients if n['nutrientName'] == 'Carbohydrate, by difference'), 0) * ratio
                                fiber = next((n['value'] for n in nutrients if n['nutrientName'] == 'Fiber, total dietary'), 0) * ratio
                                sugars = next((n['value'] for n in nutrients if n['nutrientName'] == 'Sugars, total including NLEA'), 0) * ratio
                                
                                # Create a DataFrame for the nutritional information
                                nutrients_df = pd.DataFrame([
                                    {"Nutrient": "Calories", "Amount": f"{calories:.1f} kcal"},
                                    {"Nutrient": "Protein", "Amount": f"{protein:.1f}g"},
                                    {"Nutrient": "Total Fat", "Amount": f"{fat:.1f}g"},
                                    {"Nutrient": "Carbohydrates", "Amount": f"{carbs:.1f}g"},
                                    {"Nutrient": "Fiber", "Amount": f"{fiber:.1f}g"},
                                    {"Nutrient": "Sugars", "Amount": f"{sugars:.1f}g"}
                                ])
                                
                                st.table(nutrients_df)
                                
                                # Create a bar chart for macronutrient breakdown
                                st.subheader("Macronutrient Breakdown")
                                macros_df = pd.DataFrame([
                                    ["Protein", protein * 4],
                                    ["Carbs", carbs * 4],
                                    ["Fat", fat * 9]
                                ], columns=["Nutrient", "Calories"])
                                
                                st.bar_chart(macros_df.set_index("Nutrient"))
                                
                                # Exercise recommendations
                                st.subheader("Exercise Recommendations to Burn These Calories")
                                
                                # Calculate exercise durations based on calories and BMI
                                exercise_mets = {
                                    # Cardio Exercises
                                    "Walking (moderate pace)": 3.5,
                                    "Running (6 mph)": 10,
                                    "Cycling (moderate pace)": 7.5,
                                    "Swimming (moderate pace)": 7,
                                    "Jump Rope": 12.3,
                                    "HIIT Workout": 8,
                                    "Dancing (aerobic)": 6.5,
                                    "Rowing Machine": 7,
                                    # Sports Activities
                                    "Basketball": 6.5,
                                    "Tennis": 7,
                                    "Soccer": 7,
                                    "Volleyball": 4,
                                    # Low Impact Exercises
                                    "Yoga": 2.5,
                                    "Pilates": 3,
                                    "Stretching": 2.3,
                                    "Light Weightlifting": 3
                                }
                                
                                # Calculate calories burned per minute for each exercise
                                exercise_times = {}
                                for exercise, met in exercise_mets.items():
                                    cal_per_min = (met * weight * 3.5) / 200
                                    minutes_needed = calories / cal_per_min
                                    exercise_times[exercise] = minutes_needed
                                
                                # Create categories for exercises
                                cardio_exercises = {k: v for k, v in exercise_times.items() if k in [
                                    "Walking (moderate pace)", "Running (6 mph)", "Cycling (moderate pace)",
                                    "Swimming (moderate pace)", "Jump Rope", "HIIT Workout", "Dancing (aerobic)",
                                    "Rowing Machine"
                                ]}
                                
                                sports_activities = {k: v for k, v in exercise_times.items() if k in [
                                    "Basketball", "Tennis", "Soccer", "Volleyball"
                                ]}
                                
                                low_impact = {k: v for k, v in exercise_times.items() if k in [
                                    "Yoga", "Pilates", "Stretching", "Light Weightlifting"
                                ]}
                                
                                # Display exercises by category
                                st.write("**Cardio Exercises**")
                                cardio_df = pd.DataFrame([
                                    {"Exercise Type": ex, "Duration (minutes)": f"{time:.1f}"}
                                    for ex, time in cardio_exercises.items()
                                ])
                                st.table(cardio_df)
                                
                                st.write("**Sports Activities**")
                                sports_df = pd.DataFrame([
                                    {"Exercise Type": ex, "Duration (minutes)": f"{time:.1f}"}
                                    for ex, time in sports_activities.items()
                                ])
                                st.table(sports_df)
                                
                                st.write("**Low Impact Exercises**")
                                low_impact_df = pd.DataFrame([
                                    {"Exercise Type": ex, "Duration (minutes)": f"{time:.1f}"}
                                    for ex, time in low_impact.items()
                                ])
                                st.table(low_impact_df)
                                
                                # Add personalized recommendations based on BMI
                                st.markdown("""<div style='margin-top: 1rem;'>""", unsafe_allow_html=True)
                                st.write("**Personalized Recommendations:**")
                                if bmi_category == "Underweight":
                                    st.write("- Consider consulting with a healthcare provider before starting an intense exercise routine")
                                    st.write("- Focus on strength training along with cardio exercises")
                                    st.write("- Ensure adequate nutrition and protein intake")
                                elif bmi_category == "Overweight":
                                    st.write("- Start with low-impact exercises like walking and swimming")
                                    st.write("- Gradually increase exercise intensity")
                                    st.write("- Combine cardio with strength training for better results")
                                else:
                                    st.write("- Maintain a balanced exercise routine")
                                    st.write("- Mix different types of exercises for overall fitness")
                                    st.write("- Stay consistent with your workout schedule")
                                st.markdown("</div></div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("No results found for your search query.")
        else:
            st.error("Failed to fetch data from the USDA Food Data Central API.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        if not USDA_API_KEY:
            st.warning(
                "Please set up your USDA API key in the Streamlit secrets.")