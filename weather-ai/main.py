from fastapi import FastAPI, HTTPException
import requests
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()
app = FastAPI()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not GEMINI_API_KEY or not WEATHER_API_KEY:
    raise ValueError("API keys not found. Please check your .env file.")


def get_weather_forecast(city: str, date: str = None) -> dict:
    formatted_city = city.replace(" ", ",")

    url = f"http://api.openweathermap.org/data/2.5/forecast?q={formatted_city}&appid={WEATHER_API_KEY}&units=imperial"
    try:
        response = requests.get(url)
        response.raise_for_status()  
        forecast_data = response.json()

    except requests.exceptions.RequestException as e:
        # Better error handling
        if response.status_code == 404:
            return {"error": f"City '{city}' not found. Please check the spelling."}
        return {"error": f"Failed to connect to OpenWeatherMap: {e}"}

    if "list" not in forecast_data or not forecast_data["list"]:
        return {"error": "Weather data unavailable for this location."}

    forecast_list = forecast_data["list"]
    if date:
        try:
            target = datetime.fromisoformat(date)
            closest = min(forecast_list, key=lambda f: abs(datetime.fromisoformat(f["dt_txt"]) - target))
        except Exception:
            closest = forecast_list[0]
    else:
        closest = forecast_list[0]

    return {
        "temp": closest["main"]["temp"],
        "desc": closest["weather"][0]["description"],
        "city": city,
        "forecast_time": closest["dt_txt"]
    }

# Define Gemini tool
weather_tool = {
    "name": "get_weather_forecast",
    "description": "Get the weather for a city and optional date. Date format must be YYYY-MM-DD.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City to fetch weather for"},
            "date": {"type": "string", "description": "Date in YYYY-MM-DD format", "nullable": True}
        },
        "required": ["city"]
    },
}
@app.get("/weather")
def get_weather(query: str):
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        tools = types.Tool(function_declarations=[weather_tool])
        
        config = types.GenerateContentConfig(
            tools=[tools],
            tool_config={"function_calling_config": {"mode": "ANY"}}
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=query,
            config=config,
        )

        # Check if Gemini called a function
        fc = response.candidates[0].content.parts[0].function_call
        if not fc or fc.name != "get_weather_forecast":
            return {"error": "Gemini did not suggest a weather tool call.", "raw": response.text}
        
        args = fc.args
        city = args.get("city")
        if not city:
            raise HTTPException(status_code=400, detail="The city argument was not provided by the model.")

        result = get_weather_forecast(city, args.get("date"))

        if 'error' in result:
             raise HTTPException(status_code=500, detail=f"Weather API error: {result['error']}")

        prompt2 = f"The weather in {result['city']} at {result['forecast_time']} is {result['temp']}°F with {result['desc']}. Make this a friendly answer without the time or date."
        final_response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt2
        )

        return {"result": final_response.text.strip(), "raw": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")