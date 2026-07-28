from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai.types import Content, Part
import asyncio 

MODEL = "gemini-3.1-flash-lite"

flight_agent = LlmAgent(
    model = MODEL, 
    name = "FlightAgent",
    description = """
    Your departure city is {departure}.
    Tell me the optional route between flights.
    Answer in very short.
    """,
    tools = [PreloadMemoryTool()]
)

# ADK Runner
runner = InMemoryRunner(agent=flight_agent, app_name="flight_assistant")

async def main():
    SESSION_ID = "SI_0001"
    USER_ID = "CUST_001"

    # Create Session
    await runner.session_service.create_session(
        app_name = runner.app_name,
        user_id = USER_ID,
        session_id = SESSION_ID
    )

    print("[User] > I am travelling to Beijing, China from Kenya.")
    content = Content(role = "user", parts = [Part(text = "I am travelling to Beijing, China from Kenya.")])

    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
        # Check if event has content and is from the agent (not user).
        if event.content and event.content.parts and (event.author != "user"):
            for part in event.content.parts:
                if part.text:
                    print(f"[{flight_agent.name}] > {part.text}")

    session = await runner.session_service.get_session(
        app_name = runner.app_name,
        user_id = USER_ID,
        session_id = SESSION_ID
    )    
    await runner.memory_service.add_session_to_memory(session=session)

    print("\n")
    print("[User] > Where I am travelling?")
    content = Content(role = "user", parts=[Part(text = "Where I am travelling?")])

    async for event in runner.run_async(user_id = USER_ID, session_id = SESSION_ID, new_message=content):
        # Check if event has content and is from the agent (not user)
        if event.content and event.content.parts and (event.author != "user"):
            for part in event.content.parts:
                if part.text:
                    print(f"[{flight_agent.name}] > {part.text}")

if __name__ == "__main__":
    asyncio.run(main())