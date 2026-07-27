from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from .agent import root_agent

session_service = InMemorySessionService()

runner = Runner(
    agent= root_agent,
    app_name = "Maths Genius",
    session_service =session_service
)