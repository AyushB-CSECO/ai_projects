import re
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

# Callback 1: before_model_callback (root agent)
def input_guardrail(
    callback_context: CallbackContext,
    llm_request: LlmRequest  
    ):

    user_prompt = llm_request.contents[-1]
    user_prompt = " ".join([
            part.text for part in (user_prompt.parts or []) 
            if getattr(part, "text", None)])
    num_input = re.findall(r"-?\d+", user_prompt)
    num_input = list(map(int, num_input))
    if 0 in num_input:
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text=(
                    "I can't process that request. 0 not allowed"
                ))],
            )
        )
    if any(x < 0 for x in num_input):
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text=(
                    "I can't process that request. Please don't input -ve number"
                ))],
            )
        )
    return None