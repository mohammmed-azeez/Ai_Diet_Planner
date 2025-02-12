"""
Database of Indian foods with nutritional information including macros, fiber, and glycemic index.
"""

INDIAN_FOODS_DB = {
    "Breakfast Items": {
        "Idli": {
            "portion": "2 pieces (80g)",
            "calories": 98,
            "protein": 4.5,
            "carbs": 21.0,
            "fat": 0.2,
            "fiber": 2.0,
            "gi_index": 77,
            "category": "breakfast",
            "description": "Steamed rice and fermented black lentil cake"
        },
        "Plain Dosa": {
            "portion": "1 medium (60g)",
            "calories": 120,
            "protein": 3.0,
            "carbs": 20.0,
            "fat": 3.5,
            "fiber": 1.5,
            "gi_index": 69,
            "category": "breakfast",
            "description": "Crispy rice and black gram crepe"
        },
        "Masala Dosa": {
            "portion": "1 medium with potato filling (120g)",
            "calories": 250,
            "protein": 6.0,
            "carbs": 45.0,
            "fat": 6.0,
            "fiber": 3.0,
            "gi_index": 72,
            "category": "breakfast",
            "description": "Crispy rice crepe with spiced potato filling"
        },
        "Poha": {
            "portion": "1 cup (100g)",
            "calories": 130,
            "protein": 3.3,
            "carbs": 26.7,
            "fat": 1.3,
            "fiber": 2.0,
            "gi_index": 65,
            "category": "breakfast",
            "description": "Flattened rice with peanuts and spices"
        },
        "Upma": {
            "portion": "1 cup (100g)",
            "calories": 150,
            "protein": 4.0,
            "carbs": 28.0,
            "fat": 3.0,
            "fiber": 2.5,
            "gi_index": 60,
            "category": "breakfast",
            "description": "Savory semolina porridge"
        }
    },
    "Breads": {
        "Roti": {
            "portion": "1 piece (30g)",
            "calories": 70,
            "protein": 3.0,
            "carbs": 15.0,
            "fat": 0.4,
            "fiber": 2.0,
            "gi_index": 62,
            "category": "bread",
            "description": "Whole wheat flatbread"
        },
        "Naan": {
            "portion": "1 piece (60g)",
            "calories": 150,
            "protein": 4.5,
            "carbs": 28.0,
            "fat": 3.0,
            "fiber": 1.5,
            "gi_index": 71,
            "category": "bread",
            "description": "Leavened flatbread"
        },
        "Paratha": {
            "portion": "1 piece (50g)",
            "calories": 160,
            "protein": 4.0,
            "carbs": 25.0,
            "fat": 5.0,
            "fiber": 2.0,
            "gi_index": 70,
            "category": "bread",
            "description": "Layered whole wheat flatbread"
        }
    },
    "Rice Dishes": {
        "Plain Rice": {
            "portion": "1 cup cooked (150g)",
            "calories": 205,
            "protein": 4.3,
            "carbs": 45.0,
            "fat": 0.4,
            "fiber": 0.6,
            "gi_index": 73,
            "category": "rice",
            "description": "Steamed white rice"
        },
        "Brown Rice": {
            "portion": "1 cup cooked (150g)",
            "calories": 216,
            "protein": 5.0,
            "carbs": 45.0,
            "fat": 1.8,
            "fiber": 3.5,
            "gi_index": 68,
            "category": "rice",
            "description": "Steamed brown rice"
        },
        "Vegetable Biryani": {
            "portion": "1 cup (200g)",
            "calories": 280,
            "protein": 6.0,
            "carbs": 52.0,
            "fat": 7.0,
            "fiber": 4.0,
            "gi_index": 65,
            "category": "rice",
            "description": "Spiced rice with mixed vegetables"
        }
    },
    "Lentils and Dals": {
        "Dal Tadka": {
            "portion": "1 cup (200g)",
            "calories": 220,
            "protein": 12.0,
            "carbs": 35.0,
            "fat": 5.0,
            "fiber": 6.0,
            "gi_index": 45,
            "category": "dal",
            "description": "Tempered yellow lentils"
        },
        "Rajma": {
            "portion": "1 cup (200g)",
            "calories": 280,
            "protein": 15.0,
            "carbs": 45.0,
            "fat": 6.0,
            "fiber": 8.0,
            "gi_index": 40,
            "category": "dal",
            "description": "Kidney bean curry"
        },
        "Chana Masala": {
            "portion": "1 cup (200g)",
            "calories": 270,
            "protein": 14.0,
            "carbs": 42.0,
            "fat": 7.0,
            "fiber": 7.0,
            "gi_index": 42,
            "category": "dal",
            "description": "Spiced chickpea curry"
        }
    },
    "Vegetable Dishes": {
        "Palak Paneer": {
            "portion": "1 cup (200g)",
            "calories": 260,
            "protein": 14.0,
            "carbs": 12.0,
            "fat": 18.0,
            "fiber": 5.0,
            "gi_index": 35,
            "category": "vegetable",
            "description": "Spinach curry with cottage cheese"
        },
        "Mixed Veg Curry": {
            "portion": "1 cup (200g)",
            "calories": 180,
            "protein": 6.0,
            "carbs": 25.0,
            "fat": 8.0,
            "fiber": 6.0,
            "gi_index": 45,
            "category": "vegetable",
            "description": "Mixed vegetables in spiced gravy"
        },
        "Bhindi Masala": {
            "portion": "1 cup (150g)",
            "calories": 140,
            "protein": 4.0,
            "carbs": 16.0,
            "fat": 7.0,
            "fiber": 5.0,
            "gi_index": 40,
            "category": "vegetable",
            "description": "Spiced okra"
        }
    },
    "Snacks": {
        "Samosa": {
            "portion": "1 piece (60g)",
            "calories": 180,
            "protein": 4.0,
            "carbs": 24.0,
            "fat": 8.0,
            "fiber": 2.0,
            "gi_index": 68,
            "category": "snack",
            "description": "Fried pastry with spiced potato filling"
        },
        "Dhokla": {
            "portion": "2 pieces (80g)",
            "calories": 120,
            "protein": 6.0,
            "carbs": 20.0,
            "fat": 2.0,
            "fiber": 3.0,
            "gi_index": 45,
            "category": "snack",
            "description": "Steamed fermented gram flour cake"
        },
        "Bhel Puri": {
            "portion": "1 cup (100g)",
            "calories": 160,
            "protein": 5.0,
            "carbs": 28.0,
            "fat": 5.0,
            "fiber": 3.0,
            "gi_index": 55,
            "category": "snack",
            "description": "Puffed rice with vegetables and chutneys"
        }
    }
}

def get_gi_impact(gi_index):
    """Return the blood sugar impact category based on glycemic index."""
    if gi_index <= 55:
        return "Low - Gradual blood sugar rise"
    elif gi_index <= 70:
        return "Medium - Moderate blood sugar rise"
    else:
        return "High - Rapid blood sugar rise"

def get_meal_balance_score(protein, carbs, fat, fiber):
    """Calculate a meal balance score (0-100) based on macronutrients and fiber."""
    score = 0
    
    # Protein score (ideal: 20-30% of calories)
    if 20 <= protein <= 30:
        score += 25
    elif 15 <= protein <= 35:
        score += 15
    
    # Carbs score (ideal: 45-65% of calories)
    if 45 <= carbs <= 65:
        score += 25
    elif 40 <= carbs <= 70:
        score += 15
    
    # Fat score (ideal: 20-35% of calories)
    if 20 <= fat <= 35:
        score += 25
    elif 15 <= fat <= 40:
        score += 15
    
    # Fiber score (ideal: >3g per meal)
    if fiber >= 3:
        score += 25
    elif fiber >= 2:
        score += 15
    
    return score

def get_balance_category(score):
    """Return meal balance category based on score."""
    if score >= 80:
        return "Excellent balance"
    elif score >= 60:
        return "Good balance"
    elif score >= 40:
        return "Fair balance"
    else:
        return "Needs improvement"

def get_meal_suggestions(score, macros, gi_index):
    """Generate suggestions for improving meal balance and blood sugar impact."""
    suggestions = []
    
    if macros['protein'] < 20:
        suggestions.append("Consider adding more protein (e.g., dal, paneer, or legumes)")
    
    if macros['fiber'] < 3:
        suggestions.append("Increase fiber by adding vegetables or switching to whole grains")
    
    if gi_index > 70:
        suggestions.append("High GI - consider pairing with protein/fiber to slow digestion")
    
    if macros['fat'] > 35:
        suggestions.append("Consider reducing oil/ghee content for better balance")
    
    return suggestions if suggestions else ["Meal is well-balanced!"] 