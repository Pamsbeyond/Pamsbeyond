import streamlit as st
import streamlit.components.v1 as components

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
html_code = """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PamsBeyond - Visa & Travel Global Services</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
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
                        brandRed: '#e60023',
                        brandRedDark: '#b3001b',
                        brandNavy: '#0a1128',
                        brandBlack: '#08080a',
                        brandGray: '#121318',
                        brandCard: '#1a1c23'
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
        ::-webkit-scrollbar-track { background: #08080a; }
        ::-webkit-scrollbar-thumb { background: #e60023; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #b3001b; }
        
        .glass-card {
            background: rgba(26, 28, 35, 0.88);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(230, 0, 35, 0.2);
        }
        .glass-card-hover {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .glass-card-hover:hover {
            transform: translateY(-4px);
            border-color: rgba(230, 0, 35, 0.6);
            box-shadow: 0 10px 30px -10px rgba(230, 0, 35, 0.3);
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
            mix-blend-mode: multiply;
            filter: contrast(120%) brightness(110%);
        }
    </style>
</head>
<body class="bg-brandBlack text-gray-100 font-sans min-h-screen flex flex-col relative overflow-x-hidden">

    <!-- LIVE ANIMATED CANVAS BACKGROUND (Flying Planes) -->
    <canvas id="bgCanvas"></canvas>

    <!-- TOP HEADER / NAVIGATION -->
    <header class="sticky top-0 z-40 glass-card border-b border-brandRed/20 px-4 lg:px-8 py-3">
        <div class="max-w-7xl mx-auto flex items-center justify-between">
            <!-- Brand Logo & Name -->
            <a href="#" onclick="switchTab('home')" class="flex items-center gap-3 group">
                <div class="relative w-12 h-12 flex items-center justify-center bg-transparent rounded-lg overflow-hidden logo-container">
                    <i class="fa-solid fa-plane text-brandRed text-2xl transform -rotate-45 transition group-hover:scale-110"></i>
                </div>
                <div>
                    <span class="text-2xl font-black tracking-tight text-white uppercase">pams<span class="text-brandRed">beyond</span></span>
                    <p class="text-[10px] text-gray-400 tracking-widest uppercase font-semibold">Visa & Travel Global Services</p>
                </div>
            </a>

            <!-- Navigation Links -->
            <nav class="hidden md:flex items-center gap-1 bg-brandBlack/60 p-1.5 rounded-full border border-gray-800">
                <button onclick="switchTab('visa')" class="nav-btn px-4 py-2 rounded-full text-xs font-semibold text-gray-300 hover:text-white hover:bg-brandRed/20 transition flex items-center gap-2">
                    <i class="fa-solid fa-passport text-brandRed"></i> Visas
                </button>
                <button onclick="switchTab('flights')" class="nav-btn px-4 py-2 rounded-full text-xs font-semibold text-gray-300 hover:text-white hover:bg-brandRed/20 transition flex items-center gap-2">
                    <i class="fa-solid fa-plane-departure text-brandRed"></i> Flights
                </button>
                <button onclick="switchTab('hotels')" class="nav-btn px-4 py-2 rounded-full text-xs font-semibold text-gray-300 hover:text-white hover:bg-brandRed/20 transition flex items-center gap-2">
                    <i class="fa-solid fa-hotel text-brandRed"></i> Stays
                </button>
                <button onclick="switchTab('help')" class="nav-btn px-4 py-2 rounded-full text-xs font-semibold text-gray-300 hover:text-white hover:bg-brandRed/20 transition flex items-center gap-2">
                    <i class="fa-solid fa-map-location-dot text-brandRed"></i> Local Assistance
                </button>
            </nav>

            <!-- Quick Live Chat Button -->
            <button onclick="toggleChatbot()" class="px-5 py-2.5 rounded-full bg-brandRed hover:bg-brandRedDark text-white font-bold text-xs tracking-wider transition shadow-lg shadow-brandRed/30 flex items-center gap-2">
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
                <h1 class="text-3xl sm:text-5xl font-extrabold text-white tracking-tight leading-tight">
                    Tell us where the next overseas plans
                </h1>
                <p class="text-gray-400 text-sm sm:text-base">
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
                        <div class="w-12 h-12 rounded-xl bg-brandRed/20 border border-brandRed/40 flex items-center justify-center text-brandRed text-2xl mb-4 group-hover:bg-brandRed group-hover:text-white transition">
                            <i class="fa-solid fa-passport"></i>
                        </div>
                        <span class="text-xs font-bold text-brandRed uppercase tracking-widest">What we can do for you</span>
                        <h2 class="text-2xl font-bold text-white mt-1 group-hover:text-brandRed transition">Planning to travel to get yourself overseas?</h2>
                        <p class="text-gray-400 text-xs sm:text-sm mt-2">Instant search for worldwide visa requirements, documentation, exact official fees, and direct officer support.</p>
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
                        <div class="w-12 h-12 rounded-xl bg-brandRed/20 border border-brandRed/40 flex items-center justify-center text-brandRed text-2xl mb-4 group-hover:bg-brandRed group-hover:text-white transition">
                            <i class="fa-solid fa-plane-departure"></i>
                        </div>
                        <span class="text-xs font-bold text-brandRed uppercase tracking-widest">What we can do for you</span>
                        <h2 class="text-2xl font-bold text-white mt-1 group-hover:text-brandRed transition">Need a flight booking?</h2>
                        <p class="text-gray-400 text-xs sm:text-sm mt-2">Scans global airlines & booking platforms by city to display live lowest rates and best connection routes.</p>
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
                        <div class="w-12 h-12 rounded-xl bg-brandRed/20 border border-brandRed/40 flex items-center justify-center text-brandRed text-2xl mb-4 group-hover:bg-brandRed group-hover:text-white transition">
                            <i class="fa-solid fa-hotel"></i>
                        </div>
                        <span class="text-xs font-bold text-brandRed uppercase tracking-widest">What we can do for you</span>
                        <h2 class="text-2xl font-bold text-white mt-1 group-hover:text-brandRed transition">Any accommodation?</h2>
                        <p class="text-gray-400 text-xs sm:text-sm mt-2">Discover high-rated properties globally with interactive price filters and luxury or budget recommendations.</p>
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
                        <div class="w-12 h-12 rounded-xl bg-brandRed/20 border border-brandRed/40 flex items-center justify-center text-brandRed text-2xl mb-4 group-hover:bg-brandRed group-hover:text-white transition">
                            <i class="fa-solid fa-map-location-dot"></i>
                        </div>
                        <span class="text-xs font-bold text-brandRed uppercase tracking-widest">What we can do for you</span>
                        <h2 class="text-2xl font-bold text-white mt-1 group-hover:text-brandRed transition">You are already there and need any help?</h2>
                        <p class="text-gray-400 text-xs sm:text-sm mt-2">Airport pickup, taxis, local transit, top nearby restaurants and hotels powered by live map discovery.</p>
                    </div>
                    <div class="mt-6 flex items-center text-xs font-bold text-brandRed group-hover:translate-x-2 transition">
                        Locate Nearby Services <i class="fa-solid fa-arrow-right ml-2"></i>
                    </div>
                </div>

            </div>
        </section>


        <!-- ================================================================= -->
        <!-- VIEW 1: VISA REQUIREMENTS -->
        <!-- ================================================================= -->
        <section id="view-visa" class="space-y-8 hidden">
            <div class="flex items-center justify-between border-b border-gray-800 pb-4">
                <div>
                    <span class="text-brandRed text-xs font-bold tracking-widest uppercase">What we can do for you</span>
                    <h1 class="text-3xl font-extrabold text-white">Global Visa & Requirements Search</h1>
                </div>
                <button onclick="switchTab('home')" class="text-xs text-gray-400 hover:text-white flex items-center gap-1">
                    <i class="fa-solid fa-arrow-left"></i> Back to Main
                </button>
            </div>

            <div class="glass-card p-6 sm:p-8 rounded-2xl space-y-6">
                <form id="visaForm" onsubmit="event.preventDefault(); runVisaSearch();" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div>
                        <label class="block text-xs font-bold text-gray-300 uppercase mb-2"><i class="fa-solid fa-flag text-brandRed"></i> 1. Origin Country</label>
                        <select id="visaOrigin" required class="w-full bg-brandBlack/80 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white focus:border-brandRed focus:outline-none">
                            <option value="">Select Origin...</option>
                        </select>
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-gray-300 uppercase mb-2"><i class="fa-solid fa-location-dot text-brandRed"></i> 2. Destination</label>
                        <select id="visaDest" required class="w-full bg-brandBlack/80 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white focus:border-brandRed focus:outline-none">
                            <option value="">Select Destination...</option>
                        </select>
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-gray-300 uppercase mb-2"><i class="fa-solid fa-id-card text-brandRed"></i> 3. Passport Type</label>
                        <select id="passportType" required class="w-full bg-brandBlack/80 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white focus:border-brandRed focus:outline-none">
                            <option value="Ordinary Passport">Ordinary (Standard Tourist)</option>
                            <option value="Diplomatic Passport">Diplomatic Passport</option>
                            <option value="Official / Service Passport">Official / Service</option>
                            <option value="Refugee Travel Document">Refugee / Travel Document</option>
                        </select>
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-gray-300 uppercase mb-2"><i class="fa-solid fa-briefcase text-brandRed"></i> 4. Visa Type</label>
                        <select id="visaType" required class="w-full bg-brandBlack/80 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white focus:border-brandRed focus:outline-none">
                            <option value="Tourist / Visitor Visa">Tourist / Visitor Visa</option>
                            <option value="Business Visa">Business Visa</option>
                            <option value="Student / Study Permit">Student / Study Permit</option>
                            <option value="Work / Employment Visa">Work / Employment Visa</option>
                            <option value="Transit Visa">Transit Visa</option>
                            <option value="Permanent Residence">Permanent Residence</option>
                        </select>
                    </div>

                    <div class="md:col-span-2 lg:col-span-4 mt-2">
                        <button type="submit" class="w-full py-4 rounded-xl bg-brandRed hover:bg-brandRedDark text-white font-bold text-sm tracking-wide transition shadow-lg shadow-brandRed/30 flex items-center justify-center gap-2">
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
                            <h2 id="resultTitle" class="text-2xl font-bold text-white">Egypt ➔ Canada (Visitor Visa)</h2>
                        </div>
                        <div class="text-right">
                            <span class="text-xs text-gray-400 block">Official Govt Fee</span>
                            <span id="resultFee" class="text-2xl font-black text-brandRed">$100 USD + $85 Biometrics</span>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <h3 class="text-sm font-bold text-white uppercase mb-3 flex items-center gap-2">
                                <i class="fa-solid fa-file-shield text-brandRed"></i> Required Documents Checklist
                            </h3>
                            <ul id="docList" class="space-y-2 text-xs sm:text-sm text-gray-300"></ul>
                        </div>
                        <div>
                            <h3 class="text-sm font-bold text-white uppercase mb-3 flex items-center gap-2">
                                <i class="fa-solid fa-gavel text-brandRed"></i> Key Terms & Entry Conditions
                            </h3>
                            <ul id="termsList" class="space-y-2 text-xs sm:text-sm text-gray-300"></ul>
                        </div>
                    </div>

                    <!-- HANDLING FOR YOU BOX -->
                    <div class="mt-6 p-6 rounded-xl bg-gradient-to-r from-brandNavy to-brandGray border border-brandRed/40 flex flex-col sm:flex-row items-center justify-between gap-4 glow-red">
                        <div>
                            <span class="bg-brandRed text-white text-[10px] font-extrabold px-2 py-0.5 rounded uppercase">Handling for you</span>
                            <h3 class="text-lg font-bold text-white mt-1">Want us to handle your application with the best prices?</h3>
                            <p id="offerText" class="text-xs text-gray-300 mt-1">Our team prepares, verifies & submits your visa application from start to finish.</p>
                        </div>
                        <button onclick="triggerHandledAssistance()" class="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-brandRed hover:bg-brandRedDark text-white font-extrabold text-xs whitespace-nowrap transition shadow-lg">
                            Feel free to talk to our experienced human officers <i class="fa-solid fa-headset ml-1"></i>
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
                    <h1 class="text-3xl font-extrabold text-white">Need a suitable flight?</h1>
                </div>
                <button onclick="switchTab('home')" class="text-xs text-gray-400 hover:text-white flex items-center gap-1">
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
                        <label class="block text-xs font-bold text-gray-300 uppercase mb-2"><i class="fa-solid fa-plane-departure text-brandRed"></i> Departure City</label>
                        <select id="flightOriginCity" required class="w-full bg-brandBlack/80 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white focus:border-brandRed focus:outline-none">
                            <option value="">Select Departure City...</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-300 uppercase mb-2"><i class="fa-solid fa-plane-arrival text-brandRed"></i> Destination City</label>
                        <select id="flightDestCity" required class="w-full bg-brandBlack/80 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white focus:border-brandRed focus:outline-none">
                            <option value="">Select Arrival City...</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-300 uppercase mb-2"><i class="fa-solid fa-calendar text-brandRed"></i> Departure Date</label>
                        <input type="date" id="flightDepDate" required class="w-full bg-brandBlack/80 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white focus:border-brandRed focus:outline-none">
                    </div>
                    <div id="returnDateContainer">
                        <label class="block text-xs font-bold text-gray-300 uppercase mb-2"><i class="fa-solid fa-calendar-check text-brandRed"></i> Return Date</label>
                        <input type="date" id="flightRetDate" class="w-full bg-brandBlack/80 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white focus:border-brandRed focus:outline-none">
                    </div>

                    <div class="md:col-span-2 lg:col-span-4 mt-2">
                        <button type="submit" class="w-full py-4 rounded-xl bg-brandRed hover:bg-brandRedDark text-white font-bold text-sm tracking-wide transition shadow-lg shadow-brandRed/30 flex items-center justify-center gap-2">
                            <i class="fa-solid fa-magnifying-glass"></i> Scan Airlines & Compare Fares
                        </button>
                    </div>
                </form>
            </div>

            <!-- Flight Results -->
            <div id="flightResults" class="hidden space-y-4">
                <h3 class="text-xl font-bold text-white flex items-center gap-2">
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
                    <h1 class="text-3xl font-extrabold text-white">Find High-Rated Accommodations</h1>
                </div>
                <button onclick="switchTab('home')" class="text-xs text-gray-400 hover:text-white flex items-center gap-1">
                    <i class="fa-solid fa-arrow-left"></i> Back to Main
                </button>
            </div>

            <div class="glass-card p-6 sm:p-8 rounded-2xl space-y-6">
                <form id="hotelForm" onsubmit="event.preventDefault(); runHotelSearch();" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div>
                        <label class="block text-xs font-bold text-gray-300 uppercase mb-2"><i class="fa-solid fa-city text-brandRed"></i> Destination City</label>
                        <select id="hotelLocation" required class="w-full bg-brandBlack/80 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white focus:border-brandRed focus:outline-none">
                            <option value="">Choose Destination City...</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-300 uppercase mb-2"><i class="fa-solid fa-calendar-day text-brandRed"></i> Check-in</label>
                        <input type="date" id="hotelCheckIn" required class="w-full bg-brandBlack/80 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white focus:border-brandRed focus:outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-300 uppercase mb-2"><i class="fa-solid fa-calendar-day text-brandRed"></i> Check-out</label>
                        <input type="date" id="hotelCheckOut" required class="w-full bg-brandBlack/80 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white focus:border-brandRed focus:outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-300 uppercase mb-2"><i class="fa-solid fa-users text-brandRed"></i> Guests & Rooms</label>
                        <select id="hotelGuests" class="w-full bg-brandBlack/80 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white focus:border-brandRed focus:outline-none">
                            <option value="1 Guest, 1 Room">1 Guest, 1 Room</option>
                            <option value="2 Guests, 1 Room" selected>2 Guests, 1 Room</option>
                            <option value="4 Guests, 2 Rooms">4 Guests, 2 Rooms</option>
                        </select>
                    </div>

                    <div class="md:col-span-2 lg:col-span-4">
                        <button type="submit" class="w-full py-4 rounded-xl bg-brandRed hover:bg-brandRedDark text-white font-bold text-sm tracking-wide transition shadow-lg shadow-brandRed/30 flex items-center justify-center gap-2">
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
                        <span class="text-sm font-bold text-white">Price Filter:</span>
                        <input type="range" id="priceRange" min="50" max="1000" step="50" value="1000" oninput="filterHotels()" class="accent-brandRed cursor-pointer">
                        <span id="priceRangeValue" class="text-sm font-black text-brandRed">Up to $1000/night</span>
                    </div>
                    <div class="text-xs text-gray-400">
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
                    <h1 class="text-3xl font-extrabold text-white">Already There & Need Help?</h1>
                </div>
                <button onclick="switchTab('home')" class="text-xs text-gray-400 hover:text-white flex items-center gap-1">
                    <i class="fa-solid fa-arrow-left"></i> Back to Main
                </button>
            </div>

            <div class="glass-card p-6 rounded-2xl space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label class="block text-xs font-bold text-gray-300 uppercase mb-2"><i class="fa-solid fa-location-crosshairs text-brandRed"></i> Current Location / City</label>
                        <input type="text" id="groundLocation" placeholder="e.g. Cairo, Paris, Toronto, Dubai" value="Cairo" class="w-full bg-brandBlack/80 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white focus:border-brandRed focus:outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-300 uppercase mb-2"><i class="fa-solid fa-concierge-bell text-brandRed"></i> Required Assistance</label>
                        <select id="groundService" class="w-full bg-brandBlack/80 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white focus:border-brandRed focus:outline-none">
                            <option value="Airport Pickup / Taxi">Airport Pickup & Taxi Booking</option>
                            <option value="Domestic Transportation">Domestic Transportation & Rentals</option>
                            <option value="Nearby Restaurants">Nearby Top Rated Restaurants</option>
                            <option value="Nearby Hotels">Emergency Nearby Hotels</option>
                        </select>
                    </div>
                    <div class="flex items-end">
                        <button onclick="runGroundSearch()" class="w-full py-3.5 rounded-xl bg-brandRed hover:bg-brandRedDark text-white font-bold text-sm tracking-wide transition shadow-lg shadow-brandRed/30 flex items-center justify-center gap-2">
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
                    <h3 class="text-lg font-bold text-white border-b border-gray-800 pb-2 flex items-center gap-2">
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
        <button onclick="toggleChatbot()" class="w-14 h-14 rounded-full bg-brandRed hover:bg-brandRedDark text-white flex items-center justify-center shadow-2xl glow-red transition transform hover:scale-105">
            <i class="fa-solid fa-comments text-2xl"></i>
        </button>

        <!-- Chat Window -->
        <div id="chatBox" class="hidden absolute bottom-16 right-0 w-[340px] sm:w-[380px] h-[480px] glass-card rounded-2xl shadow-2xl flex flex-col overflow-hidden border-2 border-brandRed/50">
            <!-- Header -->
            <div class="bg-brandNavy p-4 border-b border-brandRed/30 flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <div class="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
                    <div>
                        <h4 class="text-sm font-bold text-white">PamsBeyond Live Chat</h4>
                        <span class="text-[10px] text-gray-400">Human Officers Online</span>
                    </div>
                </div>
                <button onclick="toggleChatbot()" class="text-gray-400 hover:text-white">
                    <i class="fa-solid fa-xmark"></i>
                </button>
            </div>

            <!-- Messages Area -->
            <div id="chatMessages" class="flex-grow p-4 overflow-y-auto space-y-3 text-xs">
                <div class="bg-brandGray p-3 rounded-xl border border-gray-800 text-gray-200">
                    👋 Hello! Welcome to PamsBeyond. How can our experienced human officers assist your travel plans today?
                </div>
            </div>

            <!-- Pre-scripted Quick Options -->
            <div class="px-3 py-2 bg-brandBlack/60 border-t border-gray-800 flex gap-1.5 overflow-x-auto text-[10px]">
                <button onclick="sendQuickMsg('Visa Requirements')" class="px-2.5 py-1 rounded-full bg-brandRed/20 text-brandRed font-semibold whitespace-nowrap hover:bg-brandRed hover:text-white transition">Visa Help</button>
                <button onclick="sendQuickMsg('Flight Fare Deals')" class="px-2.5 py-1 rounded-full bg-brandRed/20 text-brandRed font-semibold whitespace-nowrap hover:bg-brandRed hover:text-white transition">Flight Deals</button>
                <button onclick="sendQuickMsg('Talk to Officer')" class="px-2.5 py-1 rounded-full bg-brandRed/20 text-brandRed font-semibold whitespace-nowrap hover:bg-brandRed hover:text-white transition">Speak to Officer</button>
            </div>

            <!-- Input Bar -->
            <form onsubmit="handleUserChat(event)" class="p-3 bg-brandBlack border-t border-gray-800 flex items-center gap-2">
                <input type="text" id="chatInput" placeholder="Type your inquiry..." class="flex-grow bg-brandGray border border-gray-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-brandRed">
                <button type="submit" class="p-2 rounded-xl bg-brandRed hover:bg-brandRedDark text-white text-xs">
                    <i class="fa-solid fa-paper-plane"></i>
                </button>
            </form>
        </div>
    </div>


    <!-- ================================================================= -->
    <!-- MODAL: REQUEST ASSISTANCE / OFFICER FORM -->
    <!-- ================================================================= -->
    <div id="assistanceModal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-md hidden flex items-center justify-center p-4">
        <div class="glass-card max-w-lg w-full rounded-2xl p-6 sm:p-8 space-y-6 relative border-2 border-brandRed/50">
            <button onclick="closeAssistanceModal()" class="absolute top-4 right-4 text-gray-400 hover:text-white">
                <i class="fa-solid fa-xmark text-xl"></i>
            </button>

            <div>
                <span class="text-brandRed text-xs font-bold uppercase tracking-widest">PamsBeyond Officers</span>
                <h2 class="text-2xl font-bold text-white mt-1">Feel free to talk to our experienced human officers</h2>
                <p class="text-xs text-gray-400 mt-1">Fill out your details to connect directly with an operational officer.</p>
            </div>

            <form id="assistanceForm" onsubmit="handleAssistanceSubmit(event)" class="space-y-4">
                <div>
                    <label class="block text-xs font-bold text-gray-300 uppercase mb-1">Full Name</label>
                    <input type="text" id="clientName" required placeholder="e.g. John Doe" class="w-full bg-brandBlack/90 border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-white focus:border-brandRed focus:outline-none">
                </div>

                <div>
                    <label class="block text-xs font-bold text-gray-300 uppercase mb-1">Email Address</label>
                    <input type="email" id="clientEmail" required placeholder="john@example.com" class="w-full bg-brandBlack/90 border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-white focus:border-brandRed focus:outline-none">
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-bold text-gray-300 uppercase mb-1">Visa Type</label>
                        <input type="text" id="modalVisaType" readonly class="w-full bg-brandGray border border-gray-800 rounded-xl px-3 py-2 text-xs text-gray-300">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-300 uppercase mb-1">Destination</label>
                        <input type="text" id="modalDest" readonly class="w-full bg-brandGray border border-gray-800 rounded-xl px-3 py-2 text-xs text-gray-300">
                    </div>
                </div>

                <div id="priceOfferNotice" class="p-3 bg-brandRed/10 border border-brandRed/30 rounded-xl text-xs text-brandRed font-semibold flex items-center justify-between">
                    <span>Special Officer Processing Fee:</span>
                    <span id="offerPriceTag" class="text-sm font-black">$10.99</span>
                </div>

                <button type="submit" class="w-full py-3.5 rounded-xl bg-brandRed hover:bg-brandRedDark text-white font-bold text-sm tracking-wide transition shadow-lg shadow-brandRed/30 flex items-center justify-center gap-2">
                    <i class="fa-solid fa-paper-plane"></i> Connect With Officer Desk
                </button>
            </form>

            <div id="modalSuccess" class="hidden p-4 rounded-xl bg-green-900/40 border border-green-500 text-green-200 text-center text-xs space-y-2">
                <i class="fa-solid fa-circle-check text-2xl text-green-400"></i>
                <p class="font-bold">Request Sent Successfully!</p>
                <p>Our officer team has received your inquiry. Dynamic officer reply: <em class="text-white block mt-1 font-mono">"We can handle your application starting from $10.99."</em></p>
            </div>
        </div>
    </div>

    <!-- FOOTER -->
    <footer class="relative z-10 glass-card border-t border-brandRed/20 mt-12 py-6 px-4 text-center text-xs text-gray-500">
        <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
            <div class="flex items-center gap-2">
                <span class="font-black text-white uppercase tracking-wider">pams<span class="text-brandRed">beyond</span></span>
                <span>&copy; <span id="year"></span>. All rights reserved.</span>
            </div>
            <div class="flex items-center gap-4 text-gray-400">
                <a href="#" class="hover:text-brandRed">Privacy Policy</a>
                <a href="#" class="hover:text-brandRed">Terms of Service</a>
                <a href="#" class="hover:text-brandRed">Officer Desk</a>
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
            ['visaOrigin', 'visaDest'].forEach(id => {
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
            ['home', 'visa', 'flights', 'hotels', 'help'].forEach(id => {
                document.getElementById('view-' + id).classList.add('hidden');
            });
            document.getElementById('view-' + tabId).classList.remove('hidden');

            if(tabId === 'help' && leafletMap) {
                setTimeout(() => leafletMap.invalidateSize(), 300);
            }
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        // VISA SEARCH LOGIC
        function runVisaSearch() {
            const origin = document.getElementById('visaOrigin').value;
            const dest = document.getElementById('visaDest').value;
            const passType = document.getElementById('passportType').value;
            const vType = document.getElementById('visaType').value;

            if(!origin || !dest) return;

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

            const dynamicPrice = (origin === "Egypt" && dest === "Canada") ? "10.99" : "14.99";
            document.getElementById('offerText').textContent = `Someone traveling from ${origin} to ${dest}? We can handle your full ${vType} application starting from $${dynamicPrice}!`;
            document.getElementById('offerPriceTag').textContent = `$${dynamicPrice}`;

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
                                <h4 class="text-base font-bold text-white">${a.name}</h4>
                                <span class="bg-brandRed/20 text-brandRed text-[10px] font-bold px-2 py-0.5 rounded">${a.stops}</span>
                            </div>
                            <p class="text-xs text-gray-400 mt-1">${origin} ➔ ${dest} • Duration: ${a.time}</p>
                        </div>
                    </div>
                    <div class="flex items-center gap-4 w-full md:w-auto justify-between md:justify-end border-t md:border-t-0 border-gray-800 pt-3 md:pt-0">
                        <div class="text-left md:text-right">
                            <span class="text-[10px] text-gray-400 uppercase block">Best Available Rate</span>
                            <span class="text-2xl font-black text-brandRed">${a.price}</span>
                        </div>
                        <a href="https://www.skyscanner.com" target="_blank" class="px-5 py-2.5 rounded-xl bg-brandRed hover:bg-brandRedDark text-white font-bold text-xs transition shadow-md flex items-center gap-1">
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
                list.innerHTML = `<div class="col-span-3 text-center py-8 text-gray-400">No accommodations found under $${maxPrice}. Adjust the filter.</div>`;
                return;
            }

            list.innerHTML = filtered.map(h => `
                <div class="glass-card rounded-2xl overflow-hidden glass-card-hover flex flex-col justify-between">
                    <div>
                        <div class="relative h-48 overflow-hidden">
                            <img src="${h.img}" alt="${h.name}" class="w-full h-full object-cover">
                            <span class="absolute top-3 left-3 bg-brandBlack/80 border border-brandRed/40 text-brandRed text-[10px] font-extrabold px-2 py-1 rounded-md uppercase tracking-wider">${h.tag}</span>
                            <span class="absolute bottom-3 right-3 bg-brandBlack/80 text-yellow-400 font-bold text-xs px-2 py-1 rounded-md">${h.rating}</span>
                        </div>
                        <div class="p-5">
                            <h4 class="text-lg font-bold text-white">${h.name}</h4>
                            <p class="text-xs text-gray-400 mt-1"><i class="fa-solid fa-wifi text-brandRed"></i> Free High-Speed WiFi • Pool • Airport Transfer</p>
                        </div>
                    </div>
                    <div class="p-5 pt-0 flex items-center justify-between border-t border-gray-800/80 mt-2">
                        <div>
                            <span class="text-[10px] text-gray-400 block">Nightly Rate</span>
                            <span class="text-xl font-black text-brandRed">$${h.price} <span class="text-xs text-gray-400 font-normal">/ night</span></span>
                        </div>
                        <a href="https://www.booking.com" target="_blank" class="px-4 py-2 rounded-xl bg-brandRed hover:bg-brandRedDark text-white text-xs font-bold transition">
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
                <div class="p-3 rounded-xl bg-brandBlack/60 border border-brandRed/30 space-y-1">
                    <div class="flex items-center justify-between font-bold text-white">
                        <span>${p.name}</span>
                        <span class="text-brandRed">${p.rate}</span>
                    </div>
                    <p class="text-gray-400 text-[11px]"><i class="fa-solid fa-phone text-brandRed"></i> ${p.phone}</p>
                    <button onclick="openAssistanceModal('${service}', '${location}')" class="w-full mt-2 py-1.5 rounded bg-brandRed/20 hover:bg-brandRed text-brandRed hover:text-white font-bold text-[10px] transition">
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
            msg.className = "bg-brandRed text-white p-2.5 rounded-xl ml-auto max-w-[80%] text-right font-medium";
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
        function openAssistanceModal(visaType = "Tourist Visa", dest = "Global") {
            document.getElementById('modalVisaType').value = visaType;
            document.getElementById('modalDest').value = dest;
            document.getElementById('assistanceModal').classList.remove('hidden');
            document.getElementById('modalSuccess').classList.add('hidden');
            document.getElementById('assistanceForm').classList.remove('hidden');
        }

        function closeAssistanceModal() {
            document.getElementById('assistanceModal').classList.add('hidden');
        }

        function handleAssistanceSubmit(e) {
            e.preventDefault();
            const name = document.getElementById('clientName').value;
            const email = document.getElementById('clientEmail').value;
            const visaType = document.getElementById('modalVisaType').value;
            const dest = document.getElementById('modalDest').value;

            document.getElementById('assistanceForm').classList.add('hidden');
            document.getElementById('modalSuccess').classList.remove('hidden');

            const subject = encodeURIComponent(`PamsBeyond Request: ${visaType} for ${dest}`);
            const body = encodeURIComponent(`Client Name: ${name}\nClient Email: ${email}\nVisa Type: ${visaType}\nDestination: ${dest}`);
            
            setTimeout(() => {
                window.location.href = `mailto:support@pamsbeyond.com?subject=${subject}&body=${body}`;
            }, 1500);
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

# Render Embedded Web App Component
components.html(html_code, height=950, scrolling=True)