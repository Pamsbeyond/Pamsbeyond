# PamsBeyond

## FX-Port + Gemini travel planner

The planner uses FX-Port for live flight searches and Google Gemini to generate a budget-aware itinerary and downloadable PDF. If live search or Gemini is unavailable, it automatically falls back to an offline budget plan.

Add these values in Streamlit Secrets:

```toml
GOOGLE_API_KEY = "your-gemini-api-key"
GEMINI_MODEL = "gemini-3.1-flash-lite"
FX_PORT_API_KEY = "fxp_test_your-key"
```

`GOOGLE_API_KEY` must be a Gemini API key from Google AI Studio, not a Google Maps key. Keep all keys in Streamlit Secrets and never commit them to GitHub.

For live flight search, enter a supported city or a three-letter airport code such as `CAI`, `VIE`, or `CDG`, and include a date in `YYYY-MM-DD` format.

## Run

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```
