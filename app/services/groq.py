import logging

from groq import Groq

from app.core.config import settings

logger = logging.getLogger(__name__)


def generate_recipe(ingredients: str, user_preferences: str) -> str:
    try:
        client = Groq(
            api_key=settings.groq_api_key,
            timeout=10.0,
        )

        prompt = f"""
You are a professional chef.

Create a recipe using these ingredients: {ingredients}.
User preferences: {user_preferences}

Keep the entire response under 1000 characters.

Provide:
1. Recipe title
2. Prep time
3. Cook time
4. Ingredients
5. Short step-by-step instructions
"""

        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful culinary assistant that "
                        "provides clear, easy-to-follow recipes."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_completion_tokens=1024,
            include_reasoning=False,
        )

        content = completion.choices[0].message.content

        if content and content.strip():
            return content.strip()

        logger.warning("Groq returned an empty recipe response")

    except Exception:
        logger.exception("Groq recipe generation failed")

    return (
        "Sorry, I'm unable to generate a recipe right now. "
        "Please try again in a few minutes."
    )
