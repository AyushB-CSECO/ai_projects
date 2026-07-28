import asyncio 
from google.adk.agents import Agent 
from google.adk.runners import InMemoryRunner 

MODEL = "gemini-3.1-flash-lite"

flight_agent = Agent(
    model = MODEL,
    name = "FlightAgent",
    description = "Tell me about flights route between destinations.  \
        Answer in very short."
)

async def main():
    runner = InMemoryRunner(agent=flight_agent)
    events = await runner.run_debug("What is the flight route from India to Italy?")

if __name__ == "__main__":
    asyncio.run(main())
