# PamsBeyond — Visa & Travel Global Services ✈️

PamsBeyond is a dark red and black Streamlit travel-assistance website for visa guidance, flight discovery, accommodation search, local support, and full-trip planning.

## Features

### Visa Services

- Search visa requirements by origin country, destination, passport type, and visa type.
- View document checklists, entry terms, and estimated government fees.
- Request help from experienced officers after submitting visa details.
- Visa assistance offer starting from **$5.99** with free consultation messaging.

### Flight Reservations

- Search sample flight connections by departure city, destination city, and travel dates.
- Compare airlines, durations, stops, and sample fares.
- Open external booking links for flight reservations.

### Hotel Stays

- Search accommodation options by destination and dates.
- Filter properties by maximum nightly price.
- View ratings, sample amenities, and reservation links.

### Local Assistance

- Find airport pickup, taxi, transportation, restaurant, and hotel assistance.
- View the local support map powered by Leaflet and OpenStreetMap.
- Contact the officer desk for help.

### Full Trip Handling A–Z

The main page includes a full-trip handling service with two packages:

1. **Europe on your pocket** — visa preparation, flight and accommodation documents for visa use, a professional travel plan, and insurance-support messaging. Starting from **$7.99**.
2. **Big Apple City and 50 siblings** — guided DS-160 preparation and American travel planning. Starting from **$9.99**.

Each package includes buttons for:

- Checking visa requirements
- Submitting information and speaking with an officer

### Chatbot and Support

- Floating chatbot widget with Visa Help, Flight Deals, and Officer Desk options.
- Visa Help opens the Visa Services page.
- Flight Deals opens the Flight Reservations page.
- Officer requests open the consultation form.

### Trust and Legal Pages

- Privacy Policy: data security, document handling, automatic deletion, and email-use commitments.
- Terms of Service: service limitations, third-party bookings, user responsibilities, fees, refunds, and liability terms.

## Local Installation

### 1. Extract the project files

The project should contain:

```text
pamsbeyond/
├── app.py
├── requirements.txt
└── README.md
```

### 2. Create and activate a virtual environment (recommended)

#### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the website

```bash
streamlit run app.py
```

Streamlit will display a local address, usually:

```text
http://localhost:8501
```

Open that address in your browser. Do not open `app.py` directly by double-clicking it.

## Important Notes

- The interface is embedded inside Streamlit and uses CDN-loaded Tailwind CSS, Font Awesome, Leaflet, and OpenStreetMap tiles.
- Flight and hotel results are sample/demo data and include external booking links.
- Visa fees and requirements shown by the demo should be verified with the relevant embassy or official government website.
- The officer form currently demonstrates the request flow. Connect it to a secure backend or email service before production use.
- Privacy and Terms pages are website content and should be reviewed by qualified legal counsel before public launch.
- No API keys are required for the current demo version.

## License

Add your preferred license before publishing the project publicly.
