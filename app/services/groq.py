from app.core.config import settings
from groq import Groq


def generate_recipe(ingredients: str, user_preferences: str) -> str:

    try:
        client = Groq(api_key=settings.groq_api_key)

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
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful culinary assistant that provides clear, easy-to-follow recipes.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=400,
        )

        return completion.choices[0].message.content

    except Exception as e:
        print(f"Groq Error: {e}")
        return (
            "Sorry, I'm unable to generate a recipe right now. "
            "Please try again in a few minutes."
        )
