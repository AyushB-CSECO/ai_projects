"""
Critic's Cut v2 — Safety Guardrails
=====================================
ADK callbacks that intercept the agent pipeline at multiple levels:

  before_model_callback  → blocks prompt injection (root agent)
  after_model_callback   → redacts PII from responses (root agent)
  before_tool_callback   → validates tool inputs (WatchlistAgent)

These provide defense-in-depth: model-level, output-level, and tool-level.
"""

import re
import logging 
from typing import Optional, Any 

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, llm_request
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types 

from .models import GuardrailResult

logger = logging.getLogger(__name__)

# Prompt injection patterns (deterministic, zero external deps)

_INJECTION_PATTERNS: list[re.Pattern] = [
    re.compile(p, re.IGNORECASE)
        for p in [
            r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|directives|prompts)",
            r"reveal\s+(your\s+)?(system|initial)\s+(prompt|instruction)",
            r"you\s+are\s+now\s+in\s+.*mode",
            r"override\s+(system|safety)",
            r"act\s+as\s+(an?\s+)?(unrestricted|unfiltered|jailbroken)",
        ]
]

# PII patterns for output redaction
_PII_PATTERNS: dict[str, re.Pattern] = {
    "[EMAIL REDACTED]": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "[PHONE REDACTED]": re.compile(r"(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "[SSN REDACTED]": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
}

# Watchlist constraints 
MAX_WATCHLIST_SIZE = 10
MAX_TITLE_LENGTH = 100

def _extract_last_user_text(llm_request: llm_request) -> str:
    """Pull the text of the most recent user message from the LLM request"""
    if ((llm_request.contents) and (llm_request.contents[-1].role == "user")):
        parts = llm_request.contents[-1] or []
        return " ".join(p.text for p in parts if p.text)
    return ""

# CALLBACK 1: before_model_callback (root agent)
def input_guardrail(
        callback_context: CallbackContext,
        llm_request: llm_request
) -> Optional[LlmResponse]:
    """
    Block prompt-injection attempts before they reach the LLM.
    Returns an LLM response to short-circuit the call when a threat is 
    detected, or None to let the request proceed normally
    """
    text = _extract_last_user_text(llm_request)
    matched = [p.pattern for p in _INJECTION_PATTERNS if p.search(text)]

    if matched:
        result = GuardrailResult(passed=False, reason="prompt_injection"
                                    ,patterns_matched=matched)
        logger.warning("Input guardrail BLOCKED: %s", result.model_dump_json())
        return LlmResponse(
                content = types.Content(
                    role="model",               
                    parts=[types.Part(text=(
                        "I can't process that request. "
                        "If you have a question about movies or TV shows, I'm happy to help."
                        ))] 
            ) 
        )
    return None   

# CALLBACK 2: after_model_callback(root agent)
def output_guardrail(
        callback_context: CallbackContext,
        llm_response: LlmResponse
) -> Optional[LlmResponse]:
    "Redact PII from the model's response before it reaches the user."
    if not llm_response.content or not llm_response.content.parts:
        return None 
    
    modified = False 
    new_parts: list[types.Part] = []

    for part in llm_response.content.parts:
        text = part.text 
        if not text:
            new_parts.append(part)
            continue 
        for replacement, pattern in _PII_PATTERNS.items():
            if pattern.search(text):
                text = pattern.sub(replacement, text) 
                modified = True 
        new_parts.append(types.Part(text=text))

    if modified:
        logger.info("Output guardrail — PII redacted from response")
        return LlmResponse(content=types.Content(role="model", parts=new_parts))
    return None
