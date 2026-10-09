# PamsBeyond

The planner uses FX-Port for live flight searches and OpenAI to generate a budget-aware itinerary and downloadable PDF. If live search is unavailable, it falls back to an offline budget plan.

Streamlit Secrets:

```toml
FX_PORT_API_KEY = "fxp_test_your-key"
OPENAI_API_KEY = "your-openai-key"
OPENAI_MODEL = "gpt-4o-mini"
```

Use a test key while developing. Keep all keys in Streamlit Secrets and never commit them to GitHub.

For live flight search, enter a supported city or a three-letter airport code such as `CAI`, `VIE`, or `CDG`, and include a date in `YYYY-MM-DD` format.
