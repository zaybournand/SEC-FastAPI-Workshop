from fastapi import FastAPI, HTTPException
import requests
import google.generativeai as genai
from requests.exceptions import RequestException
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import re

# Load environment variables
load_dotenv()
app = FastAPI()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not GEMINI_API_KEY or not WEATHER_API_KEY:
    raise ValueError("API keys not found. Please check your .env file.")

genai.configure(api_key=GEMINI_API_KEY)


def get_weather_forecast(city: str, date: str = None) -> str:
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=imperial"
    try:
        response = requests.get(url)
        response.raise_for_status()
        forecast_data = response.json()
    except RequestException as e:
        return json.dumps({"error": f"Failed to connect to OpenWeatherMap: {e}"})

    if "list" not in forecast_data or not forecast_data["list"]:
        return json.dumps({"error": "Weather data unavailable for this location."})

    forecast_list = forecast_data["list"]
    closest = None
    
    # Check for a date and try to find the closest forecast
    if date:
        try:
            target = datetime.fromisoformat(date)
            closest = min(forecast_list, key=lambda f: abs(datetime.fromisoformat(f["dt_txt"]) - target))
        except (ValueError, IndexError):
            # Fallback if the date is invalid or no data is found
            closest = forecast_list[0]
    else:
        # If no date is provided use the first forecast entry
        closest = forecast_list[0]
        
    temp = closest["main"]["temp"]
    desc = closest["weather"][0]["description"]
    forecast_time = closest["dt_txt"]
    return json.dumps({"temp": temp, "desc": desc, "city": city, "forecast_time": forecast_time})


@app.get("/weather")
def get_weather(query: str):
    try:
        # 1️ Gemini prompt: ask which tool to call
        prompt = f"""
Call tool:
{{
  "name": "get_weather_forecast",
  "description": "Get the weather for a city and optional date. The date should be in YYYY-MM-DD format if mentioned in the query. If a relative date like 'tomorrow' is used, provide the corresponding date in YYYY-MM-DD format.",
  "parameters": {{
    "city": "string",
    "date": "string"
  }}
}}

When calling the tool, respond ONLY with JSON in this format:
{{ "tool": "get_weather_forecast", "args": {{ "city": "CityName", "date": "YYYY-MM-DD" }} }}

User question: {query}
"""
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        # 2️ Clean format before parsing
        clean_text = re.sub(r"^```json\s*|\s*```$", "", response.text.strip(), flags=re.MULTILINE)
        tool_call = json.loads(clean_text)

        if tool_call.get("tool") != "get_weather_forecast":
            return {"error": "Gemini did not suggest a valid tool call."}

        args = tool_call.get("args", {})
        city = args.get("city")
        date = args.get("date")

        # 3️ Call local Python function
        final_result = get_weather_forecast(city, date)

        # 4️ Optional: generate friendly answer using Gemini
        try:
            parsed_result = json.loads(final_result)
            temp = parsed_result.get("temp")
            desc = parsed_result.get("desc")
            city_name = parsed_result.get("city")
            forecast_time = parsed_result.get("forecast_time")
            
            prompt2 = f"The weather in {city_name} at {forecast_time} is {temp}°F with {desc}. Make this a friendly answer without the time or date."
            ai_response = model.generate_content(prompt2)
            final_answer = ai_response.text.strip()
        except Exception:
            # fallback to raw JSON if parsing fails
            final_answer = final_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    return {"result": final_answer}