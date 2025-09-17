# 🌦️ SEC-FastAPI-Workshop

**FastAPI AI-Powered Weather API**

This project demonstrates how to build a simple **AI-powered weather API** using **FastAPI**, **Gemini**, and **OpenWeatherMap**.  
It combines **natural language processing** with structured data retrieval to deliver weather forecasts in a friendly, conversational way.

---

## ⚙️ How It Works

The workflow for each user request:

1. **Natural Language Processing (NLP)**

   - The user submits a natural query like:
     > _"What's the weather like in London on Monday?"_
   - The query is sent to the **Gemini API**.

2. **Structured Data Extraction**

   - Gemini extracts the **city** and **date** from the query.
   - Returns them in a clean **JSON format**.

3. **Data Retrieval**

   - The app uses the extracted city and date to request weather data from the **OpenWeatherMap API**.

4. **Friendly Response Generation**

   - Raw weather data is sent back to Gemini with formatting instructions.
   - Gemini returns a **human-readable forecast sentence**.

5. **Final Response**
   - The app delivers the AI-generated weather forecast back to the user.

---

## 🚀 Getting Started

### ✅ Prerequisites

- Python **3.8+**
- **Gemini API Key** (from [Google AI Studio](https://aistudio.google.com/))
- **OpenWeatherMap API Key** (from [OpenWeatherMap](https://openweathermap.org/api))

---

### ⚡ Setup

#### 1. Clone the repository and navigate into the project directory:

- git clone https://github.com/zaybournand/SEC-FastAPI-Workshop.git
- cd SEC-FastAPI-Workshop
- cd weather-ai

#### 2. Create and activate a virtual environment:

- python -m venv venv
- source venv/bin/activate # On Windows: venv\Scripts\activate

#### 3. Install Dependencies:

- pip install -r requirements.txt

#### 4. Create a .env file in the project root and add your keys:

- GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
- WEATHER_API_KEY="YOUR_OPENWEATHERMAP_API_KEY"

#### 5. ▶️ Running the Application

- Start the FastAPI server with Uvicorn:
- uvicorn weather-ai.main:app --reload

#### 6. Your API will be available at:

- Base URL: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- Redoc: http://127.0.0.1:8000/redoc

### 💰 Free Tier Limits:

Be mindful of API usage to avoid exceeding free quotas:

Gemini API:

- Up to 15 requests/minute
- Up to 1,500 requests/day

OpenWeatherMap API:

- Up to 1,000 free requests/day

