# PamsBeyond

PamsBeyond is a light, AI-assisted travel services helper supported by experienced travel agents across the Middle East, Austria, and the United States.

## Features

- Tourist visa requirements search
- Live officer consultation through FormSubmit
- Flight and accommodation search helpers
- Local assistance discovery
- Be Your Own Travel Planner: enter origin, destination, travel period, and budget to generate a practical itinerary with links to compare flights, stays, and places to explore
- About Pams, privacy policy, and terms of use sections

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Email setup

The officer request form and visa search notification use FormSubmit and send to `pamsbeyond@gmail.com`. Confirm the FormSubmit activation email before testing production submissions. No Gmail password or API key is stored in this project.

## Notes

The planner creates a useful client-side starting itinerary and links to external providers for the client to compare and reserve independently. Prices, availability, visa requirements, and government fees must be verified with the relevant official authorities or providers.
