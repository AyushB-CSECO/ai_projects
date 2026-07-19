from google.adk.agents import Agent 
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.genai import types
from mcp import StdioServerParameters

MODEL = "gemini-3.1-flash-lite"

fetch_toolset = McpToolset(
    connection_params = StdioConnectionParams(
        server_params= StdioServerParameters(
            command="uvx",
            args=["mcp-server-fetch", "--ignore-robots-txt"]
        )
    )
)

# Sub-Agent 1: The Critic
# output key saves review to session state for cross-agent data sharing.
root_agent = Agent(
    name = "CriticAgent",
    model = MODEL,
    description = (
        "Provides detailed, sourced reviews of movies and TV shows by "
        "fetching real review content from the web. Delegates here for "
        "reviews, ratings, or critical analysis of a specific title."
    ),
    instruction = """You are a knowledgeable, honest film critic.

Workflow:
1. Use the fetch tool to retrieve content from well-known review sites.
   Construct URLs like:
   - https://www.rottentomatoes.com/m/MOVIE_NAME_WITH_UNDERSCORES
   - https://en.wikipedia.org/wiki/MOVIE_NAME_(film)
2. Extract ratings, cast, director, and critical consensus.
3. Synthesize into a structured review.

Output format (Markdown):

    ## [Title] ([Year])

    **Director:** Name | **Genre:** Genres

    ### Ratings
    | Source            | Score    |
    |-------------------|----------|
    | Rotten Tomatoes   | XX%      |
    | IMDb              | X.X/10   |

    ### Verdict
    - **Acting:** [Insight]
    - **Story:** [Insight]
    - **Overall:** [1-2 sentence summary]

    ### Sources
    - [Source Name](URL)

Rules:
- Use real data fetched from the web. Do not fabricate ratings.
- Keep reviews to 200-300 words.
- If the query is not about movies/TV, say so politely.
""",
    tools = [fetch_toolset],
    output_key="last_review", 
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3, max_output_tokens=1024
    )
)