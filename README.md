# PamsBeyond

PamsBeyond is an AI-assisted travel services helper.

## Live AI travel planner

The planner tries live Amadeus flight search, then uses OpenAI to write a budget-aware itinerary and ReportLab to create a downloadable PDF. If live credentials are missing or live search fails, it automatically generates an offline budget plan and still provides a PDF download.

Add these values in Streamlit Secrets (never commit them):

```toml
AMADEUS_CLIENT_ID = "your-amadeus-client-id"
AMADEUS_CLIENT_SECRET = "your-amadeus-client-secret"
OPENAI_API_KEY = "your-openai-api-key"
OPENAI_MODEL = "gpt-4o-mini"
```

The app accepts a city or country for origin and destination. For the best live flight search, include a date in `YYYY-MM-DD` format in the travel period, for example `2027-06-10 to 2027-06-17`.

## Run

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

The app never stores API keys in the code. Prices and availability are supplied by third-party APIs and should be verified before booking.
