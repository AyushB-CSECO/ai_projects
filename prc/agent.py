from google.adk.agents import Agent 
from .tools import calculator
from .guardrails import input_guardrail

MODEL = "gemini-3.1-flash-lite"

root_agent = Agent(
    name = "MathGenius",
    model = MODEL,
    description = """You are a genius at mathematics who can do arithematic 
    calculations.""",
    global_instruction= """ You need to identify the two numbers that will be provided to you by the user and then use 
    the calculator tool to perform the required operations and then return the result
    """,
    tools= [calculator],
    before_model_callback = input_guardrail
    )