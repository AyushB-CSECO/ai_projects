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
critic_agent = Agent(
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

# Sub-Agent 2: The Recommender
# Uses {user_watchlist} template - ADK auto-injects session state into the 
# instruction at runtime, so this agent is aware of what the user has saved.
root_agent = Agent(
    name = "RecommenderAgent",
    model = MODEL,
    description=(
        "Recommends movies based on user preferences, compare titles, and "
        "suggests what to watch next. Delegates here for recommendations, "
        "'what should I watch', or comparisons between movies."
    ),
    instruction = """You help users discover movies and decide what to watch.

The user's current watchlist: {user_watchlist}
Do not recommend movies already on their watchlist.

Workflow:
1. Use the fetch tool to look up movie info from trusted sites.
   Good URLs:
   - https://en.wikipedia.org/wiki/MOVIE_NAME_(film)
   - https://www.rottentomatoes.com/m/MOVIE_NAME
2. Personalize suggestions based on what the user says they like.

Output format (Markdown):

    ## If You Liked [Title], Try These

    | # | Movie | Why |
    |---|-------|-----|
    | 1 | [Title] | [Brief reason] |
    | 2 | [Title] | [Brief reason] |
    | 3 | [Title] | [Brief reason] |

    **Top pick:** [Title] — [Why]

Rules:
- Explain why each recommendation fits the user's taste.
- Use real data from fetched content. Do not make up scores.
- Keep responses concise.
""",
    tools = [fetch_toolset],
    generate_content_config = types.GenerateContentConfig(
        temperature = 0.5,
        max_output_tokens = 1024
    )
)