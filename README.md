# iCSMS Email API

Backend service for email ingestion, classification, analytics, dashboard insights, suggestions, and settings management.

The application is built with **FastAPI** and exposes both legacy routes (`/email/...`) and v2 routes (`/email/v2/...`).

## Table of contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Environment variables](#environment-variables)
- [Local development](#local-development)
- [Running tests](#running-tests)
- [API docs](#api-docs)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Features

- Email-related processing and filtering endpoints
- Conversation summaries
- Issue, inquiry, and suggestion APIs (v2)
- Dashboard analytics endpoints
- Settings and notification channel management
- Gmail authorization callback endpoints

## Tech stack

- Python 3
- FastAPI + Uvicorn
- MongoDB (via `pymongo`)
- Google Generative AI / LangChain integration
- AWS Comprehend integration
- Pytest for tests

## Project structure

```text
iCSMS-email/
├── api/
│   ├── v2/                      # v2 routers, services, models, dependencies
│   ├── dashboard/               # legacy dashboard routes
│   ├── settings/                # legacy settings routes
│   ├── filtering/               # legacy filtering routes
│   ├── summary/                 # summary routes
│   ├── suggestions_page/        # suggestion filtering routes
│   └── email_filtering_and_info_generation/
├── external_services/           # AWS / Google cloud integrations
├── utils/                       # helper utilities
├── tests/                       # pytest test suite
├── main.py                      # FastAPI app entrypoint
├── requirements.txt             # local dependencies
├── docker-requirements.txt      # Docker dependencies
├── Dockerfile
└── vercel.json
```

## Prerequisites

- Python **3.12** recommended
- `pip`
- Access to required external services (MongoDB, Google APIs, AWS where applicable)

## Environment variables

Create a `.env` file in the repository root (`/home/runner/work/iCSMS-email/iCSMS-email/.env`).

At minimum, define:

```env
# MongoDB
MONGO_URI=your_mongodb_connection_string
MONGO_DB_NAME=your_database_name

# Google Generative AI
GOOGLE_API_KEY=your_google_api_key
GOOGLE_API_KEY_2=your_google_api_key_2
GOOGLE_API_KEY_4=your_google_api_key_4
GOOGLE_API_KEY_5=your_google_api_key_5
GOOGLE_API_KEY_6=your_google_api_key_6

# AWS Comprehend
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_DEFAULT_REGION=your_aws_region
```

### Credentials files

Some Gmail authorization flows expect credential files under:

`api/email_filtering_and_info_generation/credentialsForEmails/credentialsForEmail{id}/client_secret.json`

and may generate:

`gmail_token.json` in the same folder.

## Local development

1. Clone the repository:

   ```bash
   git clone https://github.com/rtweera/iCSMS-email.git
   cd iCSMS-email
   ```

2. Create and activate a virtual environment:

   **Linux/macOS**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   **Windows (cmd)**
   ```bat
   python -m venv .venv
   .venv\Scripts\activate.bat
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the API server:

   ```bash
   uvicorn main:app --reload
   ```

## Running tests

Run:

```bash
python -m pytest -q
```

Note: tests import `main.py`, and some modules initialize Google AI clients during import.  
If `GOOGLE_API_KEY` is not set, collection can fail before tests run.

## API docs

Once the server is running:

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
- Root redirects to docs: `http://127.0.0.1:8000/`

## Deployment

### Docker

Build:

```bash
docker build -t icsms-email .
```

Run:

```bash
docker run --rm -p 8080:8080 --env-file .env icsms-email
```

App will be available on `http://127.0.0.1:8080/docs`.

### Vercel

`vercel.json` is included and points to `main.py` using `@vercel/python`.

## Troubleshooting

- **`Did not find google_api_key` during tests/startup**  
  Set `GOOGLE_API_KEY` (and related keys if required by your flow).

- **Mongo connection issues**  
  Verify `MONGO_URI` and `MONGO_DB_NAME`.

- **AWS errors**  
  Verify `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_DEFAULT_REGION`.

## Contributing

- Open an issue for bugs or feature requests.
- Submit a pull request with clear descriptions and test evidence where possible.
