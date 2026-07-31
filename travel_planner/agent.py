import asyncio
import requests
from google.adk.agents import LlmAgent
from google.adk.agents import ParallelAgent, Agent
from google.adk.runners import InMemoryRunner

MODEL = "gemini-3.1-flash-lite"

# Sub-Agent 1: Gives information about flight
flight_agent = LlmAgent(
    model = MODEL,
    name = "FlightAgent",
    description = "You are a flight search assistant.",
    instruction = """ Your task is to give user available flight options between origin and destination.
        - Recommend only non-stop flights with economy seats available.
        - If the user has not atleast given two cities, ask him to rovide information.
        - Answer in short. Tell airlines name, fare, departure time, duration & arrival time.
    """,
    output_key = "flight_agent_response"
)

sightseeing_agent = LlmAgent(
    model = MODEL,
    name = "SightseeingAgent",
    description = "You are a tour guide helping people to create travel itineraries",
    instruction = """Your task is to recommend best places to visit in a location. 
        - Always recommend only 4 places.
        - If the user has not provided a location, ask him for same.
        - As a location user may provide city, state or country.
        - Continent is not a valid location.
    """
)

hotel_agent = LlmAgent(
    model = MODEL,
    name = "HotelAgent",
    description = "You are a hotel booking agent",
    instruction ="""Your task is to help user find a hotel.
        - Always recommned only two options.
        - Recommned only from budget hotels
        -  The room charges for a night should not be more than 30USD.
        - Always quote fares in the currency of the destination country.
    """
)

parallel_agents = Agent(
    name = "TravelPlannerAgent",
    sub_agents = [flight_agent, sightseeing_agent, hotel_agent],
    description = """You are travel planner. Fetch flight, sightseeing & hotel agents in parallel and create
        a travel itinerary for the user."""
)

async def main():
    runner = InMemoryRunner(agent = hotel_agent)
    user_query = """I am from Delhi, India. I am planning for vacation in Kerela.
      Help me with flights, sightseeing options and hotels. I am traveling on 8th Aug'26
      . I am travelling solo for 2 days. I am most interested in Munnar. My budget is Rs.35000."""
    event = await runner.run_debug(user_query)

if __name__ == "__main__":
    asyncio.run(main())
