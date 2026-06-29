from app.db.crud import get_user, create_user, update_user
from app.services.groq import generate_recipe


def handle_message(db, whatsapp_number, message):

    user = get_user(db, whatsapp_number)
    if not user:
        user = create_user(db, whatsapp_number)

    current_state = user.state
    reply_text = ""

    if current_state == "IDLE":
        if message.strip().upper() == "DIET":
            update_user(db, whatsapp_number, state="AWAITING_DIET")
            reply_text = "Please reply with your dietary preference or restriction (e.g., vegan, keto, vegetarian):"
        else:
            user_preferences = f"Diet: {user.diet_type}, Taste: {user.taste_preference}"
            reply_text = generate_recipe(message, user_preferences)

    elif current_state == "AWAITING_DIET":
        update_user(db, whatsapp_number, diet_type=message.strip(), state="IDLE")
        reply_text = f"Got it! Your diet preference ({message.strip()}) has been saved. What ingredients would you like to use for your next recipe?"

    elif current_state == "AWAITING_AGE":
        try:
            update_user(db, whatsapp_number, age=int(message.strip()), state="IDLE")
            reply_text = "Thanks! Your age has been saved. What ingredients are you working with today?"
        except ValueError:
            reply_text = "Please enter a valid number for your age."

    return reply_text
