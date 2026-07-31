import asyncio 
from google.adk.agents import Agent 
from google.adk.runners import InMemoryRunner
from google.adk.code_executors import BuiltInCodeExecutor

MODEL = "gemini-3.1-flash-lite"

python_agent = Agent(
    model = MODEL, 
    name = "PythonHelper",
    description = "You are a coding agent who is well versed in python \
        programming language. You will be given a prompt with simple coding \
        tasks to perform. Execute the task and return the result",
    code_executor = BuiltInCodeExecutor()
)

async def main():
    runner = InMemoryRunner(agent = python_agent)
    events = await runner.run_debug("what is type and dtype of [1,2,3] object?")

if __name__ == "__main__":
    asyncio.run(main())