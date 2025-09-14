# SEC-FastAPI-Workshop

FastAPI AI-Powered Weather API

⚙️ How It Works
The application follows a simple, robust workflow for every user request:

Natural Language Processing (NLP): The application sends a natural language query (e.g., "What's the weather like in London on Monday?") to the Gemini API.

Structured Data Extraction: Using a specific prompt, Gemini extracts the key information (city and date) and returns it in a clean JSON format.

Data Retrieval: The application uses the extracted city and date to make a targeted request to the OpenWeatherMap API.

Friendly Response Generation: The raw weather data is then sent back to Gemini with instructions to format it into a friendly, human-readable sentence.

Final Response: The final, AI-generated response is sent back to the user.

🚀 Getting Started
Follow these steps to set up and run the project locally.

Prerequisites
Python 3.8+

A Gemini API Key (obtained from Google AI Studio)

An OpenWeatherMap API Key (obtained from OpenWeatherMap)

Setup
Clone the repository and navigate to the project directory:

git clone [your-repo-url]
cd weather-ai

Create a Python virtual environment and activate it:

python -m venv venv
source venv/bin/activate # On Windows, use `venv\Scripts\activate`

Install the required dependencies:

pip install -r requirements.txt

Create a .env file:
In the root of the project, create a file named .env and add your API keys.

GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
WEATHER_API_KEY="YOUR_OPENWEATHERMAP_API_KEY"

Running the Application
Start the Uvicorn server:
The --reload flag will automatically restart the server when you make changes to the code.

uvicorn main:app --reload

Access the API:
Your application will be running at http://127.0.0.1:8000. You can interact with it using the automatically generated documentation:

Swagger UI: http://127.0.0.1:8000/docs

Redoc: http://127.0.0.1:8000/redoc

You can submit a natural language query to the /weather endpoint.

Free Tier Limits: Both APIs have generous free tiers for development. It is important to know their limits to avoid unexpected costs.

Gemini API: Typically 15 requests per minute and 1,500 requests per day.

OpenWeatherMap API: 1,000 free calls per day.
