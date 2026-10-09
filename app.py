import base64
import io
import os
import re
from datetime import date, timedelta
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

import requests

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
except ImportError:
    A4 = None

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="PamsBeyond - Visa & Travel Global Services",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to hide Streamlit header and padding for full-screen feel
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
            max-width: 100% !important;
        }
        iframe {
            border: none;
        }
    </style>
""", unsafe_allow_html=True)

# Single Page HTML/CSS/JS Web App Component

def _secret(name):
    try:
        return st.secrets.get(name) or os.getenv(name)
    except Exception:
        return os.getenv(name)

def _iata(value):
    value=value.strip().upper()
    aliases={"CAIRO":"CAI","DUBAI":"DXB","LONDON":"LHR","PARIS":"CDG","VIENNA":"VIE","TORONTO":"YYZ","NEW YORK":"JFK","ISTANBUL":"IST","RIYADH":"RUH","DOHA":"DOH","SYDNEY":"SYD","TOKYO":"HND","ROME":"FCO","FRANKFURT":"FRA","BANGKOK":"BKK","KUALA LUMPUR":"KUL"}
    return value if re.fullmatch(r"[A-Z]{3}",value) else aliases.get(value)

def _fx_flights(origin,destination,period):
    key=_secret("FX_PORT_API_KEY")
    if not key: return None
    origin_code=_iata(origin); destination_code=_iata(destination)
    if not origin_code or not destination_code: return None
    match=re.search(r"(20\\d{2})[-/](\\d{1,2})[-/](\\d{1,2})",period)
    departure=f"{match.group(1)}-{int(match.group(2)):02d}-{int(match.group(3)):02d}" if match else (date.today()+timedelta(days=30)).isoformat()
    r=requests.post("https://api.fx-port.com/api/v1/get_flights",headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},json={"origin":origin_code,"destination":destination_code,"departure_date":departure,"cabin_class":"economy","passengers":{"adults":1}},timeout=25)
    r.raise_for_status()
    return {"origin_code":origin_code,"destination_code":destination_code,"departure":departure,"data":r.json()}

def _offline_plan(origin,destination,period,budget):
    return f"""Pams travel plan\n\nRoute: {origin} to {destination}\nTravel period: {period}\nTotal budget: ${budget:,.0f}\n\nSuggested allocation\n- Flights: about 35% (${budget*.35:,.0f})\n- Accommodation: about 35% (${budget*.35:,.0f})\n- Food and local transport: about 20% (${budget*.20:,.0f})\n- Experiences and contingency: about 10% (${budget*.10:,.0f})\n\nItinerary framework\n- Arrival day: settle in, local orientation, and a nearby evening walk.\n- Exploration days: one signature landmark, one local neighbourhood, and one flexible discovery activity each day.\n- Final day: reserve time for shopping, packing, and the return journey.\n\nThis is a planning estimate. Verify prices, availability, entry rules, and official visa information before booking."""

def _gemini_plan(origin,destination,period,budget,live):
    key=_secret("GOOGLE_API_KEY")
    if not key: return _offline_plan(origin,destination,period,budget)
    model=_secret("GEMINI_MODEL") or "gemini-2.0-flash"
    prompt=f"Create a complete practical travel itinerary from {origin} to {destination} for {period} with a total budget of ${budget}. Include day-by-day activities, hidden/local places, flights, accommodation, food, local transport, budget allocations, and booking advice. Never invent live prices. Use this live FX-Port flight response when present: {live}. Clearly label estimates and return plain text with headings."
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    response=requests.post(url,params={"key":key},json={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.4}},timeout=45)
    response.raise_for_status()
    data=response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]

def _make_pdf(text):
    if not A4: return None
    b=io.BytesIO(); doc=SimpleDocTemplate(b,pagesize=A4,rightMargin=16*mm,leftMargin=16*mm,topMargin=16*mm,bottomMargin=16*mm); styles=getSampleStyleSheet(); story=[Paragraph("Pams Travel Plan",styles["Title"]),Spacer(1,8)]
    for line in text.split("\\n"):
        if not line.strip(): story.append(Spacer(1,5)); continue
        story += [Paragraph(line.replace("&","&amp;"),styles["Heading2"] if line.endswith(":") else styles["BodyText"]),Spacer(1,3)]
    doc.build(story); return b.getvalue()

with st.expander("Be your own travel planner", expanded=False):
    st.caption("The planner tries FX-Port for live flights and Gemini for the itinerary. If keys are missing or live search is unavailable, Pams creates an offline budget plan and still provides a PDF.")
    with st.form("secure_fx_gemini_planner"):
        c1,c2=st.columns(2); origin=c1.text_input("Origin city or airport code",placeholder="Cairo or CAI"); destination=c2.text_input("Destination city or airport code",placeholder="Vienna or VIE"); period=st.text_input("Travel period",placeholder="2027-06-10 to 2027-06-17"); budget=st.number_input("Total budget (USD)",min_value=1.0,value=1500.0,step=50.0); submitted=st.form_submit_button("Search and generate my PDF")
    if submitted and origin and destination and period and budget:
        with st.spinner("Searching live flight options and writing your plan..."):
            try:
                live=_fx_flights(origin,destination,period); plan=_gemini_plan(origin,destination,period,budget,live); st.session_state["pams_plan_text"]=plan; st.session_state["pams_plan_pdf"]=_make_pdf(plan); st.session_state["pams_live_used"]=bool(live)
            except Exception:
                text=_offline_plan(origin,destination,period,budget)+"\\n\\nLive search or Gemini was unavailable, so this plan uses offline estimates."; st.session_state["pams_plan_text"]=text; st.session_state["pams_plan_pdf"]=_make_pdf(text); st.session_state["pams_live_used"]=False
    if st.session_state.get("pams_plan_text"):
        st.success("Live FX-Port flight data and Gemini used." if st.session_state.get("pams_live_used") else "Offline budget plan ready."); st.text_area("Generated plan",st.session_state["pams_plan_text"],height=280)
        if st.session_state.get("pams_plan_pdf"): st.download_button("Download travel plan PDF",st.session_state["pams_plan_pdf"],file_name="pams-travel-plan.pdf",mime="application/pdf")

html_code = """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PamsBeyond - Visa & Travel Global Services</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Leaflet OpenStreetMap CSS & JS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        brandRed: '#dc2626',
                        brandRedDark: '#991b1b',
                        brandNavy: '#dbeafe',
                        brandBlack: '#f8fafc',
                        brandGray: '#eef2ff',
                        brandCard: '#ffffff'
                    },
                    fontFamily: {
                        sans: ['Inter', 'system-ui', 'sans-serif'],
                    }
                }
            }
        }
    </script>
    <style>
        /* Custom scrollbars */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #f8fafc; }
        ::-webkit-scrollbar-thumb { background: #e60023; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #b3001b; }
        
        .glass-card {
            background: rgba(255, 255, 255, 0.92);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(124, 58, 237, 0.20);
        }
        .glass-card-hover {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .glass-card-hover:hover {
            transform: translateY(-4px);
            border-color: rgba(124, 58, 237, 0.6);
            box-shadow: 0 10px 30px -10px rgba(124, 58, 237, 0.25);
        }
        
        /* Dynamic Background Canvas */
        #bgCanvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 0;
            pointer-events: none;
        }

        /* Animated pulse glow */
        @keyframes redGlow {
            0%, 100% { box-shadow: 0 0 15px rgba(230, 0, 35, 0.4); }
            50% { box-shadow: 0 0 30px rgba(230, 0, 35, 0.8); }
        }
        .glow-red {
            animation: redGlow 3s infinite;
        }

        /* Logo blend styling without white background */
        .logo-container img {
            display: block;
            width: 100%;
            height: 100%;
            object-fit: contain;
            mix-blend-mode: normal;
            filter: none;
        }
    </style>
</head>
<body class="bg-brandBlack text-slate-900 font-sans min-h-screen flex flex-col relative overflow-x-hidden">

    <!-- LIVE ANIMATED CANVAS BACKGROUND (Flying Planes) -->
    <canvas id="bgCanvas"></canvas>

    <!-- TOP HEADER / NAVIGATION -->
    <header class="sticky top-0 z-40 glass-card border-b border-brandRed/20 px-4 lg:px-8 py-3">
        <div class="max-w-7xl mx-auto flex items-center justify-between">
            <!-- Brand Logo & Name -->
            <a href="#" onclick="switchTab('home')" class="flex items-center gap-3 group">
                <div class="relative w-20 h-14 flex items-center justify-center bg-brandRed rounded-xl overflow-hidden border-2 border-purple-200 shadow-lg logo-container">
                    <span class="text-3xl font-serif italic font-black text-white tracking-tight">Pams</span>
                    <i class="fa-solid fa-rocket absolute text-white text-xs -right-1 top-1 rotate-12"></i>
                    <i class="fa-solid fa-suitcase-rolling absolute text-purple-200 text-[11px] left-1 bottom-1 -rotate-12"></i>
                </div>
                <div>
                    <span class="text-2xl font-black tracking-tight text-slate-900 uppercase">Pams<span class="text-brandRed">Beyond</span></span>
                    <p class="text-[10px] text-slate-500 tracking-widest uppercase font-semibold">AI Travel Services</p>
                </div>
            </a>

            <!-- Navigation Links -->
            <nav class="hidden md:flex items-center gap-1 bg-white/80 p-1.5 rounded-full border border-gray-800">
                <button onclick="switchTab('visa')" class="nav-btn px-4 py-2 rounded-full text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-brandRed/20 transition flex items-center gap-2">
                    <i class="fa-solid fa-passport text-brandRed"></i> Visas
                </button>
                <button onclick="switchTab('flights')" class="nav-btn px-4 py-2 rounded-full text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-brandRed/20 transition flex items-center gap-2">
                    <i class="fa-solid fa-plane-departure text-brandRed"></i> Flights
                </button>
                <button onclick="switchTab('hotels')" class="nav-btn px-4 py-2 rounded-full text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-brandRed/20 transition flex items-center gap-2">
                    <i class="fa-solid fa-hotel text-brandRed"></i> Stays
                </button>
                <button onclick="switchTab('help')" class="nav-btn px-4 py-2 rounded-full text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-brandRed/20 transition flex items-center gap-2">
                    <i class="fa-solid fa-map-location-dot text-brandRed"></i> Local Assistance
                </button>
            </nav>

            <!-- Quick Live Chat Button -->
            <button onclick="toggleChatbot()" class="px-5 py-2.5 rounded-full bg-brandRed hover:bg-brandRedDark text-slate-900 font-bold text-xs tracking-wider transition shadow-lg shadow-brandRed/30 flex items-center gap-2">
                <i class="fa-solid fa-comments"></i> Live Chat
            </button>
        </div>
    </header>

    <!-- MAIN CONTENT CONTAINER -->
    <main class="relative z-10 flex-grow max-w-7xl w-full mx-auto px-4 py-8">

        <!-- ================================================================= -->
        <!-- VIEW 0: MAIN DASHBOARD -->
        <!-- ================================================================= -->
        <section id="view-home" class="space-y-10">
            <!-- Hero Banner -->
            <div class="text-center space-y-4 max-w-3xl mx-auto pt-6">
                <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brandRed/10 border border-brandRed/30 text-brandRed text-xs font-bold uppercase tracking-wider">
                    <i class="fa-solid fa-compass"></i> Worldwide Visa & Travel Assistance
                </div>
                <h1 class="text-3xl sm:text-5xl font-extrabold text-slate-900 tracking-tight leading-tight">
                    Tell us where the next overseas plans
                </h1>
                <p class="text-slate-500 text-sm sm:text-base">
                    Select your travel service below. From instant global visa requirements to flights, accommodations, and local ground support.
                </p>
            </div>

            <!-- Dashboard Options -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">

                <!-- CARD 1 -->
                <div onclick="switchTab('visa')" class="glass-card glass-card-hover p-6 sm:p-8 rounded-2xl cursor-pointer group relative overflow-hidden flex flex-col justify-between min-h-[220px]">
                    <div class="absolute -right-8 -bottom-8 opacity-10 group-hover:opacity-25 transition text-brandRed">
                        <i class="fa-solid fa-passport text-9xl"></i>
                    </div>
                    <div>
                        <div class="w-12 h-12 rounded-xl bg-brandRed/20 border border-brandRed/40 flex items-center justify-center text-brandRed text-2xl mb-4 group-hover:bg-brandRed group-hover:text-slate-900 transition">
                            <i class="fa-solid fa-passport"></i>
                        </div>
                        <span class="text-xs font-bold text-brandRed uppercase tracking-widest">What we can do for you</span>
                        <h2 class="text-2xl font-bold text-slate-900 mt-1 group-hover:text-brandRed transition">Planning to travel to get yourself overseas?</h2>
                        <p class="text-slate-500 text-xs sm:text-sm mt-2">Instant search for worldwide visa requirements, documentation, exact official fees, and direct officer support.</p>
                    </div>
                    <div class="mt-6 flex items-center text-xs font-bold text-brandRed group-hover:translate-x-2 transition">
                        Explore Visa Requirements <i class="fa-solid fa-arrow-right ml-2"></i>
                    </div>
                </div>

                <!-- CARD 2 -->
                <div onclick="switchTab('flights')" class="glass-card glass-card-hover p-6 sm:p-8 rounded-2xl cursor-pointer group relative overflow-hidden flex flex-col justify-between min-h-[220px]">
                    <div class="absolute -right-8 -bottom-8 opacity-10 group-hover:opacity-25 transition text-brandRed">
                        <i class="fa-solid fa-plane text-9xl"></i>
                    </div>
                    <div>
                        <div class="w-12 h-12 rounded-xl bg-brandRed/20 border border-brandRed/40 flex items-center justify-center text-brandRed text-2xl mb-4 group-hover:bg-brandRed group-hover:text-slate-900 transition">
                            <i class="fa-solid fa-plane-departure"></i>
                        </div>
                        <span class="text-xs font-bold text-brandRed uppercase tracking-widest">What we can do for you</span>
                        <h2 class="text-2xl font-bold text-slate-900 mt-1 group-hover:text-brandRed transition">Need a flight booking?</h2>
                        <p class="text-slate-500 text-xs sm:text-sm mt-2">Scans global airlines & booking platforms by city to display live lowest rates and best connection routes.</p>
                    </div>
                    <div class="mt-6 flex items-center text-xs font-bold text-brandRed group-hover:translate-x-2 transition">
                        Find Best Flights <i class="fa-solid fa-arrow-right ml-2"></i>
                    </div>
                </div>

                <!-- CARD 3 -->
                <div onclick="switchTab('hotels')" class="glass-card glass-card-hover p-6 sm:p-8 rounded-2xl cursor-pointer group relative overflow-hidden flex flex-col justify-between min-h-[220px]">
                    <div class="absolute -right-8 -bottom-8 opacity-10 group-hover:opacity-25 transition text-brandRed">
                        <i class="fa-solid fa-hotel text-9xl"></i>
                    </div>
                    <div>
                        <div class="w-12 h-12 rounded-xl bg-brandRed/20 border border-brandRed/40 flex items-center justify-center text-brandRed text-2xl mb-4 group-hover:bg-brandRed group-hover:text-slate-900 transition">
                            <i class="fa-solid fa-hotel"></i>
                        </div>
                        <span class="text-xs font-bold text-brandRed uppercase tracking-widest">What we can do for you</span>
                        <h2 class="text-2xl font-bold text-slate-900 mt-1 group-hover:text-brandRed transition">Any accommodation?</h2>
                        <p class="text-slate-500 text-xs sm:text-sm mt-2">Discover high-rated properties globally with interactive price filters and luxury or budget recommendations.</p>
                    </div>
                    <div class="mt-6 flex items-center text-xs font-bold text-brandRed group-hover:translate-x-2 transition">
                        Search Accommodations <i class="fa-solid fa-arrow-right ml-2"></i>
                    </div>
                </div>

                <!-- CARD 4 -->
                <div onclick="switchTab('help')" class="glass-card glass-card-hover p-6 sm:p-8 rounded-2xl cursor-pointer group relative overflow-hidden flex flex-col justify-between min-h-[220px]">
                    <div class="absolute -right-8 -bottom-8 opacity-10 group-hover:opacity-25 transition text-brandRed">
                        <i class="fa-solid fa-taxi text-9xl"></i>
                    </div>
                    <div>
                        <div class="w-12 h-12 rounded-xl bg-brandRed/20 border border-brandRed/40 flex items-center justify-center text-brandRed text-2xl mb-4 group-hover:bg-brandRed group-hover:text-slate-900 transition">
                            <i class="fa-solid fa-map-location-dot"></i>
                        </div>
                        <span class="text-xs font-bold text-brandRed uppercase tracking-widest">What we can do for you</span>
                        <h2 class="text-2xl font-bold text-slate-900 mt-1 group-hover:text-brandRed transition">You are already there and need any help?</h2>
                        <p class="text-slate-500 text-xs sm:text-sm mt-2">Airport pickup, taxis, local transit, top nearby restaurants and hotels powered by live map discovery.</p>
                    </div>
                    <div class="mt-6 flex items-center text-xs font-bold text-brandRed group-hover:translate-x-2 transition">
                        Locate Nearby Services <i class="fa-solid fa-arrow-right ml-2"></i>
                    </div>
                </div>

            </div>
                <!-- CARD 5: BE YOUR OWN TRAVEL PLANNER -->
                <div onclick="switchTab('planner')" class="glass-card glass-card-hover p-6 sm:p-8 rounded-2xl cursor-pointer group relative overflow-hidden flex flex-col justify-between min-h-[240px] md:col-span-2 border-purple-300/70">
                    <div class="absolute -right-8 -bottom-8 opacity-10 group-hover:opacity-25 transition text-purple-600">
                        <i class="fa-solid fa-compass-drafting text-9xl"></i>
                    </div>
                    <div>
                        <div class="w-12 h-12 rounded-xl bg-purple-100 border border-purple-300 flex items-center justify-center text-purple-600 text-2xl mb-4 group-hover:bg-purple-600 group-hover:text-white transition">
                            <i class="fa-solid fa-compass-drafting"></i>
                        </div>
                        <span class="text-xs font-bold text-purple-600 uppercase tracking-widest">New: Personal travel planning</span>
                        <h2 class="text-2xl font-bold text-slate-900 mt-1 group-hover:text-purple-600 transition">Be your own travel planner</h2>
                        <p class="text-slate-600 text-xs sm:text-sm mt-2">Tell Pams your origin, destination, dates, and budget. Receive a practical itinerary with flights, stays, hidden places, and booking links.</p>
                    </div>
                    <div class="mt-6 flex items-center text-xs font-bold text-purple-600 group-hover:translate-x-2 transition">
                        Build My Travel Plan <i class="fa-solid fa-arrow-right ml-2"></i>
                    </div>
                </div>

            <!-- ABOUT PAMS -->
            <section class="glass-card rounded-3xl p-6 sm:p-10 border border-purple-200 overflow-hidden">
                <div class="grid lg:grid-cols-[1.1fr_.9fr] gap-8 items-center">
                    <div>
                        <span class="text-brandRed text-xs font-bold uppercase tracking-widest">About Pams</span>
                        <h2 class="text-3xl sm:text-4xl font-black text-slate-900 mt-2">Travel support that feels human, wherever you start.</h2>
                        <p class="text-slate-600 mt-4 leading-relaxed">Pams is an AI travel services helper built with the experience of expert travel agents working across the Middle East, Austria, and the United States. It gives travellers a faster way to understand their options and plan with confidence.</p>
                        <div class="grid sm:grid-cols-2 gap-4 mt-6">
                            <div class="rounded-2xl bg-blue-50 border border-blue-200 p-4"><b class="text-slate-900">Is Pams human?</b><p class="text-slate-600 text-sm mt-1">Pams is an AI assistant supported by travel agents. Ask to talk to an agent and connect with a person in seconds, free of charge.</p></div>
                            <div class="rounded-2xl bg-purple-50 border border-purple-200 p-4"><b class="text-slate-900">Is it free?</b><p class="text-slate-600 text-sm mt-1">Pams is free to use. Fees apply only when you request an external service handled by an expert agent, such as application support or an embassy appointment.</p></div>
                        </div>
                        <p class="text-xs text-slate-500 mt-4">We do not archive personal information for these planning tools. External services are handled under the legal terms described in our policies.</p>
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <img class="h-44 w-full object-cover rounded-2xl border-4 border-white shadow-xl rotate-[-2deg]" src="https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=700&q=80" alt="Airplane travelling above the clouds">
                        <img class="h-44 w-full object-cover rounded-2xl border-4 border-white shadow-xl rotate-[2deg] mt-7" src="https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=700&q=80" alt="Beautiful travel destination">
                        <img class="h-36 w-full object-cover rounded-2xl border-4 border-white shadow-xl col-span-2" src="https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=900&q=80" alt="Travel planning at a desk">
                    </div>
                </div>
            </section>

        </section>


        <!-- ================================================================= -->

        <!-- ================================================================= -->
        <!-- VIEW: BE YOUR OWN TRAVEL PLANNER -->
        <section id="view-planner" class="space-y-8 hidden">
            <div class="flex items-center justify-between border-b border-purple-200 pb-4">
                <div><span class="text-purple-600 text-xs font-bold tracking-widest uppercase">Personal planning assistant</span><h1 class="text-3xl font-extrabold text-slate-900">Be your own travel planner</h1><p class="text-slate-600 text-sm mt-2">Share your trip parameters and Pams will build a practical starting itinerary around your budget.</p></div>
                <button onclick="switchTab('home')" class="text-xs text-slate-500 hover:text-slate-900 flex items-center gap-1"><i class="fa-solid fa-arrow-left"></i> Back to Main</button>
            </div>
            <div class="glass-card p-6 sm:p-8 rounded-2xl border border-purple-200">
                <form onsubmit="event.preventDefault(); generateTravelPlan();" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div><label class="block text-xs font-bold text-slate-600 uppercase mb-2">Origin country</label><select id="plannerOrigin" required class="w-full bg-white border border-blue-200 rounded-xl px-4 py-3 text-sm text-slate-900"><option value="">Select origin...</option></select></div>
                    <div><label class="block text-xs font-bold text-slate-600 uppercase mb-2">Destination</label><select id="plannerDestination" required class="w-full bg-white border border-blue-200 rounded-xl px-4 py-3 text-sm text-slate-900"><option value="">Select destination...</option></select></div>
                    <div><label class="block text-xs font-bold text-slate-600 uppercase mb-2">Travel period</label><input id="plannerPeriod" required placeholder="e.g. 7 days in October" class="w-full bg-white border border-blue-200 rounded-xl px-4 py-3 text-sm text-slate-900"></div>
                    <div><label class="block text-xs font-bold text-slate-600 uppercase mb-2">Total budget</label><input id="plannerBudget" required type="number" min="1" placeholder="e.g. 1500" class="w-full bg-white border border-blue-200 rounded-xl px-4 py-3 text-sm text-slate-900"></div>
                    <div class="md:col-span-2"><button type="submit" class="w-full py-4 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-bold text-sm tracking-wide transition shadow-lg shadow-purple-200 flex items-center justify-center gap-2"><i class="fa-solid fa-wand-magic-sparkles"></i> Generate My Travel Plan</button></div>
                </form>
            </div>
            <div id="plannerResults" class="hidden glass-card p-6 sm:p-8 rounded-2xl border-l-4 border-l-purple-600 space-y-5"></div>
        </section>

        <!-- VIEW 1: VISA REQUIREMENTS -->
        <!-- ================================================================= -->
        <section id="view-visa" class="space-y-8 hidden">
            <div class="flex items-center justify-between border-b border-gray-800 pb-4">
                <div>
                    <span class="text-brandRed text-xs font-bold tracking-widest uppercase">What we can do for you</span>
                    <h1 class="text-3xl font-extrabold text-slate-900">Global Visa & Requirements Search</h1>
                </div>
                <button onclick="switchTab('home')" class="text-xs text-slate-500 hover:text-slate-900 flex items-center gap-1">
                    <i class="fa-solid fa-arrow-left"></i> Back to Main
                </button>
            </div>

            <div class="glass-card p-6 sm:p-8 rounded-2xl space-y-6">
                <form id="visaForm" onsubmit="event.preventDefault(); runVisaSearch();" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-flag text-brandRed"></i> 1. Origin Country</label>
                        <select id="visaOrigin" required class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                            <option value="">Select Origin...</option>
                        </select>
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-location-dot text-brandRed"></i> 2. Destination</label>
                        <select id="visaDest" required class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                            <option value="">Select Destination...</option>
                        </select>
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-id-card text-brandRed"></i> 3. Passport Type</label>
                        <select id="passportType" required class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                            <option value="Ordinary Passport">Ordinary (Standard Tourist)</option>
                            <option value="Diplomatic Passport">Diplomatic Passport</option>
                            <option value="Official / Service Passport">Official / Service</option>
                            <option value="Refugee Travel Document">Refugee / Travel Document</option>
                        </select>
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-briefcase text-brandRed"></i> 4. Visa Type</label>
                        <select id="visaType" required class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                            <option value="Tourist Visa">Tourist Visa</option>
                        </select>
                    </div>

                    <div class="md:col-span-2 lg:col-span-4 mt-2">
                        <button type="submit" class="w-full py-4 rounded-xl bg-brandRed hover:bg-brandRedDark text-slate-900 font-bold text-sm tracking-wide transition shadow-lg shadow-brandRed/30 flex items-center justify-center gap-2">
                            <i class="fa-solid fa-magnifying-glass"></i> Search Requirements & Official Fees
                        </button>
                    </div>
                </form>
            </div>

            <!-- Visa Results -->
            <div id="visaResults" class="hidden space-y-6">
                <div class="glass-card p-6 sm:p-8 rounded-2xl border-l-4 border-l-brandRed space-y-6">
                    <div class="flex flex-wrap items-center justify-between gap-4 border-b border-gray-800 pb-4">
                        <div>
                            <span class="text-xs text-brandRed font-bold uppercase tracking-wider">Search Result</span>
                            <h2 id="resultTitle" class="text-2xl font-bold text-slate-900">Egypt ➔ Canada (Visitor Visa)</h2>
                        </div>
                        <div class="text-right">
                            <span class="text-xs text-slate-500 block">Official Govt Fee</span>
                            <span id="resultFee" class="text-2xl font-black text-brandRed">$100 USD + $85 Biometrics</span>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <h3 class="text-sm font-bold text-slate-900 uppercase mb-3 flex items-center gap-2">
                                <i class="fa-solid fa-file-shield text-brandRed"></i> Required Documents Checklist
                            </h3>
                            <ul id="docList" class="space-y-2 text-xs sm:text-sm text-slate-600"></ul>
                        </div>
                        <div>
                            <h3 class="text-sm font-bold text-slate-900 uppercase mb-3 flex items-center gap-2">
                                <i class="fa-solid fa-gavel text-brandRed"></i> Key Terms & Entry Conditions
                            </h3>
                            <ul id="termsList" class="space-y-2 text-xs sm:text-sm text-slate-600"></ul>
                        </div>
                    </div>

                    <!-- HANDLING FOR YOU BOX -->
                    <div class="mt-6 p-6 rounded-xl bg-gradient-to-r from-brandNavy to-brandGray border border-brandRed/40 flex flex-col sm:flex-row items-center justify-between gap-4 glow-red">
                        <div>
                            <span class="bg-brandRed text-slate-900 text-[10px] font-extrabold px-2 py-0.5 rounded uppercase">Want to talk live to the agent</span>
                            <h3 class="text-lg font-bold text-slate-900 mt-1">Talk live with an experienced agent</h3>
                            <p id="offerText" class="text-xs text-slate-600 mt-1">Ask your questions directly and receive guidance from our officer team.</p>
                        </div>
                        <button onclick="triggerHandledAssistance()" class="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-brandRed hover:bg-brandRedDark text-slate-900 font-extrabold text-xs whitespace-nowrap transition shadow-lg">
                            Talk to the agent live <i class="fa-solid fa-headset ml-1"></i>
                        </button>
                    </div>
                </div>
            </div>
        </section>


        <!-- ================================================================= -->
        <!-- VIEW 2: FLIGHT BOOKING SEARCH (CITY BASED) -->
        <!-- ================================================================= -->
        <section id="view-flights" class="space-y-8 hidden">
            <div class="flex items-center justify-between border-b border-gray-800 pb-4">
                <div>
                    <span class="text-brandRed text-xs font-bold tracking-widest uppercase">What we can do for you</span>
                    <h1 class="text-3xl font-extrabold text-slate-900">Need a suitable flight?</h1>
                </div>
                <button onclick="switchTab('home')" class="text-xs text-slate-500 hover:text-slate-900 flex items-center gap-1">
                    <i class="fa-solid fa-arrow-left"></i> Back to Main
                </button>
            </div>

            <div class="glass-card p-6 sm:p-8 rounded-2xl space-y-6">
                <div class="flex items-center gap-4 border-b border-gray-800 pb-4">
                    <label class="inline-flex items-center gap-2 cursor-pointer">
                        <input type="radio" name="tripType" value="oneway" class="accent-brandRed" onchange="toggleReturnDate(false)">
                        <span class="text-sm font-semibold text-gray-200">One Way</span>
                    </label>
                    <label class="inline-flex items-center gap-2 cursor-pointer">
                        <input type="radio" name="tripType" value="return" checked class="accent-brandRed" onchange="toggleReturnDate(true)">
                        <span class="text-sm font-semibold text-gray-200">Return Trip</span>
                    </label>
                </div>

                <!-- Flight Search Form with Cities -->
                <form id="flightForm" onsubmit="event.preventDefault(); runFlightSearch();" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-plane-departure text-brandRed"></i> Departure City</label>
                        <select id="flightOriginCity" required class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                            <option value="">Select Departure City...</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-plane-arrival text-brandRed"></i> Destination City</label>
                        <select id="flightDestCity" required class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                            <option value="">Select Arrival City...</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-calendar text-brandRed"></i> Departure Date</label>
                        <input type="date" id="flightDepDate" required class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                    </div>
                    <div id="returnDateContainer">
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-calendar-check text-brandRed"></i> Return Date</label>
                        <input type="date" id="flightRetDate" class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                    </div>

                    <div class="md:col-span-2 lg:col-span-4 mt-2">
                        <button type="submit" class="w-full py-4 rounded-xl bg-brandRed hover:bg-brandRedDark text-slate-900 font-bold text-sm tracking-wide transition shadow-lg shadow-brandRed/30 flex items-center justify-center gap-2">
                            <i class="fa-solid fa-magnifying-glass"></i> Scan Airlines & Compare Fares
                        </button>
                    </div>
                </form>
            </div>

            <!-- Flight Results -->
            <div id="flightResults" class="hidden space-y-4">
                <h3 class="text-xl font-bold text-slate-900 flex items-center gap-2">
                    <i class="fa-solid fa-plane text-brandRed"></i> Available Connection Deals
                </h3>
                <div id="flightList" class="space-y-4"></div>
            </div>
        </section>


        <!-- ================================================================= -->
        <!-- VIEW 3: ACCOMMODATION -->
        <!-- ================================================================= -->
        <section id="view-hotels" class="space-y-8 hidden">
            <div class="flex items-center justify-between border-b border-gray-800 pb-4">
                <div>
                    <span class="text-brandRed text-xs font-bold tracking-widest uppercase">What we can do for you</span>
                    <h1 class="text-3xl font-extrabold text-slate-900">Find High-Rated Accommodations</h1>
                </div>
                <button onclick="switchTab('home')" class="text-xs text-slate-500 hover:text-slate-900 flex items-center gap-1">
                    <i class="fa-solid fa-arrow-left"></i> Back to Main
                </button>
            </div>

            <div class="glass-card p-6 sm:p-8 rounded-2xl space-y-6">
                <form id="hotelForm" onsubmit="event.preventDefault(); runHotelSearch();" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-city text-brandRed"></i> Destination City</label>
                        <select id="hotelLocation" required class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                            <option value="">Choose Destination City...</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-calendar-day text-brandRed"></i> Check-in</label>
                        <input type="date" id="hotelCheckIn" required class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-calendar-day text-brandRed"></i> Check-out</label>
                        <input type="date" id="hotelCheckOut" required class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-users text-brandRed"></i> Guests & Rooms</label>
                        <select id="hotelGuests" class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                            <option value="1 Guest, 1 Room">1 Guest, 1 Room</option>
                            <option value="2 Guests, 1 Room" selected>2 Guests, 1 Room</option>
                            <option value="4 Guests, 2 Rooms">4 Guests, 2 Rooms</option>
                        </select>
                    </div>

                    <div class="md:col-span-2 lg:col-span-4">
                        <button type="submit" class="w-full py-4 rounded-xl bg-brandRed hover:bg-brandRedDark text-slate-900 font-bold text-sm tracking-wide transition shadow-lg shadow-brandRed/30 flex items-center justify-center gap-2">
                            <i class="fa-solid fa-hotel"></i> Search Available Stays
                        </button>
                    </div>
                </form>
            </div>

            <!-- Hotel Output -->
            <div id="hotelResults" class="hidden space-y-6">
                <div class="glass-card p-4 rounded-xl flex flex-wrap items-center justify-between gap-4">
                    <div class="flex items-center gap-3">
                        <i class="fa-solid fa-sliders text-brandRed text-lg"></i>
                        <span class="text-sm font-bold text-slate-900">Price Filter:</span>
                        <input type="range" id="priceRange" min="50" max="1000" step="50" value="1000" oninput="filterHotels()" class="accent-brandRed cursor-pointer">
                        <span id="priceRangeValue" class="text-sm font-black text-brandRed">Up to $1000/night</span>
                    </div>
                    <div class="text-xs text-slate-500">
                        <span id="hotelCount">0</span> top-rated properties available
                    </div>
                </div>

                <div id="hotelList" class="grid grid-cols-1 md:grid-cols-3 gap-6"></div>
            </div>
        </section>


        <!-- ================================================================= -->
        <!-- VIEW 4: ON-GROUND HELP -->
        <!-- ================================================================= -->
        <section id="view-help" class="space-y-8 hidden">
            <div class="flex items-center justify-between border-b border-gray-800 pb-4">
                <div>
                    <span class="text-brandRed text-xs font-bold tracking-widest uppercase">What we can do for you</span>
                    <h1 class="text-3xl font-extrabold text-slate-900">Already There & Need Help?</h1>
                </div>
                <button onclick="switchTab('home')" class="text-xs text-slate-500 hover:text-slate-900 flex items-center gap-1">
                    <i class="fa-solid fa-arrow-left"></i> Back to Main
                </button>
            </div>

            <div class="glass-card p-6 rounded-2xl space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-location-crosshairs text-brandRed"></i> Current Location / City</label>
                        <input type="text" id="groundLocation" placeholder="e.g. Cairo, Paris, Toronto, Dubai" value="Cairo" class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-2"><i class="fa-solid fa-concierge-bell text-brandRed"></i> Required Assistance</label>
                        <select id="groundService" class="w-full bg-white border border-gray-700 rounded-xl px-4 py-3 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                            <option value="Airport Pickup / Taxi">Airport Pickup & Taxi Booking</option>
                            <option value="Domestic Transportation">Domestic Transportation & Rentals</option>
                            <option value="Nearby Restaurants">Nearby Top Rated Restaurants</option>
                            <option value="Nearby Hotels">Emergency Nearby Hotels</option>
                        </select>
                    </div>
                    <div class="flex items-end">
                        <button onclick="runGroundSearch()" class="w-full py-3.5 rounded-xl bg-brandRed hover:bg-brandRedDark text-slate-900 font-bold text-sm tracking-wide transition shadow-lg shadow-brandRed/30 flex items-center justify-center gap-2">
                            <i class="fa-solid fa-map-pin"></i> Locate Nearby Services
                        </button>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div class="lg:col-span-2 glass-card rounded-2xl overflow-hidden p-2 min-h-[400px] flex flex-col">
                    <div id="map" class="w-full h-full min-h-[400px] rounded-xl z-10"></div>
                </div>

                <div class="glass-card p-6 rounded-2xl space-y-4">
                    <h3 class="text-lg font-bold text-slate-900 border-b border-gray-800 pb-2 flex items-center gap-2">
                        <i class="fa-solid fa-shield-halved text-brandRed"></i> Verified Local Operators
                    </h3>
                    <div id="providerList" class="space-y-3 text-xs"></div>
                </div>
            </div>
        </section>

    </main>


    <!-- ================================================================= -->
    <!-- FLOATING LIVE CHATBOT WIDGET -->
    <!-- ================================================================= -->
    <div class="fixed bottom-6 right-6 z-50">
        <!-- Floating Toggle Button -->
        <button onclick="toggleChatbot()" class="w-14 h-14 rounded-full bg-brandRed hover:bg-brandRedDark text-slate-900 flex items-center justify-center shadow-2xl glow-red transition transform hover:scale-105">
            <i class="fa-solid fa-comments text-2xl"></i>
        </button>

        <!-- Chat Window -->
        <div id="chatBox" class="hidden absolute bottom-16 right-0 w-[340px] sm:w-[380px] h-[480px] glass-card rounded-2xl shadow-2xl flex flex-col overflow-hidden border-2 border-brandRed/50">
            <!-- Header -->
            <div class="bg-brandNavy p-4 border-b border-brandRed/30 flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <div class="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
                    <div>
                        <h4 class="text-sm font-bold text-slate-900">PamsBeyond Live Chat</h4>
                        <span class="text-[10px] text-slate-500">Human Officers Online</span>
                    </div>
                </div>
                <button onclick="toggleChatbot()" class="text-slate-500 hover:text-slate-900">
                    <i class="fa-solid fa-xmark"></i>
                </button>
            </div>

            <!-- Messages Area -->
            <div id="chatMessages" class="flex-grow p-4 overflow-y-auto space-y-3 text-xs">
            </div>

            <!-- Pre-scripted Quick Options -->
            <div class="px-3 py-2 bg-white/80 border-t border-gray-800 flex gap-1.5 overflow-x-auto text-[10px]">
                <button onclick="switchTab('visa'); toggleChatbot();" class="px-2.5 py-1 rounded-full bg-brandRed/20 text-brandRed font-semibold whitespace-nowrap hover:bg-brandRed hover:text-slate-900 transition">Visa Help</button>
                <button onclick="switchTab('flights'); toggleChatbot();" class="px-2.5 py-1 rounded-full bg-brandRed/20 text-brandRed font-semibold whitespace-nowrap hover:bg-brandRed hover:text-slate-900 transition">Flight Deals</button>
                <button onclick="sendQuickMsg('Talk to Officer')" class="px-2.5 py-1 rounded-full bg-brandRed/20 text-brandRed font-semibold whitespace-nowrap hover:bg-brandRed hover:text-slate-900 transition">Speak to Officer</button>
            </div>

            <!-- Input Bar -->
            <form onsubmit="handleUserChat(event)" class="p-3 bg-brandBlack border-t border-gray-800 flex items-center gap-2">
                <input type="text" id="chatInput" placeholder="Type your inquiry..." class="flex-grow bg-brandGray border border-gray-700 rounded-xl px-3 py-2 text-xs text-slate-900 focus:outline-none focus:border-brandRed">
                <button type="submit" class="p-2 rounded-xl bg-brandRed hover:bg-brandRedDark text-slate-900 text-xs">
                    <i class="fa-solid fa-paper-plane"></i>
                </button>
            </form>
        </div>
    </div>


    <!-- ================================================================= -->
    <!-- MODAL: REQUEST ASSISTANCE / OFFICER FORM -->
    <!-- ================================================================= -->
    <div id="assistanceModal" class="fixed inset-0 z-50 bg-white/80 backdrop-blur-md hidden flex items-center justify-center p-4">
        <div class="glass-card max-w-lg w-full rounded-2xl p-6 sm:p-8 space-y-6 relative border-2 border-brandRed/50">
            <button onclick="closeAssistanceModal()" class="absolute top-4 right-4 text-slate-500 hover:text-slate-900">
                <i class="fa-solid fa-xmark text-xl"></i>
            </button>

            <div>
                <span class="text-brandRed text-xs font-bold uppercase tracking-widest">PamsBeyond Officers</span>
                <h2 class="text-2xl font-bold text-slate-900 mt-1">Feel free to talk to our experienced human officers</h2>
                <p class="text-xs text-slate-500 mt-1">Fill out your details to connect directly with an operational officer.</p>
            </div>

            <form id="assistanceForm" onsubmit="handleAssistanceSubmit(event)" class="space-y-4">
                <div>
                    <label class="block text-xs font-bold text-slate-600 uppercase mb-1">Full Name</label>
                    <input type="text" id="clientName" required placeholder="e.g. John Doe" class="w-full bg-white border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-600 uppercase mb-1">Email Address</label>
                    <input type="email" id="clientEmail" required placeholder="john@example.com" class="w-full bg-white border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-slate-900 focus:border-brandRed focus:outline-none">
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-1">Visa Assistance</label>
                        <input type="text" id="modalVisaType" readonly class="w-full bg-brandGray border border-gray-800 rounded-xl px-3 py-2 text-xs text-slate-600">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-600 uppercase mb-1">Other Services</label>
                        <select id="modalDest" class="w-full bg-brandGray border border-gray-800 rounded-xl px-3 py-2 text-xs text-slate-600">
                            <option value="Flights">Flights</option>
                            <option value="Hotels">Hotels</option>
                        </select>
                    </div>
                </div>

                <div id="freeConsultationNotice" class="p-3 bg-brandRed/10 border border-brandRed/30 rounded-xl text-xs text-brandRed font-semibold flex items-center gap-2">
                    <i class="fa-solid fa-circle-check"></i>
                    <span>Free consultation — no processing fees.</span>
                </div>

                <button type="submit" class="w-full py-3.5 rounded-xl bg-brandRed hover:bg-brandRedDark text-slate-900 font-bold text-sm tracking-wide transition shadow-lg shadow-brandRed/30 flex items-center justify-center gap-2">
                    <i class="fa-solid fa-paper-plane"></i> Connect With Officer Desk
                </button>
            </form>

            <div id="modalSuccess" class="hidden p-4 rounded-xl bg-green-900/40 border border-green-500 text-green-200 text-center text-xs space-y-2">
                <i class="fa-solid fa-circle-check text-2xl text-green-400"></i>
                <p class="font-bold">Request Sent Successfully!</p>
                <p>The officer will be with you shortly.</p>
            </div>
        </div>
    </div>


        <!-- PRIVACY POLICY PAGE -->
        <section id="view-privacy" class="space-y-8 hidden">
            <div class="flex items-center justify-between border-b border-gray-800 pb-4">
                <div>
                    <span class="text-brandRed text-xs font-bold tracking-widest uppercase">Trust & transparency</span>
                    <h1 class="text-3xl font-extrabold text-slate-900">Privacy Policy: Data Security & Document Handling</h1>
                </div>
                <button onclick="switchTab('home')" class="text-xs text-slate-500 hover:text-slate-900 flex items-center gap-1"><i class="fa-solid fa-arrow-left"></i> Back to Main</button>
            </div>
            <div class="glass-card p-6 sm:p-8 rounded-2xl space-y-8 text-sm text-slate-600 leading-relaxed">
                <p><strong class="text-slate-900">PamsBeyond</strong> is committed to protecting your personal data and ensuring transparency regarding how your information is handled.</p>
                <div><h2 class="text-xl font-bold text-slate-900 mb-3">1. Handling of Identity Documents</h2><ul class="list-disc pl-5 space-y-2"><li><strong class="text-slate-900">Secure transmission:</strong> Documents provided for external services handled by our agents are transmitted using appropriate security measures to help protect them during processing.</li><li><strong class="text-slate-900">Limited scope:</strong> Documents are requested only when an external service is handled directly by one of our agents. We use them only for that requested service and do not archive them as part of the free planning tools.</li></ul></div>
                <div><h2 class="text-xl font-bold text-slate-900 mb-3">2. Use of Email and Contact Information</h2><ul class="list-disc pl-5 space-y-2"><li><strong class="text-slate-900">Strictly for updates:</strong> Your email is collected for important updates, status notifications, and essential information about your request or booking.</li><li><strong class="text-slate-900">No spam or third-party sharing:</strong> We do not send spam or sell, rent, or share personal contact details with third parties for marketing or advertising.</li></ul></div>
                <div><h2 class="text-xl font-bold text-slate-900 mb-3">3. Privacy Reminders</h2><ul class="list-disc pl-5 space-y-2"><li>Secure-transmission notices apply only to documents submitted for external services handled directly by our agents.</li><li>Email and checkout notices explain that contact information is used for request updates only.</li><li>When an external service is complete, we aim to remove service documents in line with the applicable policy and legal requirements.</li></ul></div>
            </div>
        </section>

        <!-- TERMS OF SERVICE PAGE -->
        <section id="view-terms" class="space-y-8 hidden">
            <div class="flex items-center justify-between border-b border-gray-800 pb-4">
                <div>
                    <span class="text-brandRed text-xs font-bold tracking-widest uppercase">Legal information</span>
                    <h1 class="text-3xl font-extrabold text-slate-900">PamsBeyond — Terms of Use</h1>
                </div>
                <button onclick="switchTab('home')" class="text-xs text-slate-500 hover:text-slate-900 flex items-center gap-1"><i class="fa-solid fa-arrow-left"></i> Back to Main</button>
            </div>
            <div class="glass-card p-6 sm:p-8 rounded-2xl space-y-8 text-sm text-slate-600 leading-relaxed">
                <div><h2 class="text-xl font-bold text-slate-900 mb-3">1. Nature of Services and Disclaimer</h2><ul class="list-disc pl-5 space-y-2"><li><strong class="text-slate-900">Independent service provider:</strong> PamsBeyond provides AI-powered tools and human-assisted guidance for travel planning and visa application preparation.</li><li><strong class="text-slate-900">Not a government agency:</strong> PamsBeyond is not a government agency, embassy, or official consulate and cannot grant visas. Visa decisions rest solely with the relevant authorities and approval is not guaranteed.</li></ul></div>
                <div><h2 class="text-xl font-bold text-slate-900 mb-3">2. Bookings and Third-Party Suppliers</h2><ul class="list-disc pl-5 space-y-2"><li>PamsBeyond compares flight and hotel prices and may link to third-party suppliers. We do not directly hold travel reservations.</li><li>Bookings are subject to supplier pricing, cancellation policies, and terms. PamsBeyond is not liable for supplier failures, delays, cancellations, or booking errors.</li></ul></div>
                <div><h2 class="text-xl font-bold text-slate-900 mb-3">3. User Responsibilities</h2><ul class="list-disc pl-5 space-y-2"><li>Users must provide accurate, truthful, and current information.</li><li>Users are responsible for passport validity, vaccinations, transit visas, and other travel prerequisites.</li><li>Users must carefully review completed applications. If an error is identified on our part, PamsBeyond will work to correct it.</li></ul></div>
                <div><h2 class="text-xl font-bold text-slate-900 mb-3">4. Fees, Payments, and Refund Policy</h2><ul class="list-disc pl-5 space-y-2"><li>PamsBeyond service fees cover preparation and filling services. Government fees, embassy charges, and third-party travel costs are separate.</li><li>Service fees are generally non-refundable. Visa rejection does not automatically qualify for a refund.</li><li>Fees for external agent services, government charges, and third-party travel costs are separate and are disclosed before the service begins.</li></ul></div>
                <div><h2 class="text-xl font-bold text-slate-900 mb-3">5. Limitation of Liability</h2><p>PamsBeyond is not liable for financial losses, missed flights, denied boarding, or entry refusals caused by visa processing delays, embassy decisions, or inaccurate user-provided information. Liability is limited to the scope of application preparation and facilitation services.</p></div>
            </div>
        </section>

    <!-- FOOTER -->
    <footer class="relative z-10 glass-card border-t border-brandRed/20 mt-12 py-6 px-4 text-center text-xs text-slate-500">
        <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
            <div class="flex items-center gap-2">
                <span class="font-black text-slate-900 uppercase tracking-wider">pams<span class="text-brandRed">beyond</span></span>
                <span>&copy; <span id="year"></span>. All rights reserved.</span>
            </div>
            <div class="flex items-center gap-4 text-slate-500">
                <a href="#" onclick="switchTab('privacy'); return false;" class="hover:text-brandRed">Privacy Policy</a>
                <a href="#" onclick="switchTab('terms'); return false;" class="hover:text-brandRed">Terms of Service</a>
                <a href="#" onclick="openAssistanceModal('General Consultation', 'Flights'); return false;" class="hover:text-brandRed">Officer Desk</a>
            </div>
        </div>
    </footer>


    <!-- ================================================================= -->
    <!-- JAVASCRIPT LOGIC & ANIMATIONS -->
    <!-- ================================================================= -->
    <script>
        document.getElementById('year').textContent = new Date().getFullYear();

        // WORLD COUNTRIES
        const globalCountries = [
            "Afghanistan", "Albania", "Algeria", "Argentina", "Australia", "Austria", "Bahrain", 
            "Bangladesh", "Belgium", "Brazil", "Canada", "China", "Colombia", "Czech Republic", 
            "Denmark", "Egypt", "Finland", "France", "Germany", "Greece", "Hong Kong", "Hungary", 
            "India", "Indonesia", "Iran", "Iraq", "Ireland", "Italy", "Japan", "Jordan", 
            "Kuwait", "Lebanon", "Malaysia", "Mexico", "Morocco", "Netherlands", "New Zealand", 
            "Nigeria", "Norway", "Oman", "Pakistan", "Philippines", "Poland", "Portugal", 
            "Qatar", "Romania", "Saudi Arabia", "Singapore", "South Africa", "Spain", "Sweden", 
            "Switzerland", "Thailand", "Turkey", "UAE", "UK", "USA", "Vietnam"
        ];

        // GLOBAL CITIES (For Flight Search Option)
        const globalCities = [
            "Cairo (CAI) - Egypt", "Toronto (YYZ) - Canada", "Dubai (DXB) - UAE", 
            "London (LHR) - UK", "New York (JFK) - USA", "Paris (CDG) - France", 
            "Istanbul (IST) - Turkey", "Riyadh (RUH) - Saudi Arabia", "Sydney (SYD) - Australia", 
            "Tokyo (HND) - Japan", "Rome (FCO) - Italy", "Frankfurt (FRA) - Germany", 
            "Doha (DOH) - Qatar", "Bangkok (BKK) - Thailand", "Kuala Lumpur (KUL) - Malaysia"
        ];

        window.addEventListener('DOMContentLoaded', () => {
            // Populate Countries
            ['visaOrigin', 'visaDest', 'plannerOrigin', 'plannerDestination'].forEach(id => {
                const el = document.getElementById(id);
                globalCountries.forEach(c => {
                    const opt = document.createElement('option');
                    opt.value = c; opt.textContent = c;
                    el.appendChild(opt);
                });
            });

            // Populate Cities
            ['flightOriginCity', 'flightDestCity', 'hotelLocation'].forEach(id => {
                const el = document.getElementById(id);
                globalCities.forEach(city => {
                    const opt = document.createElement('option');
                    opt.value = city; opt.textContent = city;
                    el.appendChild(opt);
                });
            });

            const today = new Date().toISOString().split('T')[0];
            const future = new Date(Date.now() + 86400000 * 7).toISOString().split('T')[0];
            ['flightDepDate', 'hotelCheckIn'].forEach(id => { if (document.getElementById(id)) document.getElementById(id).value = today; });
            ['flightRetDate', 'hotelCheckOut'].forEach(id => { if (document.getElementById(id)) document.getElementById(id).value = future; });

            initMap();
            initCanvas();
        });

        function switchTab(tabId) {
            ['home', 'planner', 'visa', 'flights', 'hotels', 'help', 'privacy', 'terms'].forEach(id => {
                document.getElementById('view-' + id).classList.add('hidden');
            });
            document.getElementById('view-' + tabId).classList.remove('hidden');

            if(tabId === 'help' && leafletMap) {
                setTimeout(() => leafletMap.invalidateSize(), 300);
            }
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        function generateTravelPlan() {
            const origin = document.getElementById('plannerOrigin').value;
            const destination = document.getElementById('plannerDestination').value;
            const period = document.getElementById('plannerPeriod').value.trim();
            const budget = Number(document.getElementById('plannerBudget').value);
            const results = document.getElementById('plannerResults');
            if (!origin || !destination || !period || !budget) return;
            const budgetNote = budget < 800 ? 'Focus on flexible dates, public transport, and locally owned stays.' : budget < 1800 ? 'Balance comfortable stays with one or two priority experiences.' : 'Allow room for upgraded connections, central stays, and guided experiences.';
            const flightLink = `https://www.google.com/travel/flights?q=Flights%20from%20${encodeURIComponent(origin)}%20to%20${encodeURIComponent(destination)}`;
            const hotelLink = `https://www.booking.com/searchresults.html?ss=${encodeURIComponent(destination)}`;
            const placesLink = `https://www.google.com/maps/search/hidden+gems+in+${encodeURIComponent(destination)}`;
            results.innerHTML = `<div><span class="text-purple-600 text-xs font-bold uppercase tracking-widest">Your Pams travel plan</span><h2 class="text-2xl font-black text-slate-900 mt-1">${origin} to ${destination}</h2><p class="text-slate-600 text-sm mt-1">${period} · Budget: $${budget.toLocaleString()}</p></div><div class="grid md:grid-cols-2 gap-3"><div class="rounded-2xl bg-blue-50 border border-blue-200 p-4"><b class="text-slate-900">Flights</b><p class="text-slate-600 text-sm mt-1">Compare flexible connections and choose the route that preserves the largest share of your budget.</p><a class="text-brandRed text-sm font-bold" target="_blank" href="${flightLink}">Compare flights →</a></div><div class="rounded-2xl bg-purple-50 border border-purple-200 p-4"><b class="text-slate-900">Hotels</b><p class="text-slate-600 text-sm mt-1">Start with well-reviewed stays near transport, then filter by your budget and dates.</p><a class="text-brandRed text-sm font-bold" target="_blank" href="${hotelLink}">Compare stays →</a></div><div class="rounded-2xl bg-red-50 border border-red-200 p-4"><b class="text-slate-900">Places to explore</b><p class="text-slate-600 text-sm mt-1">Mix one landmark, one local neighbourhood, and one hidden place each day.</p><a class="text-brandRed text-sm font-bold" target="_blank" href="${placesLink}">Explore places →</a></div><div class="rounded-2xl bg-slate-50 border border-slate-200 p-4"><b class="text-slate-900">Budget guidance</b><p class="text-slate-600 text-sm mt-1">${budgetNote}</p><p class="text-xs text-slate-500 mt-2">This is a planning starting point. Prices and availability are supplied by the linked providers.</p></div></div>`;
            results.classList.remove('hidden');
            results.scrollIntoView({ behavior: 'smooth' });
        }

        // VISA SEARCH LOGIC
        function runVisaSearch() {
            const origin = document.getElementById('visaOrigin').value;
            const dest = document.getElementById('visaDest').value;
            const passType = document.getElementById('passportType').value;
            const vType = document.getElementById('visaType').value;

            if(!origin || !dest) return;

            // Send the client's visa search details to PamsBeyond through FormSubmit.
            fetch('https://formsubmit.co/ajax/pamsbeyond@gmail.com', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    client_nationality: origin,
                    destination: dest,
                    visa_type: vType,
                    passport_type: passType,
                    _subject: `PamsBeyond Visa Search: ${origin} to ${dest}`,
                    _captcha: 'true',
                    _template: 'table'
                })
            }).catch(error => {
                console.error('Visa request notification failed:', error);
            });

            const resultsDiv = document.getElementById('visaResults');
            resultsDiv.classList.remove('hidden');

            document.getElementById('resultTitle').textContent = `${origin} ➔ ${dest} (${vType})`;
            
            let baseFee = 85;
            if (['USA', 'Canada', 'UK', 'Australia'].includes(dest)) baseFee = 150;
            if (['UAE', 'Qatar', 'Saudi Arabia'].includes(dest)) baseFee = 95;
            document.getElementById('resultFee').textContent = `$${baseFee} USD Approx Govt Processing Fee`;

            const docs = [
                `Valid ${passType} (Minimum 6 months validity from departure date)`,
                `Biometric passport photos meeting ${dest} embassy guidelines`,
                `Bank statements (Last 3 to 6 months)`,
                `Hotel accommodation booking / proof of stay`,
                `Round-trip flight ticket reservation`,
                `Official statement of purpose for ${vType}`
            ];
            document.getElementById('docList').innerHTML = docs.map(d => `<li class="flex items-start gap-2"><i class="fa-solid fa-circle-check text-green-500 mt-1"></i> <span>${d}</span></li>`).join('');

            const terms = [
                `Maximum stay: Up to 90 days per entry`,
                `Overstaying incurs daily legal fines and potential travel restrictions`,
                `Mandatory travel insurance coverage required`,
                `Biometrics appointment required at designated center`
            ];
            document.getElementById('termsList').innerHTML = terms.map(t => `<li class="flex items-start gap-2"><i class="fa-solid fa-circle-exclamation text-brandRed mt-1"></i> <span>${t}</span></li>`).join('');

            document.getElementById('offerText').textContent = `Talk to an experienced agent live about your travel needs.`;

            resultsDiv.scrollIntoView({ behavior: 'smooth' });
        }

        function triggerHandledAssistance() {
            const origin = document.getElementById('visaOrigin').value || "Egypt";
            const dest = document.getElementById('visaDest').value || "Canada";
            const vType = document.getElementById('visaType').value || "Tourist Visa";
            openAssistanceModal(vType, dest);
        }

        // FLIGHT SEARCH LOGIC
        function toggleReturnDate(show) {
            const container = document.getElementById('returnDateContainer');
            if (show) container.classList.remove('opacity-40', 'pointer-events-none');
            else container.classList.add('opacity-40', 'pointer-events-none');
        }

        function runFlightSearch() {
            const origin = document.getElementById('flightOriginCity').value || "Cairo (CAI) - Egypt";
            const dest = document.getElementById('flightDestCity').value || "Toronto (YYZ) - Canada";

            const resultsContainer = document.getElementById('flightResults');
            const flightList = document.getElementById('flightList');
            resultsContainer.classList.remove('hidden');

            const airlines = [
                { name: "Emirates", logo: "fa-plane-up", price: "$620", stops: "1 Stop", time: "14h 20m" },
                { name: "Qatar Airways", logo: "fa-plane", price: "$645", stops: "1 Stop", time: "15h 05m" },
                { name: "Turkish Airlines", logo: "fa-plane-departure", price: "$590", stops: "1 Stop", time: "13h 45m" },
                { name: "Lufthansa / Air Canada", logo: "fa-plane", price: "$710", stops: "Direct Flight", time: "11h 30m" }
            ];

            flightList.innerHTML = airlines.map(a => `
                <div class="glass-card p-5 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-4 border-l-4 border-l-brandRed">
                    <div class="flex items-center gap-4">
                        <div class="w-12 h-12 rounded-xl bg-brandNavy border border-brandRed/40 flex items-center justify-center text-brandRed text-xl">
                            <i class="fa-solid ${a.logo}"></i>
                        </div>
                        <div>
                            <div class="flex items-center gap-2">
                                <h4 class="text-base font-bold text-slate-900">${a.name}</h4>
                                <span class="bg-brandRed/20 text-brandRed text-[10px] font-bold px-2 py-0.5 rounded">${a.stops}</span>
                            </div>
                            <p class="text-xs text-slate-500 mt-1">${origin} ➔ ${dest} • Duration: ${a.time}</p>
                        </div>
                    </div>
                    <div class="flex items-center gap-4 w-full md:w-auto justify-between md:justify-end border-t md:border-t-0 border-gray-800 pt-3 md:pt-0">
                        <div class="text-left md:text-right">
                            <span class="text-[10px] text-slate-500 uppercase block">Best Available Rate</span>
                            <span class="text-2xl font-black text-brandRed">${a.price}</span>
                        </div>
                        <a href="https://www.skyscanner.com" target="_blank" class="px-5 py-2.5 rounded-xl bg-brandRed hover:bg-brandRedDark text-slate-900 font-bold text-xs transition shadow-md flex items-center gap-1">
                            Book Deal <i class="fa-solid fa-arrow-up-right-from-square text-[10px]"></i>
                        </a>
                    </div>
                </div>
            `).join('');

            resultsContainer.scrollIntoView({ behavior: 'smooth' });
        }

        // ACCOMMODATION SEARCH
        const sampleHotels = [
            { name: "The Ritz Luxury Resort", rating: "4.9 ★", price: 340, img: "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=600&q=80", tag: "Luxury Choice" },
            { name: "Grand Horizon Hotel & Spa", rating: "4.7 ★", price: 180, img: "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=600&q=80", tag: "Top Rated" },
            { name: "Urban City Boutique Stay", rating: "4.5 ★", price: 95, img: "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=600&q=80", tag: "Best Value" },
            { name: "Palace Waterfront Suites", rating: "4.8 ★", price: 520, img: "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=600&q=80", tag: "Exclusive" }
        ];

        function runHotelSearch() {
            document.getElementById('hotelResults').classList.remove('hidden');
            filterHotels();
            document.getElementById('hotelResults').scrollIntoView({ behavior: 'smooth' });
        }

        function filterHotels() {
            const maxPrice = parseInt(document.getElementById('priceRange').value);
            document.getElementById('priceRangeValue').textContent = `Up to $${maxPrice}/night`;

            const filtered = sampleHotels.filter(h => h.price <= maxPrice);
            document.getElementById('hotelCount').textContent = filtered.length;

            const list = document.getElementById('hotelList');
            if (filtered.length === 0) {
                list.innerHTML = `<div class="col-span-3 text-center py-8 text-slate-500">No accommodations found under $${maxPrice}. Adjust the filter.</div>`;
                return;
            }

            list.innerHTML = filtered.map(h => `
                <div class="glass-card rounded-2xl overflow-hidden glass-card-hover flex flex-col justify-between">
                    <div>
                        <div class="relative h-48 overflow-hidden">
                            <img src="${h.img}" alt="${h.name}" class="w-full h-full object-cover">
                            <span class="absolute top-3 left-3 bg-white border border-brandRed/40 text-brandRed text-[10px] font-extrabold px-2 py-1 rounded-md uppercase tracking-wider">${h.tag}</span>
                            <span class="absolute bottom-3 right-3 bg-white text-yellow-400 font-bold text-xs px-2 py-1 rounded-md">${h.rating}</span>
                        </div>
                        <div class="p-5">
                            <h4 class="text-lg font-bold text-slate-900">${h.name}</h4>
                            <p class="text-xs text-slate-500 mt-1"><i class="fa-solid fa-wifi text-brandRed"></i> Free High-Speed WiFi • Pool • Airport Transfer</p>
                        </div>
                    </div>
                    <div class="p-5 pt-0 flex items-center justify-between border-t border-gray-800/80 mt-2">
                        <div>
                            <span class="text-[10px] text-slate-500 block">Nightly Rate</span>
                            <span class="text-xl font-black text-brandRed">$${h.price} <span class="text-xs text-slate-500 font-normal">/ night</span></span>
                        </div>
                        <a href="https://www.booking.com" target="_blank" class="px-4 py-2 rounded-xl bg-brandRed hover:bg-brandRedDark text-slate-900 text-xs font-bold transition">
                            Reserve Room
                        </a>
                    </div>
                </div>
            `).join('');
        }

        // MAP LOGIC
        let leafletMap = null;
        let markers = [];

        function initMap() {
            leafletMap = L.map('map').setView([30.0444, 31.2357], 12);
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; OpenStreetMap',
                maxZoom: 19
            }).addTo(leafletMap);
        }

        function runGroundSearch() {
            const location = document.getElementById('groundLocation').value || "Cairo";
            const service = document.getElementById('groundService').value;

            const providerList = document.getElementById('providerList');
            const providers = [
                { name: `PamsBeyond Airport Transport`, phone: "+1 (800) 555-PAMS", rate: "$25 Fixed Rate" },
                { name: `VIP Private Chauffeurs`, phone: "+1 (800) 555-0192", rate: "Verified Operator" },
                { name: `Local Assistance Officer Desk`, phone: "+1 (800) 555-DESK", rate: "24/7 Available" }
            ];

            providerList.innerHTML = providers.map(p => `
                <div class="p-3 rounded-xl bg-white/80 border border-brandRed/30 space-y-1">
                    <div class="flex items-center justify-between font-bold text-slate-900">
                        <span>${p.name}</span>
                        <span class="text-brandRed">${p.rate}</span>
                    </div>
                    <p class="text-slate-500 text-[11px]"><i class="fa-solid fa-phone text-brandRed"></i> ${p.phone}</p>
                    <button onclick="openAssistanceModal('${service}', '${location}')" class="w-full mt-2 py-1.5 rounded bg-brandRed/20 hover:bg-brandRed text-brandRed hover:text-slate-900 font-bold text-[10px] transition">
                        Feel free to talk to our experienced human officers
                    </button>
                </div>
            `).join('');

            leafletMap.setView([30.0444 + (Math.random()-0.5)*0.04, 31.2357 + (Math.random()-0.5)*0.04], 13);
            markers.forEach(m => leafletMap.removeLayer(m));
            markers = [];

            const marker = L.marker([30.0444, 31.2357]).addTo(leafletMap)
                .bindPopup(`<b>PamsBeyond Local Service Hub</b><br>${service} in ${location}`).openPopup();
            markers.push(marker);
        }

        // CHATBOT FUNCTIONS
        function toggleChatbot() {
            const chatBox = document.getElementById('chatBox');
            chatBox.classList.toggle('hidden');
        }

        function sendQuickMsg(text) {
            appendUserMsg(text);
            setTimeout(() => {
                appendOfficerMsg(`Thank you for inquiring about "${text}". An experienced officer is ready to help! You can click "Live Chat" or fill out our request form.`);
            }, 800);
        }

        function handleUserChat(e) {
            e.preventDefault();
            const input = document.getElementById('chatInput');
            const val = input.value.trim();
            if(!val) return;
            appendUserMsg(val);
            input.value = '';

            setTimeout(() => {
                appendOfficerMsg("Message received! Our human officers are processing your overseas travel request. Someone will reply directly or you can leave your email.");
            }, 1000);
        }

        function appendUserMsg(txt) {
            const chatMessages = document.getElementById('chatMessages');
            const msg = document.createElement('div');
            msg.className = "bg-brandRed text-slate-900 p-2.5 rounded-xl ml-auto max-w-[80%] text-right font-medium";
            msg.textContent = txt;
            chatMessages.appendChild(msg);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function appendOfficerMsg(txt) {
            const chatMessages = document.getElementById('chatMessages');
            const msg = document.createElement('div');
            msg.className = "bg-brandGray border border-gray-800 p-2.5 rounded-xl mr-auto max-w-[85%] text-gray-200";
            msg.textContent = txt;
            chatMessages.appendChild(msg);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        // MODAL FUNCTIONS
        function openAssistanceModal(visaType = "Tourist Visa", dest = "Flights") {
            document.getElementById('modalVisaType').value = visaType;
            const serviceSelect = document.getElementById('modalDest');
            serviceSelect.value = ['Flights', 'Hotels'].includes(dest) ? dest : 'Flights';
            document.getElementById('assistanceModal').classList.remove('hidden');
            document.getElementById('modalSuccess').classList.add('hidden');
            document.getElementById('assistanceForm').classList.remove('hidden');
        }

        function closeAssistanceModal() {
            document.getElementById('assistanceModal').classList.add('hidden');
        }

        async function handleAssistanceSubmit(e) {
            e.preventDefault();

            const name = document.getElementById('clientName').value.trim();
            const email = document.getElementById('clientEmail').value.trim();
            const visaType = document.getElementById('modalVisaType').value;
            const dest = document.getElementById('modalDest').value;
            const submitButton = document.querySelector('#assistanceForm button[type="submit"]');

            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Sending...';

            const formData = {
                name,
                email,
                visa_assistance: visaType,
                other_service: dest,
                _subject: `PamsBeyond Officer Request: ${visaType} - ${dest}`,
                _captcha: 'true',
                _template: 'table'
            };

            try {
                const response = await fetch('https://formsubmit.co/ajax/pamsbeyond@gmail.com', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                if (!response.ok) {
                    throw new Error('Form submission failed');
                }

                document.getElementById('assistanceForm').classList.add('hidden');
                document.getElementById('modalSuccess').classList.remove('hidden');
            } catch (error) {
                submitButton.disabled = false;
                submitButton.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Connect With Officer Desk';
                alert('Sorry, your request could not be sent. Please try again or email us directly.');
            }
        }

        // FLYING PLANES BACKGROUND CANVAS
        function initCanvas() {
            const canvas = document.getElementById('bgCanvas');
            const ctx = canvas.getContext('2d');

            function resize() {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            }
            window.addEventListener('resize', resize);
            resize();

            const planes = Array.from({ length: 8 }, () => ({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                speed: 1 + Math.random() * 1.5,
                angle: Math.random() * Math.PI * 2,
                size: 10 + Math.random() * 8,
                trail: []
            }));

            function drawPlane(x, y, angle, size) {
                ctx.save();
                ctx.translate(x, y);
                ctx.rotate(angle);
                
                ctx.beginPath();
                ctx.moveTo(size * 1.5, 0);
                ctx.lineTo(-size, -size * 0.7);
                ctx.lineTo(-size * 0.4, 0);
                ctx.lineTo(-size, size * 0.7);
                ctx.closePath();
                ctx.fillStyle = '#e60023';
                ctx.fill();

                ctx.restore();
            }

            function animate() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                ctx.strokeStyle = 'rgba(230, 0, 35, 0.03)';
                ctx.lineWidth = 1;
                for (let x = 0; x < canvas.width; x += 60) {
                    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
                }

                planes.forEach(p => {
                    p.x += Math.cos(p.angle) * p.speed;
                    p.y += Math.sin(p.angle) * p.speed;

                    p.trail.push({ x: p.x, y: p.y });
                    if (p.trail.length > 20) p.trail.shift();

                    if (p.trail.length > 1) {
                        ctx.beginPath();
                        ctx.moveTo(p.trail[0].x, p.trail[0].y);
                        for (let i = 1; i < p.trail.length; i++) {
                            ctx.lineTo(p.trail[i].x, p.trail[i].y);
                        }
                        ctx.strokeStyle = 'rgba(230, 0, 35, 0.25)';
                        ctx.lineWidth = 1.5;
                        ctx.stroke();
                    }

                    if (p.x < -50) p.x = canvas.width + 50;
                    if (p.x > canvas.width + 50) p.x = -50;
                    if (p.y < -50) p.y = canvas.height + 50;
                    if (p.y > canvas.height + 50) p.y = -50;

                    drawPlane(p.x, p.y, p.angle, p.size);
                });

                requestAnimationFrame(animate);
            }

            animate();
        }
    </script>
</body>
</html>
"""

# Embed the uploaded PamsBeyond logo directly so the app works as a standalone app.py.
# Embed a standalone PamsBeyond logo so the app works without extra assets.
logo_data = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA5MDAgMzAwIj4KPHJlY3Qgd2lkdGg9IjkwMCIgaGVpZ2h0PSIzMDAiIHJ4PSIyOCIgZmlsbD0iIzA4MDgwYSIvPgo8cGF0aCBkPSJNOTAgMjE4IEMxNjUgODAgMjQ1IDgwIDMyMCAxNjAgQzM4NSAyMjggNDcwIDIyMCA1NDAgMTMwIiBmaWxsPSJub25lIiBzdHJva2U9IiNlNjAwMjMiIHN0cm9rZS13aWR0aD0iMTIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8cGF0aCBkPSJNNDkyIDExNiBsMTUwIC01NSAtNTQgNTIgODQgMTggLTEwNCA5IC0zNiA1MCA0IC00OCAtNzAgLTI2IDc4IDR6IiBmaWxsPSIjZmZmIi8+Cjx0ZXh0IHg9IjcwIiB5PSIxNjUiIGZvbnQtZmFtaWx5PSJBcmlhbCxIZWx2ZXRpY2Esc2Fucy1zZXJpZiIgZm9udC1zaXplPSI4MiIgZm9udC13ZWlnaHQ9IjgwMCIgZmlsbD0iI2U2MDAyMyI+UGFtczwvdGV4dD4KPHRleHQgeD0iMzE1IiB5PSIxNjUiIGZvbnQtZmFtaWx5PSJBcmlhbCxIZWx2ZXRpY2Esc2Fucy1zZXJpZiIgZm9udC1zaXplPSI4MiIgZm9udC13ZWlnaHQ9IjgwMCIgZmlsbD0iI2ZmZiI+YmV5b25kPC90ZXh0Pgo8dGV4dCB4PSI3NCIgeT0iMjQyIiBmb250LWZhbWlseT0iQXJpYWwsSGVsdmV0aWNhLHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMzAiIGZvbnQtd2VpZ2h0PSI3MDAiIGxldHRlci1zcGFjaW5nPSI4IiBmaWxsPSIjZTYwMDIzIj5HRVQgQkVZT05EPC90ZXh0Pgo8L3N2Zz4="

# Render Embedded Web App Component
components.html(html_code.replace("{{LOGO_DATA}}", logo_data), height=950, scrolling=True)