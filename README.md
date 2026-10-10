# PamsBeyond

## FX-Port + Groq Llama travel planner

The planner uses FX-Port for live flight searches and Groq Llama to generate a budget-aware itinerary and downloadable PDF. The Be your own travel planner section also includes 15 separately selectable destinations, each with real destination photography and a seven-day starting itinerary. If live search or Groq is unavailable, it automatically falls back to an offline budget plan.

The default model is `llama-3.3-70b-specdec`, selected for fast itinerary generation. You can override it with `GROQ_MODEL` if you need a different supported Groq model.

Add these values in Streamlit Secrets:

```toml
GROQ_API_KEY = "your-groq-api-key"
GROQ_MODEL = "llama-3.3-70b-specdec"
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

## Troubleshooting offline results

If the app returns an offline plan, it now displays the exact failed service and response. Confirm that the Streamlit Secrets names are exactly `GROQ_API_KEY`, `GROQ_MODEL`, and `FX_PORT_API_KEY`, then reboot the app. Use a real Groq model such as `llama-3.3-70b-specdec`, and use a valid three-letter airport code such as `CAI`, `VIE`, or `CDG`. FX-Port request and response formats can vary by account, so compare the displayed FX-Port error with your account’s API documentation.


Clients can select a destination card to open its dedicated itinerary, photo, and booking links. These are planning starting points; verify seasonal conditions, opening hours, prices, entry requirements, and availability before booking.

The secure Groq + FX-Port generator is the expanded Streamlit planner panel at the top of the app. The embedded custom-trip form provides a browser-side planning preview because browser JavaScript must not receive private API keys.
