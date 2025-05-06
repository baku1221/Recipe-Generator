# AI Recipe Generator

An AI-powered recipe generator that creates custom recipes based on available ingredients and dietary preferences. The application uses:

- **SerperAPI** to search for ingredient information
- **Groq** for inference using the **Llama 3 70B** model
- **Streamlit** for the user interface

## Features

- Generate custom recipes based on ingredients you have
- Customize by cuisine type and meal type
- Apply dietary restrictions (vegetarian, vegan, gluten-free, etc.)
- View nicely formatted recipes with sections for ingredients, instructions, and more
- Download recipes as text files

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- API keys for SerperAPI and Groq

### Installation

1. Clone this repository or download the code
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the project root directory:
   ```
   SERPER_API_KEY=your_serper_api_key_here
   GROQ_API_KEY=your_groq_api_key_here
   ```

### How to Get API Keys

- **SerperAPI**: Sign up at [serper.dev](https://serper.dev/) to get your API key
- **Groq**: Create an account at [groq.com](https://groq.com/) and get your API key from the dashboard

### Running the Application

```bash
streamlit run recipe_generator.py
```

The application will open in your default web browser at http://localhost:8501

## Usage

1. Enter your available ingredients (comma-separated) in the sidebar
2. Select cuisine type and meal type
3. Choose any dietary restrictions that apply
4. Click "Generate Recipe"
5. View the generated recipe with all details
6. Download the recipe as a text file if desired

## System Architecture

```
User Interface (Streamlit)
      ↓     ↑
Recipe Generator
   ↙         ↘
SerperAPI    Groq API (Llama 3)
```

## Limitations

- The application requires active internet connection
- API rate limits may apply based on your SerperAPI and Groq subscription plans
- Recipe quality depends on the Llama 3 model's capabilities