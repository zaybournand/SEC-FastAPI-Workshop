from fastapi import FastAPI, HTTPException
import requests
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
from datetime import datetime

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello world"}
