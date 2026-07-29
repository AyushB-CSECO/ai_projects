import asyncio 
import requests
from google.adk.agents import Agent
# from google.adk.tools import FunctionTool
from google.adk.runners import InMemoryRunner

MODEL = "gemini-3.1-flash-lite"

def get_weather(coords: dict) -> dict:
    """
    coords: {'latitude':float, 'longitude':float}
    Returns: JSON weather response
    """
    lat = coords.get("latitude")
    lon = coords.get("longitude")

    if lat is None or lon is None:
        return {"error": "latitude & longitude required"}
    
    # Open Source website for weather data based on coordinates
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data 

# Define a custom function tool that an agent can use
# Do this when you need to do advance functions with tool. 
# Except simple approach is sufficient
# weather_tool = FunctionTool(get_weather)

# Define agent
weather_agent = Agent(
    model = MODEL,
    name = "WeatherAgent",
    description = "Use weather tool to fetch weather",
    instruction = """
    - If user asks about weather in a location(latitude/longitude), call weather_tool
    - Otherwise respond appropriately
    When returning weather, report temperature, wind spped and if it's day or night time.
    """,
    tools = [get_weather] # [weather_tool] if using FunctionTool class
)

async def main():
    runner = InMemoryRunner(agent = weather_agent)
    user_query = "Get weather of Whitefield, Bengaluru. Use coordinates \
        Latitude: 12.9713 & Longitude: 77.7501"
    events = await runner.run_debug(user_query)

if __name__ == "__main__":
    if False:
        # Check weather function
        coords_val = {'latitude':24.4329, 'longitude': 54.6445}
        weather_data = get_weather(coords_val) 
        # print(weather_data) 

    asyncio.run(main())