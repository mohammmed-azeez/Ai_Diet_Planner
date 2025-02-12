import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Configure Google Gemini API with the API key
GOOGLE_API_KEY = "AIzaSyDptRo_34RiCU6LKCpvdxHHeWh43EY8axA"
genai.configure(api_key=GOOGLE_API_KEY)

# Set up the model
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]

model = genai.GenerativeModel('gemini-pro', 
                            safety_settings=safety_settings,
                            generation_config={
                                "temperature": 0.9,
                                "top_p": 1,
                                "top_k": 1,
                                "max_output_tokens": 2048,
                            })

# Initialize session state
if 'meal_plan' not in st.session_state:
    st.session_state.meal_plan = None
if 'nutrition_data' not in st.session_state:
    st.session_state.nutrition_data = None

class DietPlanner:
    def __init__(self):
        self.diet_types = [
            "Regular", "Vegetarian", "Vegan", "Keto", 
            "Paleo", "Mediterranean", "Low-Carb"
        ]
        self.allergies = [
            "None", "Peanuts", "Tree Nuts", "Dairy", 
            "Eggs", "Soy", "Wheat", "Shellfish", "Fish"
        ]
        
    def generate_meal_plan(self, preferences):
        try:
            # Construct prompt for Gemini
            prompt = f"""
            Create a 7-day meal plan based on these preferences:
            - Diet Type: {preferences['diet_type']}
            - Daily Calories: {preferences['calories']}
            - Protein: {preferences['protein']}%
            - Carbs: {preferences['carbs']}%
            - Fat: {preferences['fat']}%
            - Allergies: {', '.join(preferences['allergies'])}
            
            Please provide a detailed meal plan in JSON format with this exact structure:
            {{
                "weekly_plan": {{
                    "day1": {{
                        "breakfast": {{"meal": "Meal description with portions", "calories": 500, "protein": 30, "carbs": 40, "fat": 20}},
                        "lunch": {{"meal": "Meal description with portions", "calories": 600, "protein": 35, "carbs": 45, "fat": 25}},
                        "dinner": {{"meal": "Meal description with portions", "calories": 500, "protein": 30, "carbs": 40, "fat": 20}}
                    }},
                    "day2": {{...}},
                    "day3": {{...}},
                    "day4": {{...}},
                    "day5": {{...}},
                    "day6": {{...}},
                    "day7": {{...}}
                }}
            }}
            
            Ensure:
            1. All meals comply with the dietary restrictions and allergies
            2. Include specific portion sizes
            3. Nutritional values are realistic and sum up close to daily targets
            4. Meals are varied and practical
            5. Response must be valid JSON
            """
            
            # Generate response using Gemini
            response = model.generate_content(prompt)
            response_text = response.text
            
            # Extract JSON from the response
            # Find the first { and last } to extract just the JSON part
            start_idx = response_text.find('{')
            end_idx = response_text.rindex('}') + 1
            json_str = response_text[start_idx:end_idx]
            
            # Parse the JSON
            meal_plan = json.loads(json_str)
            return meal_plan
            
        except Exception as e:
            st.error(f"Error generating meal plan: {str(e)}")
            return None

    def calculate_nutrition_totals(self, meal_plan):
        if not meal_plan:
            return None
            
        daily_totals = []
        for day in range(1, 8):
            day_key = f"day{day}"
            day_data = meal_plan['weekly_plan'][day_key]
            
            daily_calories = sum(meal['calories'] for meal in day_data.values())
            daily_protein = sum(meal['protein'] for meal in day_data.values())
            daily_carbs = sum(meal['carbs'] for meal in day_data.values())
            daily_fat = sum(meal['fat'] for meal in day_data.values())
            
            daily_totals.append({
                'Day': day,
                'Calories': daily_calories,
                'Protein': daily_protein,
                'Carbs': daily_carbs,
                'Fat': daily_fat
            })
            
        return pd.DataFrame(daily_totals)

def main():
    st.title("AI Diet Planner")
    
    planner = DietPlanner()
    
    # Sidebar for user inputs
    with st.sidebar:
        st.header("Your Preferences")
        
        diet_type = st.selectbox("Diet Type", planner.diet_types)
        calories = st.number_input("Daily Calorie Target", 1200, 4000, 2000, 100)
        
        st.subheader("Macronutrient Distribution (%)")
        col1, col2, col3 = st.columns(3)
        with col1:
            protein = st.number_input("Protein", 10, 50, 30, 5)
        with col2:
            carbs = st.number_input("Carbs", 10, 60, 40, 5)
        with col3:
            fat = st.number_input("Fat", 10, 60, 30, 5)
            
        allergies = st.multiselect("Allergies/Restrictions", planner.allergies)
        
        if st.button("Generate Meal Plan"):
            preferences = {
                'diet_type': diet_type,
                'calories': calories,
                'protein': protein,
                'carbs': carbs,
                'fat': fat,
                'allergies': allergies if allergies else ['None']
            }
            
            with st.spinner("Generating your personalized meal plan..."):
                st.session_state.meal_plan = planner.generate_meal_plan(preferences)
                if st.session_state.meal_plan:
                    st.session_state.nutrition_data = planner.calculate_nutrition_totals(st.session_state.meal_plan)
    
    # Main content area
    if st.session_state.meal_plan:
        # Tabs for different views
        tab1, tab2 = st.tabs(["Meal Plan", "Nutrition Analysis"])
        
        with tab1:
            st.header("Your Weekly Meal Plan")
            for day in range(1, 8):
                day_key = f"day{day}"
                with st.expander(f"Day {day}"):
                    day_data = st.session_state.meal_plan['weekly_plan'][day_key]
                    
                    for meal_type, meal_info in day_data.items():
                        st.subheader(meal_type.capitalize())
                        st.write(f"🍽️ {meal_info['meal']}")
                        st.write(f"Calories: {meal_info['calories']} kcal | "
                                f"Protein: {meal_info['protein']}g | "
                                f"Carbs: {meal_info['carbs']}g | "
                                f"Fat: {meal_info['fat']}g")
        
        with tab2:
            st.header("Nutrition Analysis")
            
            if st.session_state.nutrition_data is not None:
                # Daily nutrition trends
                st.subheader("Daily Nutrition Trends")
                fig_calories = px.line(st.session_state.nutrition_data, 
                                     x='Day', y='Calories',
                                     title='Daily Calorie Intake')
                st.plotly_chart(fig_calories)
                
                # Macronutrient distribution
                st.subheader("Macronutrient Distribution")
                fig_macros = px.bar(st.session_state.nutrition_data,
                                   x='Day',
                                   y=['Protein', 'Carbs', 'Fat'],
                                   title='Daily Macronutrient Distribution',
                                   barmode='group')
                st.plotly_chart(fig_macros)
                
                # Weekly averages
                st.subheader("Weekly Averages")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Calories", 
                             f"{st.session_state.nutrition_data['Calories'].mean():.0f}")
                with col2:
                    st.metric("Protein", 
                             f"{st.session_state.nutrition_data['Protein'].mean():.1f}g")
                with col3:
                    st.metric("Carbs", 
                             f"{st.session_state.nutrition_data['Carbs'].mean():.1f}g")
                with col4:
                    st.metric("Fat", 
                             f"{st.session_state.nutrition_data['Fat'].mean():.1f}g")

if __name__ == "__main__":
    main()
