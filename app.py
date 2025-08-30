import os
import random
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# --- Flask App Initialization ---
app = Flask(__name__)
# Enable CORS for all routes, allowing the frontend to communicate with this backend
CORS(app)

# --- Gemini API Configuration ---
try:
    # Configure the Gemini API with the key from the environment variables
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise KeyError("GEMINI_API_KEY not found in environment variables.")
    genai.configure(api_key=api_key)
    # Initialize the generative model
    model = genai.GenerativeModel('gemini-pro')
    print("Gemini API configured successfully.")
except KeyError as e:
    print(f"ERROR: {e}")
    print("Please create a .env file and add GEMINI_API_KEY='your_key_here'")
    model = None
except Exception as e:
    print(f"An unexpected error occurred during Gemini configuration: {e}")
    model = None

# --- API Endpoints ---

@app.route('/analyze-crop', methods=['POST'])
def analyze_crop():
    """
    Simulates a machine learning model analyzing a satellite image to identify a crop.
    In a real-world scenario, this endpoint would process image data.
    """
    # For this demo, we simulate the analysis by picking a random crop and confidence level.
    possible_crops = ["Wheat", "Rice", "Sugarcane", "Cotton", "Mustard"]
    
    # Simulate the result
    detected_crop = random.choice(possible_crops)
    confidence_score = random.randint(85, 98)

    # Return the simulated result as JSON
    return jsonify({
        'crop': detected_crop,
        'confidence': confidence_score
    })

@app.route('/get-farming-tips', methods=['POST'])
def get_farming_tips():
    """
    Receives a crop name from the frontend, sends a request to the Gemini API,
    and returns tailored, expert farming tips.
    """
    # Ensure the Gemini model was initialized correctly
    if not model:
        return jsonify({'error': 'Gemini API not configured'}), 500

    # Get the crop name from the incoming JSON request
    data = request.get_json()
    crop_name = data.get('cropName')

    if not crop_name:
        return jsonify({'error': 'Crop name is required'}), 400

    # --- Prompt Engineering for Gemini ---
    # This detailed prompt instructs the AI on its role, the desired format, and content.
    prompt = f"""
    Act as an expert agronomist specializing in smallholder farms in Northern India.
    Provide practical, concise farming tips for the crop: {crop_name}.
    The audience is a tech-savvy individual at a hackathon, so the tips should be clear and actionable.
    
    IMPORTANT: Format the entire response as an HTML unordered list (`<ul>`). 
    Each list item (`<li>`) should contain one tip.
    Each tip should start with a relevant emoji.
    
    Example for "Tomatoes":
    <ul>
        <li>💧 **Water Management:** Ensure consistent watering to prevent blossom-end rot. Drip irrigation is highly effective.</li>
        <li>🐛 **Pest Control:** Regularly inspect for hornworms and use neem oil as a natural pesticide.</li>
        <li>🌱 **Soil Health:** Maintain a soil pH between 6.2 and 6.8 and enrich with compost before planting.</li>
    </ul>

    Generate the tips for {crop_name} now.
    """

    try:
        # Send the prompt to the Gemini model
        response = model.generate_content(prompt)
        
        # Clean up the response text from Gemini
        # Sometimes the model might wrap the response in markdown backticks (```html ... ```)
        cleaned_tips = response.text.replace("```html", "").replace("```", "").strip()

        # Return the generated HTML tips as JSON
        return jsonify({'tips': cleaned_tips})
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return jsonify({'error': 'Failed to get tips from Gemini API'}), 500

# --- Main Execution ---
if __name__ == '__main__':
    # Runs the Flask app. 
    # debug=True allows for automatic reloading when code changes are saved.
    # Use port 5000, the standard for Flask development.
    app.run(debug=True, port=5000)

