from fastapi import FastAPI, HTTPException
import requests
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from requests.exceptions import RequestException
from dotenv import load_dotenv
import os
import json
from datetime import datetime

# Load environment variables
load_dotenv()
app = FastAPI()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not GEMINI_API_KEY or not WEATHER_API_KEY:
    raise ValueError("API keys not found. Please check your .env file.")

# Configure Gemini with the validated key
genai.configure(api_key=GEMINI_API_KEY)

@app.get("/weather")
def get_weather(query: str):
    try:
        # Step 1: Ask Gemini to extract city & date
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        prompt = (
            f"Extract the city and date (if mentioned) from this query. "
            f"Return ONLY JSON like {{\"city\": \"...\", \"date\": \"YYYY-MM-DD\"}}. "
            f"Do not include any conversational text, markdown, or code blocks."
            f"Query: '{query}'"
        )
        extraction = model.generate_content(prompt)

        json_string = extraction.text.strip()
        start_index = json_string.find('{')
        end_index = json_string.rfind('}') + 1
        
        if start_index == -1 or end_index == -1:
            raise json.JSONDecodeError("Could not find valid JSON.", json_string, 0)
            
        cleaned_json = json_string[start_index:end_index]
        
        data = json.loads(cleaned_json)
        city = data.get("city")
        date_str = data.get("date")

    except ResourceExhausted:
        raise HTTPException(
            status_code=429,
            detail="You have exceeded your Gemini API quota. Please try again later."
        )
    except json.JSONDecodeError as e:
        # Handle Gemini's output not being a valid JSON
        raise HTTPException(
            status_code=500,
            detail=f"Could not parse JSON from Gemini. Raw output: '{extraction.text}'"
        )
    except Exception as e:
        # Catch any other unexpected errors from Gemini 
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while communicating with Gemini: {e}"
        )

    if not city:
        return {"error": "City not found in query."}

    # Step 2: Call OpenWeatherMap
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=imperial"
    try:
        response = requests.get(url)
        response.raise_for_status()  
        forecast_data = response.json()
    except RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to OpenWeatherMap: {e}"
        )

    if "list" not in forecast_data:
        return {"error": "Weather data unavailable for this location."}

    forecast_list = forecast_data["list"]

    # Step 3: Find closest forecast if date specified
    closest = None
    if date_str:
        try:
            target = datetime.fromisoformat(date_str)
            closest = min(forecast_list, key=lambda f: abs(datetime.fromisoformat(f["dt_txt"]) - target))
        except (ValueError, KeyError, TypeError):
            closest = forecast_list[0]
    else:
        closest = forecast_list[0]

    temp = closest["main"]["temp"]
    desc = closest["weather"][0]["description"]

    # Step 4: Gemini formats a friendly answer
    prompt2 = f"The weather in {city} at {closest['dt_txt']} is {temp}°F with {desc}. Make this a friendly answer."
    try:
        ai_response = model.generate_content(prompt2)
        final_answer = ai_response.text.strip()
    except ResourceExhausted:
        raise HTTPException(
            status_code=429,
            detail="You have exceeded your Gemini API quota. Please try again later."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating the final response: {e}"
        )

    return {"result": final_answer}