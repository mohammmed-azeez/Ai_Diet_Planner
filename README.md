# AI Diet Planner

An intelligent diet planning application that creates personalized meal plans based on your preferences, dietary restrictions, and nutritional goals.

## Features

- Personalized meal planning based on dietary preferences
- Support for various diet types (vegan, vegetarian, keto, etc.)
- Nutritional goal setting and tracking
- Interactive dashboards and progress visualization
- Food allergies and restrictions management
- Weekly meal plan generation
- Detailed nutritional breakdown

## Setup Instructions

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root and add your Google Gemini API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```
4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Select your dietary preferences from the available options
2. Set your nutritional goals and restrictions
3. Click "Generate Meal Plan" to create your personalized plan
4. View and interact with your meal plan and nutritional insights
5. Track your progress using the interactive dashboard

## Note

This application uses the Google Gemini API for initial model training purposes. The trained model is then used for generating meal plans without requiring constant API calls. 