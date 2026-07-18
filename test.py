from google import genai
from pydantic import BaseModel, Field 
from typing import List, Optional

class Recipe(BaseModel):
    name: str = Field(description="Name of the recipe")
    ingredients: List[str] = Field(description="List of ingredients")
    prep_time: Optional[int] = Field(description="Prep time in minutes")


if __name__ == "__main__":
    # Google SDK Client
    client = genai.Client()

    # Define the output of LLM in defined format
    interaction = client.interactions.create(
        model = "gemini-3.1-flash-lite",
        input = "What is the recipe of Peanut Butter & Jam Sandwich?",
        response_format= {
            "type": "text",
            "mime_type": "application/json",
            "schema": Recipe.model_json_schema() 
        }
    )

    recipe = Recipe.model_validate_json(interaction.output_text)
    print(recipe)

    print("\n===================\n")
    print(interaction.output_text)

    if False:
        # Basic Interaction
        interaction = client.interactions.create(
            model = "gemini-3.1-flash-lite",
            input = "Answer in short. Name all countries in G7 organization?"
        )

        print(interaction.output_text)

        # Multilayer Conversation
        interaction1 = client.interactions.create(
            model = "gemini-3.1-flash-lite",
            input = "I am 31 years old."
        )
        print(f"Response-1: {interaction1.output_text}")

        interaction2 = client.interactions.create(
            model = "gemini-3.1-flash-lite",
            input = "What is my age?",
            previous_interaction_id= interaction1.id
        )
        print(f"Response-2: {interaction2.output_text}")

