import streamlit as st
import requests
import os
import json
from typing import List, Dict, Any, Optional, Union
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys (should be stored in .env file in production)
SERPER_API_KEY = '64387bd18391d5f03e9867464b515009a1128a74'
GROQ_API_KEY = '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'

# API endpoints
SERPER_API_URL = "https://google.serper.dev/search"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


class RecipeGenerator:
    def __init__(self):
        self.serper_api_key = SERPER_API_KEY
        self.groq_api_key = GROQ_API_KEY

    def search_ingredients(self, query: str) -> List[Dict[Any, Any]]:
        """Search for ingredients information using SerperAPI."""
        headers = {
            "X-API-KEY": self.serper_api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": f"{query} ingredients nutritional information",
            "num": 5
        }

        try:
            response = requests.post(SERPER_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            return response.json().get("organic", [])
        except requests.exceptions.RequestException as e:
            st.error(f"Error searching for ingredients: {str(e)}")
            return []

    def search_dish_info(self, dish_name: str) -> Dict[str, Any]:
        """Search for dish information using SerperAPI."""
        headers = {
            "X-API-KEY": self.serper_api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": f"{dish_name} traditional recipe authentic",
            "num": 3
        }

        try:
            response = requests.post(SERPER_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            search_results = response.json().get("organic", [])

            # Extract relevant information
            dish_info = {
                "description": "",
                "origin": "",
                "key_ingredients": []
            }

            if search_results:
                # Try to extract information from snippets
                for result in search_results:
                    snippet = result.get("snippet", "")
                    if "origin" in snippet.lower() or "traditional" in snippet.lower():
                        dish_info["description"] += snippet + " "
                    if "ingredients" in snippet.lower():
                        dish_info["key_ingredients"].append(snippet)

            return dish_info
        except requests.exceptions.RequestException as e:
            st.error(f"Error searching for dish information: {str(e)}")
            return {"description": "", "origin": "", "key_ingredients": []}

    def generate_recipe_by_ingredients(self, ingredients: List[str], dietary_restrictions: List[str],
                                       cuisine_type: str, meal_type: str) -> str:
        """Generate a recipe based on ingredients using Groq API with Llama 3 model."""
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }

        # Format the ingredients list
        ingredients_str = ", ".join(ingredients)
        dietary_restrictions_str = ", ".join(dietary_restrictions) if dietary_restrictions else "None"

        # Create prompt for recipe generation
        prompt = f"""Generate a detailed recipe based on the following information:

Ingredients available: {ingredients_str}
Dietary restrictions: {dietary_restrictions_str}
Cuisine type: {cuisine_type}
Meal type: {meal_type}

Please include:
1. A creative name for the dish
2. Preparation time and cooking time
3. Serving size
4. Ingredients with measurements
5. Step-by-step cooking instructions
6. Nutritional information (approximate calories, protein, carbs, fat)
7. Tips for serving and storage

Format the recipe nicely with clear sections.
"""

        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system",
                 "content": "You are a professional chef specialized in creating delicious, creative recipes that match the user's requirements."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }

        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            st.error(f"Error generating recipe: {str(e)}")
            return "Failed to generate recipe. Please try again later."

    def generate_recipe_by_name(self, dish_name: str, dietary_restrictions: Optional[List[str]] = None) -> str:
        """Generate a recipe based on dish name using Groq API with Llama 3 model."""
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }

        # Get additional information about the dish
        dish_info = self.search_dish_info(dish_name)

        dietary_restrictions_str = ", ".join(dietary_restrictions) if dietary_restrictions else "None"

        # Create prompt for recipe generation
        prompt = f"""Generate a detailed authentic recipe for {dish_name}.

Dietary adaptations (if applicable): {dietary_restrictions_str}

Please incorporate any traditional elements and authentic techniques. Include:
1. A brief description and history of the dish
2. Preparation time and cooking time
3. Serving size
4. Complete list of ingredients with precise measurements
5. Step-by-step cooking instructions with details on techniques
6. Nutritional information (approximate calories, protein, carbs, fat)
7. Tips for serving, presentation, and storage
8. Variations or substitutions if relevant

Format the recipe with clear sections.
"""

        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system",
                 "content": "You are a professional chef specialized in authentic recipes from around the world with deep knowledge of traditional cooking techniques and ingredients."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }

        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            st.error(f"Error generating recipe: {str(e)}")
            return "Failed to generate recipe. Please try again later."

    def extract_recipe_sections(self, recipe_text: str) -> Dict[str, str]:
        """Extract different sections from the recipe text."""
        sections = {
            "title": "",
            "time": "",
            "servings": "",
            "ingredients": "",
            "instructions": "",
            "nutrition": "",
            "tips": ""
        }

        # Try to extract title (first line is usually the title)
        lines = recipe_text.split('\n')
        if lines:
            sections["title"] = lines[0].strip('# ').strip()

        # Extract time information
        time_match = re.search(r'(Prep|Preparation|Cook|Total) [Tt]ime:.*', recipe_text, re.MULTILINE)
        if time_match:
            time_line_index = recipe_text.find(time_match.group(0))
            time_section = recipe_text[time_line_index:time_line_index + 200]
            time_end = time_section.find('\n\n')
            if time_end > 0:
                sections["time"] = time_section[:time_end].strip()
            else:
                sections["time"] = time_match.group(0).strip()

        # Extract servings
        servings_match = re.search(r'Serv(ing|ings|es):.*', recipe_text, re.MULTILINE)
        if servings_match:
            sections["servings"] = servings_match.group(0).strip()

        # Extract ingredients section
        ingredients_match = re.search(r'Ingredients:(.*?)(Instructions|Directions|Steps|Method)',
                                      recipe_text, re.DOTALL | re.IGNORECASE)
        if ingredients_match:
            sections["ingredients"] = ingredients_match.group(1).strip()

        # Extract instructions section
        instructions_match = re.search(r'(Instructions|Directions|Steps|Method):(.*?)(Nutrition|Tips|Notes|$)',
                                       recipe_text, re.DOTALL | re.IGNORECASE)
        if instructions_match:
            sections["instructions"] = instructions_match.group(2).strip()

        # Extract nutrition information
        nutrition_match = re.search(r'Nutrition(al)? [Ii]nformation:(.*?)(Tips|Notes|$)',
                                    recipe_text, re.DOTALL | re.IGNORECASE)
        if nutrition_match:
            sections["nutrition"] = nutrition_match.group(2).strip()

        # Extract tips
        tips_match = re.search(r'(Tips|Notes):(.*?)($)', recipe_text, re.DOTALL | re.IGNORECASE)
        if tips_match:
            sections["tips"] = tips_match.group(2).strip()

        return sections


def main():
    st.set_page_config(
        page_title="AI Recipe Generator",
        page_icon="🍳",
        layout="wide"
    )

    st.title("🍳 AI Recipe Generator")
    st.markdown("Generate custom recipes based on ingredients you have or get recipes for specific dishes.")

    recipe_gen = RecipeGenerator()

    # Create tabs for different recipe generation methods
    tab1, tab2 = st.tabs(["🥕 Generate by Ingredients", "🍲 Get Recipe by Dish Name"])

    with tab1:
        st.header("Generate Recipe from Ingredients")
        st.markdown("Enter ingredients you have on hand to create a custom recipe.")

        col1, col2 = st.columns([2, 1])

        with col1:
            # Input for ingredients
            ingredients_input = st.text_area("Enter ingredients (comma separated):",
                                             placeholder="chicken, rice, tomatoes, olive oil, garlic",
                                             height=100)

        with col2:
            # Cuisine type selection
            cuisine_types = ["Any", "Italian", "Mexican", "Chinese", "Indian", "Japanese",
                             "Thai", "Mediterranean", "French", "American", "Middle Eastern"]
            cuisine_type = st.selectbox("Cuisine Type:", cuisine_types)

            # Meal type selection
            meal_types = ["Any", "Breakfast", "Lunch", "Dinner", "Appetizer", "Dessert", "Snack"]
            meal_type = st.selectbox("Meal Type:", meal_types)

        # Dietary restrictions
        dietary_options = ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free",
                           "Low-Carb", "Keto", "Paleo", "Low-Fat", "High-Protein"]
        dietary_restrictions = st.multiselect("Dietary Restrictions:", dietary_options)

        ingredients_generate_button = st.button("Generate Recipe", key="ingredients_button", type="primary")

        # Process ingredient-based recipe generation
        if ingredients_generate_button:
            if not ingredients_input.strip():
                st.error("Please enter at least one ingredient.")
            else:
                with st.spinner("Generating your custom recipe..."):
                    # Process ingredients
                    ingredients = [ing.strip() for ing in ingredients_input.split(",") if ing.strip()]

                    # Handle "Any" selections
                    cuisine = "" if cuisine_type == "Any" else cuisine_type
                    meal = "" if meal_type == "Any" else meal_type

                    # Generate recipe
                    recipe_text = recipe_gen.generate_recipe_by_ingredients(
                        ingredients=ingredients,
                        dietary_restrictions=dietary_restrictions,
                        cuisine_type=cuisine,
                        meal_type=meal
                    )

                # Extract sections to display nicely
                recipe_sections = recipe_gen.extract_recipe_sections(recipe_text)

                # Display the recipe with nice formatting
                st.header(recipe_sections["title"] or "Your Custom Recipe")

                col1, col2 = st.columns(2)

                with col1:
                    if recipe_sections["time"]:
                        st.subheader("⏱️ Time")
                        st.write(recipe_sections["time"])

                    if recipe_sections["servings"]:
                        st.subheader("🍽️ Servings")
                        st.write(recipe_sections["servings"])

                    st.subheader("🛒 Ingredients")
                    st.write(recipe_sections["ingredients"] or recipe_sections.get("ingredients", ""))

                with col2:
                    st.subheader("👨‍🍳 Instructions")
                    st.write(recipe_sections["instructions"] or "")

                    if recipe_sections["nutrition"]:
                        st.subheader("📊 Nutrition Information")
                        st.write(recipe_sections["nutrition"])

                    if recipe_sections["tips"]:
                        st.subheader("💡 Tips")
                        st.write(recipe_sections["tips"])

                # Save recipe option
                st.download_button(
                    label="Download Recipe",
                    data=recipe_text,
                    file_name=f"{recipe_sections['title'].replace(' ', '_').lower() or 'custom_recipe'}.txt",
                    mime="text/plain"
                )

    with tab2:
        st.header("Get Recipe by Dish Name")
        st.markdown("Enter the name of a dish to get its authentic recipe.")

        # Input for dish name
        dish_name = st.text_input("Enter dish name:", placeholder="Pad Thai, Lasagna, Biryani, etc.")

        # Dietary restrictions for dish
        dish_dietary_options = ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free",
                                "Low-Carb", "Keto", "Paleo", "Low-Fat", "High-Protein"]
        dish_dietary_restrictions = st.multiselect("Any dietary adaptations needed?",
                                                   dish_dietary_options,
                                                   key="dish_dietary")

        dish_generate_button = st.button("Get Recipe", key="dish_button", type="primary")

        # Process dish-based recipe generation
        if dish_generate_button:
            if not dish_name.strip():
                st.error("Please enter a dish name.")
            else:
                with st.spinner(f"Generating recipe for {dish_name}..."):
                    # Generate recipe by dish name
                    recipe_text = recipe_gen.generate_recipe_by_name(
                        dish_name=dish_name,
                        dietary_restrictions=dish_dietary_restrictions
                    )

                    # Extract sections to display nicely
                    recipe_sections = recipe_gen.extract_recipe_sections(recipe_text)

                    # Display the recipe with nice formatting
                    st.header(recipe_sections["title"] or f"{dish_name} Recipe")

                    col1, col2 = st.columns(2)

                    with col1:
                        if recipe_sections["time"]:
                            st.subheader("⏱️ Time")
                            st.write(recipe_sections["time"])

                        if recipe_sections["servings"]:
                            st.subheader("🍽️ Servings")
                            st.write(recipe_sections["servings"])

                        st.subheader("🛒 Ingredients")
                        st.write(recipe_sections["ingredients"] or recipe_sections.get("ingredients", ""))

                    with col2:
                        st.subheader("👨‍🍳 Instructions")
                        st.write(recipe_sections["instructions"] or "")

                        if recipe_sections["nutrition"]:
                            st.subheader("📊 Nutrition Information")
                            st.write(recipe_sections["nutrition"])

                        if recipe_sections["tips"]:
                            st.subheader("💡 Tips")
                            st.write(recipe_sections["tips"])

                    # Save recipe option
                    st.download_button(
                        label="Download Recipe",
                        data=recipe_text,
                        file_name=f"{dish_name.replace(' ', '_').lower()}_recipe.txt",
                        mime="text/plain",
                        key="dish_download"
                    )


if __name__ == "__main__":
    main()