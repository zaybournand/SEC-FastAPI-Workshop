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

genai.configure(api_key=GEMINI_API_KEY)

# Schema for function calling
city_date_schema = {
    "type": "object",
    "properties": {
        "city": {"type": "string", "description": "The name of the city."},
        "date": {"type": "string", "format": "date", "description": "Date in YYYY-MM-DD format, if mentioned."}
    },
    "required": ["city"]
}

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/weather")
def get_weather(query: str):
    try:
        # Step 1: Gemini structured extraction
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(
            contents=f"Extract the city and date from this query: '{query}'",
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                response_schema=city_date_schema
            )
        )

        data = response.candidates[0].content.parts[0].text
        city_date = json.loads(data)
        city = city_date.get("city")
        date_str = city_date.get("date")

    except ResourceExhausted:
        raise HTTPException(
            status_code=429,
            detail="You have exceeded your Gemini API quota. Please try again later."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting city/date with Gemini: {e}"
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
            closest = min(
                forecast_list,
                key=lambda f: abs(datetime.fromisoformat(f["dt_txt"]) - target)
            )
        except Exception:
            closest = forecast_list[0]
    else:
        closest = forecast_list[0]

    temp = closest["main"]["temp"]
    desc = closest["weather"][0]["description"]

    # Step 4: Gemini formats a friendly answer
    try:
        prompt2 = f"The weather in {city} is {temp}°F with {desc}. Make this a friendly answer."
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
            detail=f"Error while generating final response: {e}"
        )

    return {"result": final_answer}
