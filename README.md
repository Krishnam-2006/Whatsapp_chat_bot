# AI WhatsApp Recipe Bot

![Tests](https://github.com/Krishnam-2006/Whatsapp_chat_bot/actions/workflows/tests.yml/badge.svg?branch=main)

An AI-powered WhatsApp chatbot that generates recipes from ingredients you have available. Built with FastAPI, PostgreSQL, Twilio WhatsApp, and Groq.

## Features

- Generate recipes from user-provided ingredients using Groq.
- Save dietary preferences such as vegan, vegetarian, and keto.
- Interact with the bot through WhatsApp.
- Store user preferences and processed-message records in PostgreSQL.
- Validate Twilio webhook signatures.
- Prevent duplicate message processing and recover stale processing records.
- Automated tests using pytest and pytest-cov.
- Continuous integration with GitHub Actions.

## Tech Stack

- Python 3.10+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Twilio WhatsApp API
- Groq API
- pytest, pytest-cov, and Ruff
- GitHub Actions

## Prerequisites

- Python 3.10 or newer
- PostgreSQL
- A Groq API key
- A Twilio account with WhatsApp Sandbox access
- ngrok for local webhook testing

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Krishnam-2006/Whatsapp_chat_bot.git
cd Whatsapp_chat_bot
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements-dev.txt
```

## Database Setup

Connect to PostgreSQL using an account with permission to create databases, then run:

```sql
CREATE DATABASE recipebot;
CREATE DATABASE test_recipebot;
```

Configure your database URLs in `.env`:

```dotenv
DATABASE_URL=postgresql://bloguser:your_password@localhost:5432/recipebot
TEST_DATABASE_URL=postgresql://bloguser:your_password@localhost:5432/test_recipebot
```

Replace `bloguser` and `your_password` with your own PostgreSQL credentials.

**Important:** `TEST_DATABASE_URL` must point to a dedicated database whose name contains `test_recipebot`. The test fixture drops and recreates tables, so never point it at a database containing data you need to keep.

## Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Set the following variables in `.env`:

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | API key for Groq |
| `TWILIO_ACCOUNT_SID` | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | Twilio authentication token |
| `TWILIO_WHATSAPP_NUMBER` | Your configured Twilio WhatsApp number |
| `TWILIO_WEBHOOK_URL` | Public HTTPS webhook URL ending in `/webhook` |
| `DATABASE_URL` | PostgreSQL application database URL |
| `TEST_DATABASE_URL` | PostgreSQL test database URL |

Keep your real `.env` file private. Never commit API keys, authentication tokens, or real database passwords to GitHub.

## Run the Application

Start FastAPI locally:

```bash
python -m uvicorn app.main:app --reload
```

The application will be available at:

`http://127.0.0.1:8000`

## Twilio and ngrok Setup

1. Start the application.
2. Expose the local server using ngrok:

   ```bash
   ngrok http 8000
   ```

3. Copy the HTTPS forwarding URL provided by ngrok.
4. Append `/webhook` to the URL. For example:

   ```text
   https://your-ngrok-url.ngrok-free.dev/webhook
   ```

5. Set this exact URL as `TWILIO_WEBHOOK_URL` in `.env`.
6. Configure the incoming-message webhook in your Twilio WhatsApp Sandbox settings to use the same URL and the HTTP POST method.
7. If your ngrok URL changes, update both the environment variable and the Twilio webhook configuration.

The URL must match because the application validates incoming Twilio request signatures.

## Usage

1. Open the WhatsApp Sandbox section in your Twilio Console.
2. Follow Twilio's instructions to join the Sandbox from your WhatsApp account using the displayed join code.
3. Send `DIET` to the Sandbox WhatsApp number.
4. Follow the bot's instructions to choose a dietary preference, such as vegan, vegetarian, or keto.
5. Send the ingredients you have available.
6. The bot generates and sends a recipe based on your ingredients and saved preferences.

## Running Tests

Ensure `TEST_DATABASE_URL` points to the dedicated `test_recipebot` database before running tests.

Run the full test suite:

```bash
python -m pytest -q
```

Run tests with coverage:

```bash
python -m pytest --cov=app --cov-report=term-missing -q
```

Run Ruff:

```bash
ruff check .
```

## Continuous Integration

GitHub Actions runs the test suite on pushes and pull requests using the workflow in `.github/workflows/tests.yml`.

Check the **Actions** tab on GitHub to view workflow runs and their results.

## Project Structure

```text
Whatsapp_chat_bot/
├── app/
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── crud.py
│   │   └── database.py
│   ├── models/
│   │   ├── processed_message.py
│   │   └── user.py
│   ├── routes/
│   │   └── webhook.py
│   ├── services/
│   │   ├── groq.py
│   │   ├── session.py
│   │   └── twilio.py
│   └── main.py
├── tests/
├── .github/
│   └── workflows/
│       └── tests.yml
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Future Improvements

- Add more conversational features and recipe personalization.
- Improve deployment and monitoring.
