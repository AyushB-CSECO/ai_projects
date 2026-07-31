"Agent with Graph Workflow"

from google.adk.agents import Agent 
from google.adk.events import Event 
from google.adk import Workflow
from pydantic import BaseModel

MODEL = "gemini-3.1-flash-lite"

city_generator_agent = Agent(
    model = MODEL, 
    name = "CityGenerator",
    description = "You provide a city name from all around the world randomly",
    instruction = """Choose only one city uniformly from cities around the world.
        Avoid repeating previous choices if possible. Return only the city name.
    """,
    output_schema = str,
    generate_content_config = {"temperature": 1.2}
)

class CityTime(BaseModel):
    time_info: str
    city: str 

def look_time_function(node_input: str):
    return CityTime(time_info = "12PM", city = node_input)

city_report_agent = Agent(
    model = MODEL,
    name = "CityReportAgent",
    description = "Report the city time.",
    instruction = """Both city name and time will be provided to you as input. 
        Output the following line:
        It is {CityTime.time_info} in {CityTime.city} right now.
    """,
    input_schema = CityTime,
    output_schema = str
)

def completed_msg_func(node_input: str):
    return Event(message = f"{node_input}\n WORKFLOW COMPLETED")

root_agent = Workflow(
    name = "TimeReportAgent",
    edges = [("START", city_generator_agent, look_time_function,
                city_report_agent, completed_msg_func)
    ]
)