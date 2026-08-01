from google.adk.agents import Agent 
from google.adk.events import Event
from google.adk import Workflow

MODEL = "gemini-3.1-flash-lite"

msg_processing_agent = Agent(
    model = MODEL, 
    name = "MsgProcessingAgent",
    instruction = """Classify user message into either "BUG", "CUSTOMER_SUPPORT",
        or "LOGISTICS". If you think a message applies to more than one category,
        reply with a comma seperated list of categories.
    """
)

def router(node_input: str):
    routes = [route.strip() for route in node_input.split(",")]
    return Event(route=routes)

def response_bug():
    return Event(message = "Handling Bugs...")

def response_support():
    return Event(message = "Handling Customer Support...")

def response_logistics():
    return Event(message = "Handling Logistics....")

response_dict = {
    "BUG": response_bug,
    "CUSTOMER_SUPPORT": response_support,
    "LOGISTICS": response_logistics
}

root_agent = Workflow(
    name = "routing_workflow",
    edges = [("START", msg_processing_agent, router),
        (router, response_dict)
    ]
)