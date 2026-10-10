# PamsBeyond

## FX-Port + Groq Llama travel planner

The planner uses FX-Port for live flight searches and Groq Llama to generate a budget-aware itinerary and downloadable PDF. The Be your own travel planner section also includes 15 separately selectable destinations, each with real destination photography and a seven-day starting itinerary. If live search or Groq is unavailable, it automatically falls back to an offline budget plan.

The default model is `llama-3.3-70b-versatile`, selected for stronger itinerary quality and practical reasoning. You can override it with `GROQ_MODEL` if you prefer a faster Llama 3.1 model.

Add these values in Streamlit Secrets:

```toml
GROQ_API_KEY = "your-groq-api-key"
GROQ_MODEL = "llama-3.3-70b-versatile"
FX_PORT_API_KEY = "fxp_test_your-key"
```

`GROQ_API_KEY` is created in the Groq Console. Keep all keys in Streamlit Secrets and never commit them to GitHub.

For live flight search, enter a supported city or a three-letter airport code such as `CAI`, `VIE`, or `CDG`, and include a date in `YYYY-MM-DD` format.

## Run

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud

1. Open your app in Streamlit Community Cloud.
2. Open **Settings → Secrets**.
3. Paste the TOML block above and replace both placeholder API keys.
4. Save the secrets and reboot the app.

Never put the Groq or FX-Port keys directly in `app.py`, JavaScript, or a public repository. The Groq request is made server-side so the key is not exposed to visitors.


Clients can select a destination card to open its dedicated itinerary, photo, and booking links. These are planning starting points; verify seasonal conditions, opening hours, prices, entry requirements, and availability before booking.
