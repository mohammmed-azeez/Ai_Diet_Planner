import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta
from indian_foods_db import (
    INDIAN_FOODS_DB, 
    get_gi_impact, 
    get_meal_balance_score,
    get_balance_category,
    get_meal_suggestions
)
import re

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
if 'logged_meals' not in st.session_state:
    st.session_state.logged_meals = []
if 'meal_history' not in st.session_state:
    st.session_state.meal_history = []

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
        self.meal_categories = list(INDIAN_FOODS_DB.keys())
        
        # Daily recommended fiber intake ranges (in grams)
        self.fiber_recommendations = {
            "min": 25,  # Minimum recommended daily fiber
            "max": 35   # Maximum recommended daily fiber
        }
        
    def get_food_options(self, category):
        """Get food options for a specific category."""
        return list(INDIAN_FOODS_DB[category].keys())
        
    def get_food_info(self, category, food_name):
        """Get nutritional information for a specific food."""
        return INDIAN_FOODS_DB[category][food_name]
        
    def calculate_daily_targets(self, total_calories, protein_pct, carbs_pct, fat_pct, fiber_target):
        """Calculate daily macro targets in grams based on percentages."""
        protein_cals = (total_calories * protein_pct) / 100
        carbs_cals = (total_calories * carbs_pct) / 100
        fat_cals = (total_calories * fat_pct) / 100
        
        return {
            'protein': round(protein_cals / 4),  # 4 calories per gram of protein
            'carbs': round(carbs_cals / 4),      # 4 calories per gram of carbs
            'fat': round(fat_cals / 9),          # 9 calories per gram of fat
            'fiber': fiber_target                 # Direct gram target
        }

    def parse_meal_line(self, line):
        """Parse meal line using regex for robust extraction."""
        pattern = re.compile(
            r"^(?P<meal_type>Breakfast|Lunch|Dinner) Option (?P<option_num>\d+): "
            r"(?P<meal_name>.+?) \((?:.*?)\) \| "
            r"(?:.*?Calories: (?P<calories>\d+)cal \| )?"
            r"(?:.*?Protein: (?P<protein>\d+)g \| )?"
            r"(?:.*?Carbs: (?P<carbs>\d+)g \| )?"
            r"(?:.*?Fat: (?P<fat>\d+)g \| )?"
            r"(?:.*?Fiber: (?P<fiber>\d+)g)"
        )
        
        match = pattern.search(line)
        if not match:
            return None
            
        return {
            'meal_type': match.group('meal_type').lower(),
            'option_num': f"option{match.group('option_num')}",
            'meal_name': match.group('meal_name').strip(),
            'calories': int(match.group('calories') or 0),
            'protein': int(match.group('protein') or 0),
            'carbs': int(match.group('carbs') or 0),
            'fat': int(match.group('fat') or 0),
            'fiber': int(match.group('fiber') or 0)
        }

    def generate_meal_plan(self, preferences):
        try:
            # Calculate daily targets
            daily_targets = self.calculate_daily_targets(
                preferences['calories'],
                preferences['protein'],
                preferences['carbs'],
                preferences['fat'],
                preferences['fiber']
            )

            # Improved prompt with strict formatting instructions
            prompt = f"""Create a 7-day Indian meal plan with EXACT format:
            Diet: {preferences['diet_type']}
            Calories/day: {preferences['calories']}
            Allergies: {', '.join(preferences['allergies'])}

            FORMAT TEMPLATE:
            DAY [day_number]
            Breakfast Option 1: [Name] (portion) | Calories: [N]cal | Protein: [N]g | Carbs: [N]g | Fat: [N]g | Fiber: [N]g
            Breakfast Option 2: [Name] (portion) | Calories: [N]cal | Protein: [N]g | Carbs: [N]g | Fat: [N]g | Fiber: [N]g
            Lunch Option 1: [Name] (portion) | Calories: [N]cal | Protein: [N]g | Carbs: [N]g | Fat: [N]g | Fiber: [N]g
            Lunch Option 2: [Name] (portion) | Calories: [N]cal | Protein: [N]g | Carbs: [N]g | Fat: [N]g | Fiber: [N]g
            Dinner Option 1: [Name] (portion) | Calories: [N]cal | Protein: [N]g | Carbs: [N]g | Fat: [N]g | Fiber: [N]g
            Dinner Option 2: [Name] (portion) | Calories: [N]cal | Protein: [N]g | Carbs: [N]g | Fat: [N]g | Fiber: [N]g

            EXAMPLE:
            DAY 1
            Breakfast Option 1: Poha (1.5 cups) | Calories: 250cal | Protein: 8g | Carbs: 45g | Fat: 5g | Fiber: 4g
            Breakfast Option 2: Upma (2 cups) | Calories: 300cal | Protein: 10g | Carbs: 50g | Fat: 7g | Fiber: 5g

            RULES:
            1. Use only integers for numbers
            2. Maintain exact nutrient order
            3. Include all meal options
            4. No markdown formatting"""

            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            meal_plan = {"weekly_plan": {}}
            current_day = None
            
            for line in response_text.split('\n'):
                line = line.strip()
                
                # Parse day headers
                if line.startswith('DAY'):
                    day_num = int(line.split()[1])
                    current_day = f"day{day_num}"
                    meal_plan["weekly_plan"][current_day] = {
                        "breakfast": {"option1": {}, "option2": {}},
                        "lunch": {"option1": {}, "option2": {}},
                        "dinner": {"option1": {}, "option2": {}}
                    }
                    continue
                    
                # Parse meal lines
                meal_data = self.parse_meal_line(line)
                if meal_data and current_day:
                    meal_type = meal_data['meal_type']
                    option_num = meal_data['option_num']
                    
                    meal_plan["weekly_plan"][current_day][meal_type][option_num] = {
                        "meal": meal_data['meal_name'],
                        "calories": meal_data['calories'],
                        "protein": meal_data['protein'],
                        "carbs": meal_data['carbs'],
                        "fat": meal_data['fat'],
                        "fiber": meal_data['fiber']
                    }

            # Validation with fallback values
            for day in range(1, 8):
                day_key = f"day{day}"
                if day_key not in meal_plan['weekly_plan']:
                    meal_plan['weekly_plan'][day_key] = {
                        "breakfast": {"option1": {}, "option2": {}},
                        "lunch": {"option1": {}, "option2": {}},
                        "dinner": {"option1": {}, "option2": {}}
                    }
                
                for meal_type in ['breakfast', 'lunch', 'dinner']:
                    for option in ['option1', 'option2']:
                        if not meal_plan['weekly_plan'][day_key][meal_type][option]:
                            meal_plan['weekly_plan'][day_key][meal_type][option] = {
                                "meal": "Alternative Option Available",
                                "calories": 300,
                                "protein": 10,
                                "carbs": 40,
                                "fat": 8,
                                "fiber": 5
                            }
            
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
            
            # Calculate totals for option1 (default option)
            daily_calories = sum(meal['option1']['calories'] for meal in day_data.values())
            daily_protein = sum(meal['option1']['protein'] for meal in day_data.values())
            daily_carbs = sum(meal['option1']['carbs'] for meal in day_data.values())
            daily_fat = sum(meal['option1']['fat'] for meal in day_data.values())
            daily_fiber = sum(meal['option1']['fiber'] for meal in day_data.values())
            
            daily_totals.append({
                'Day': day,
                'Calories': daily_calories,
                'Protein': daily_protein,
                'Carbs': daily_carbs,
                'Fat': daily_fat,
                'Fiber': daily_fiber
            })
            
        return pd.DataFrame(daily_totals)

def main():
    st.set_page_config(
        page_title="AI Diet Planner",
        page_icon="🥗",
        layout="wide"
    )
    
    # Custom CSS for better styling
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
            background-color: #1E1E1E;
            color: white;
        }
        .stButton>button {
            width: 100%;
            background-color: #4CAF50;
            color: white;
            padding: 0.75rem;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #45a049;
            box-shadow: 0 4px 8px rgba(0,255,0,0.2);
        }
        .stProgress .st-bo {
            background-color: #4CAF50;
        }
        .stExpander {
            background-color: #2D2D2D;
            border-radius: 8px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            border: 1px solid #3D3D3D;
            color: white;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            color: white;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 1rem 2rem;
            font-weight: 600;
            color: white;
        }
        h1 {
            color: #4CAF50;
            text-align: center;
            padding: 2rem 0;
            font-size: 2.5rem;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        h2 {
            color: #4CAF50;
            font-size: 1.8rem;
            padding: 1rem 0;
            border-bottom: 2px solid #4CAF50;
            margin-bottom: 1.5rem;
        }
        h3 {
            color: #4CAF50;
            font-size: 1.4rem;
            margin: 1rem 0;
        }
        .metric-card {
            background-color: #2D2D2D;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            text-align: center;
            color: white;
            border: 1px solid #3D3D3D;
        }
        .chart-container {
            background-color: #2D2D2D;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            margin: 1rem 0;
            border: 1px solid #3D3D3D;
            color: white;
        }
        .sidebar .stSelectbox, .sidebar .stNumberInput {
            margin-bottom: 1rem;
            color: white;
        }
        /* Additional dark theme styles */
        .stTextInput>div>div>input {
            color: white;
            background-color: #2D2D2D;
        }
        .stSelectbox>div>div>div {
            background-color: #2D2D2D;
            color: white;
        }
        .stNumberInput>div>div>input {
            color: white;
            background-color: #2D2D2D;
        }
        div[data-baseweb="select"] {
            background-color: #2D2D2D;
            color: white;
        }
        div[data-baseweb="base-input"] {
            background-color: #2D2D2D;
            color: white;
        }
        .stMarkdown {
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🥗 AI Diet Planner")
    st.markdown("---")
    
    planner = DietPlanner()
    
    # Main navigation with icons
    page = st.sidebar.radio("📋 Navigation", 
        ["🍳 Meal Planner", "📝 Manual Logging", "📊 Progress Tracking"])
    
    if "🍳 Meal Planner" in page:
        # Meal Plan Generation Section
        with st.sidebar:
            st.header("Your Preferences")
            
            diet_type = st.selectbox("Diet Type", planner.diet_types)
            calories = st.number_input("Daily Calorie Target", 1200, 4000, 2000, 100)
            
            st.subheader("Macronutrient Distribution")
            
            # Macronutrient columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("Percentages (%)")
                protein = st.number_input("Protein %", 10, 50, 30, 5)
                carbs = st.number_input("Carbs %", 10, 60, 40, 5)
                fat = st.number_input("Fat %", 10, 60, 30, 5)
                
                # Validate percentages
                total_pct = protein + carbs + fat
                if total_pct != 100:
                    st.warning(f"Percentages should sum to 100% (currently {total_pct}%)")
            
            with col2:
                st.write("Daily Targets (g)")
                # Calculate and display gram targets
                daily_targets = planner.calculate_daily_targets(calories, protein, carbs, fat, 25)
                st.write(f"Protein: {daily_targets['protein']}g")
                st.write(f"Carbs: {daily_targets['carbs']}g")
                st.write(f"Fat: {daily_targets['fat']}g")
            
            # Fiber target
            st.subheader("Fiber Target")
            fiber = st.number_input(
                "Daily Fiber (g)", 
                min_value=planner.fiber_recommendations['min'],
                max_value=planner.fiber_recommendations['max'],
                value=25,
                help=f"Recommended daily fiber intake is {planner.fiber_recommendations['min']}-{planner.fiber_recommendations['max']}g"
            )
            
            allergies = st.multiselect("Allergies/Restrictions", planner.allergies)
            
            if st.button("Generate Meal Plan"):
                if total_pct == 100:  # Only generate if macros sum to 100%
                    preferences = {
                        'diet_type': diet_type,
                        'calories': calories,
                        'protein': protein,
                        'carbs': carbs,
                        'fat': fat,
                        'fiber': fiber,
                        'allergies': allergies if allergies else ['None']
                    }
                    
                    with st.spinner("Generating your personalized Indian meal plan..."):
                        st.session_state.meal_plan = planner.generate_meal_plan(preferences)
                        if st.session_state.meal_plan:
                            st.session_state.nutrition_data = planner.calculate_nutrition_totals(st.session_state.meal_plan)
                else:
                    st.error("Please adjust the macronutrient percentages to sum to 100%")
        
        # Display meal plan
        if st.session_state.meal_plan:
            tab1, tab2 = st.tabs(["Meal Plan", "Nutrition Analysis"])
            
            with tab1:
                st.header("Your Weekly Meal Plan")
                for day in range(1, 8):
                    day_key = f"day{day}"
                    with st.expander(f"Day {day}"):
                        day_data = st.session_state.meal_plan['weekly_plan'][day_key]
                        
                        for meal_type, meal_options in day_data.items():
                            st.subheader(meal_type.capitalize())
                            
                            # Option 1
                            st.write("Option 1:")
                            meal_info = meal_options['option1']
                            st.write(f"🍽️ {meal_info['meal']}")
                            col1, col2, col3, col4, col5 = st.columns(5)
                            with col1:
                                st.write(f"Calories: {meal_info['calories']}")
                            with col2:
                                st.write(f"Protein: {meal_info['protein']}g")
                            with col3:
                                st.write(f"Carbs: {meal_info['carbs']}g")
                            with col4:
                                st.write(f"Fat: {meal_info['fat']}g")
                            with col5:
                                st.write(f"Fiber: {meal_info['fiber']}g")
                            
                            # Option 2
                            st.write("Option 2:")
                            meal_info = meal_options['option2']
                            st.write(f"🍽️ {meal_info['meal']}")
                            col1, col2, col3, col4, col5 = st.columns(5)
                            with col1:
                                st.write(f"Calories: {meal_info['calories']}")
                            with col2:
                                st.write(f"Protein: {meal_info['protein']}g")
                            with col3:
                                st.write(f"Carbs: {meal_info['carbs']}g")
                            with col4:
                                st.write(f"Fat: {meal_info['fat']}g")
                            with col5:
                                st.write(f"Fiber: {meal_info['fiber']}g")
            
            with tab2:
                st.header("Nutrition Analysis")
                
                if st.session_state.nutrition_data is not None:
                    # Weekly averages in cards
                    st.subheader("Weekly Averages")
                    cols = st.columns(5)
                    metrics = [
                        ("Calories", "Calories", "kcal", "#FF9800"),
                        ("Protein", "Protein", "g", "#2196F3"),
                        ("Carbs", "Carbs", "g", "#4CAF50"),
                        ("Fat", "Fat", "g", "#F44336"),
                        ("Fiber", "Fiber", "g", "#9C27B0")
                    ]
                    
                    for col, (metric, column, unit, color) in zip(cols, metrics):
                        with col:
                            st.markdown(f"""
                                <div class="metric-card">
                                    <h4 style="color: {color};">{metric}</h4>
                                    <h2 style="color: {color}; margin: 0;">{st.session_state.nutrition_data[column].mean():.1f}{unit}</h2>
                                </div>
                            """, unsafe_allow_html=True)
                    
                    # Daily nutrition trends
                    st.subheader("Daily Nutrition Trends")
                    
                    with st.container():
                        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                        # Calories trend with improved styling
                        fig_calories = px.line(
                            st.session_state.nutrition_data, 
                            x='Day', 
                            y='Calories',
                            title='Daily Calorie Intake',
                            markers=True
                        )
                        fig_calories.update_traces(line_color='#FF9800', line_width=3)
                        fig_calories.update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            title_x=0.5,
                            title_font_size=20
                        )
                        st.plotly_chart(fig_calories, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with st.container():
                        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                        # Macronutrient distribution with improved styling
                        fig_macros = px.line(
                            st.session_state.nutrition_data,
                            x='Day',
                            y=['Protein', 'Carbs', 'Fat', 'Fiber'],
                            title='Daily Macronutrient Distribution',
                            markers=True
                        )
                        colors = ['#2196F3', '#4CAF50', '#F44336', '#9C27B0']
                        for i, trace in enumerate(fig_macros.data):
                            trace.line.color = colors[i]
                            trace.line.width = 3
                        fig_macros.update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            title_x=0.5,
                            title_font_size=20,
                            legend_title_text=''
                        )
                        st.plotly_chart(fig_macros, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Blood Sugar Impact Analysis
                    st.subheader("Blood Sugar Impact Analysis")
                    
                    # Calculate average GI impact for each day's meals
                    gi_analysis = []
                    for day in range(1, 8):
                        day_key = f"day{day}"
                        day_meals = st.session_state.meal_plan['weekly_plan'][day_key]
                        
                        # Analyze each meal's impact
                        meals_impact = []
                        for meal_type, options in day_meals.items():
                            meal = options['option1']  # Analyze primary option
                            # Calculate rough GI impact based on carbs and fiber ratio
                            carbs = meal['carbs']
                            fiber = meal['fiber']
                            if carbs > 0:
                                impact = max(0, min(100, 100 * (carbs - fiber) / carbs))
                            else:
                                impact = 0
                            meals_impact.append(impact)
                        
                        avg_impact = sum(meals_impact) / len(meals_impact)
                        impact_category = "Low" if avg_impact < 40 else "Medium" if avg_impact < 70 else "High"
                        
                        gi_analysis.append({
                            'Day': day,
                            'Impact': avg_impact,
                            'Category': impact_category
                        })
                    
                    gi_df = pd.DataFrame(gi_analysis)
                    
                    with st.container():
                        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                        # Blood Sugar Impact Visualization
                        fig_gi = px.bar(
                            gi_df,
                            x='Day',
                            y='Impact',
                            color='Category',
                            title='Daily Blood Sugar Impact',
                            color_discrete_map={
                                'Low': '#4CAF50',
                                'Medium': '#FF9800',
                                'High': '#F44336'
                            }
                        )
                        fig_gi.update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            title_x=0.5,
                            title_font_size=20,
                            yaxis_title='Glycemic Impact Score',
                            showlegend=True
                        )
                        st.plotly_chart(fig_gi, use_container_width=True)
                        
                        # Add impact explanations
                        cols = st.columns(3)
                        with cols[0]:
                            st.markdown("""
                                <div style="background-color: #E8F5E9; padding: 1rem; border-radius: 8px;">
                                    <h4 style="color: #4CAF50;">Low Impact (0-40)</h4>
                                    <p>Minimal effect on blood sugar levels. Ideal for stable energy.</p>
                                </div>
                            """, unsafe_allow_html=True)
                        with cols[1]:
                            st.markdown("""
                                <div style="background-color: #FFF3E0; padding: 1rem; border-radius: 8px;">
                                    <h4 style="color: #FF9800;">Medium Impact (40-70)</h4>
                                    <p>Moderate blood sugar response. Balanced energy release.</p>
                                </div>
                            """, unsafe_allow_html=True)
                        with cols[2]:
                            st.markdown("""
                                <div style="background-color: #FFEBEE; padding: 1rem; border-radius: 8px;">
                                    <h4 style="color: #F44336;">High Impact (70-100)</h4>
                                    <p>Significant blood sugar elevation. May cause energy spikes.</p>
                                </div>
                            """, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
    
    elif "📝 Manual Logging" in page:
        st.header("Manual Meal Logging")
        
        # Create form
        with st.form(key="meal_logging_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                meal_date = st.date_input("Date", datetime.now())
                meal_time = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
                
            with col2:
                food_category = st.selectbox("Food Category", planner.meal_categories)
                food_options = planner.get_food_options(food_category)
                selected_food = st.selectbox("Select Food", food_options)
            
            # Get food info
            food_info = planner.get_food_info(food_category, selected_food)
            
            # Display food information
            st.write("### Nutritional Information")
            st.write(f"Portion: {food_info['portion']}")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.write(f"Calories: {food_info['calories']}")
            with col2:
                st.write(f"Protein: {food_info['protein']}g")
            with col3:
                st.write(f"Carbs: {food_info['carbs']}g")
            with col4:
                st.write(f"Fat: {food_info['fat']}g")
            with col5:
                st.write(f"Fiber: {food_info['fiber']}g")
            
            # Blood sugar impact
            gi_impact = get_gi_impact(food_info['gi_index'])
            st.write(f"Blood Sugar Impact: {gi_impact}")
            
            # Calculate meal balance
            balance_score = get_meal_balance_score(
                food_info['protein'],
                food_info['carbs'],
                food_info['fat'],
                food_info['fiber']
            )
            balance_category = get_balance_category(balance_score)
            
            st.write(f"Meal Balance: {balance_category} ({balance_score}/100)")
            
            # Get and display suggestions
            suggestions = get_meal_suggestions(
                balance_score,
                {
                    'protein': food_info['protein'],
                    'carbs': food_info['carbs'],
                    'fat': food_info['fat'],
                    'fiber': food_info['fiber']
                },
                food_info['gi_index']
            )
            
            st.write("### Suggestions for Improvement")
            for suggestion in suggestions:
                st.write(f"• {suggestion}")
            
            # Submit button at the end of the form
            submit_button = st.form_submit_button(label="Log Meal")
            
            if submit_button:
                # Add meal to history
                meal_entry = {
                    'date': meal_date.strftime("%Y-%m-%d"),
                    'meal_type': meal_time,
                    'food': selected_food,
                    'category': food_category,
                    **food_info
                }
                st.session_state.meal_history.append(meal_entry)
                st.success("Meal logged successfully!")
    
    else:  # Progress Tracking
        st.header("Progress Tracking")
        
        if not st.session_state.meal_history:
            st.warning("No meals logged yet. Start logging meals to see your progress!")
        else:
            # Convert meal history to DataFrame
            df = pd.DataFrame(st.session_state.meal_history)
            
            # Daily totals
            daily_totals = df.groupby('date').agg({
                'calories': 'sum',
                'protein': 'sum',
                'carbs': 'sum',
                'fat': 'sum',
                'fiber': 'sum'
            }).reset_index()
            
            # Trends over time
            st.subheader("Nutrition Trends")
            
            # Calories trend
            fig_calories = px.line(daily_totals, x='date', y='calories',
                                 title='Daily Calorie Intake')
            st.plotly_chart(fig_calories)
            
            # Macronutrient trends
            fig_macros = px.line(daily_totals, x='date', 
                                y=['protein', 'carbs', 'fat', 'fiber'],
                                title='Daily Macronutrient Intake')
            st.plotly_chart(fig_macros)
            
            # Meal type distribution
            meal_dist = df['meal_type'].value_counts()
            fig_meal_dist = px.pie(values=meal_dist.values, 
                                 names=meal_dist.index,
                                 title='Meal Type Distribution')
            st.plotly_chart(fig_meal_dist)
            
            # Food category distribution
            category_dist = df['category'].value_counts()
            fig_category_dist = px.pie(values=category_dist.values,
                                     names=category_dist.index,
                                     title='Food Category Distribution')
            st.plotly_chart(fig_category_dist)

if __name__ == "__main__":
    main()
