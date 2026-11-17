# AirSaathi AI (एयरसाथी) 🌿🌫️
> **GenAI-Powered Urban Air Quality & Smog Intelligence Platform**

AirSaathi AI is an urban resilience platform built to help families and communities understand toxic winter smog, protect vulnerable populations (infants, seniors, asthmatics), optimize indoor air quality (HEPA CADR and ventilation), adopt low-emission transit routines, and track collective environmental impact.

---

## 🏛️ Monorepo Architecture

```
AirSaathi-AI/
├── frontend/                     # React + Vite + TypeScript + Tailwind CSS
│   ├── index.html                # HTML5 entry with Plus Jakarta Sans & NAQI meta
│   ├── vite.config.ts            # Vite bundler configuration with backend proxy
│   ├── tailwind.config.js        # CPCB-aligned color palette & glassmorphism utilities
│   ├── postcss.config.js         # PostCSS plugins
│   ├── tsconfig.json             # TypeScript compiler settings (strict mode)
│   ├── package.json              # Frontend scripts & dependencies
│   └── src/
│       ├── main.tsx              # DOM mounting
│       ├── App.tsx               # Primary application layout & module orchestration
│       ├── index.css             # Glassmorphism, animations & scrollbar utilities
│       ├── types/
│       │   └── aqi.ts            # Data contracts for AQI, pollutants, stations & family
│       ├── utils/
│       │   └── aqiUtils.ts       # CPCB bands, color mapping & timestamp helpers
│       ├── services/
│       │   ├── api.ts            # Dual-mode API client (FastAPI + fallback)
│       │   └── mockData.ts       # Calibrated CPCB baseline demonstration data
│       ├── context/
│       │   └── AppContext.tsx    # State management (stations, languages, profile)
│       └── components/
│           ├── layout/
│           │   ├── Navbar.tsx    # Station selector, language toggle, family badge
│           │   └── Footer.tsx    # Attribution, data provenance & security standards
│           └── dashboard/
│               ├── DemoDataBanner.tsx        # Transparent demonstration mode indicator
│               ├── AqiCard.tsx               # Hero AQI, prominent pollutant & weather
│               ├── PollutantBreakdown.tsx    # PM2.5, PM10, NO2, SO2, CO, O3 cards
│               ├── HourlyTrendChart.tsx      # 24-hr diurnal area chart with inversion peak
│               ├── HealthRecommendations.tsx # N95 masks, HEPA purifiers, ventilation
│               ├── VulnerabilityAlerts.tsx   # Demographic guards (children, seniors, asthma)
│               └── QuickModuleNav.tsx        # 7-module architecture pipeline
├── backend/                      # Python + FastAPI + Pydantic
│   ├── requirements.txt          # Python dependencies
│   ├── app/
│   │   ├── main.py               # FastAPI app instance, CORS & router mounting
│   │   ├── core/
│   │   │   └── config.py         # App settings & environment variable management
│   │   ├── models/
│   │   │   ├── aqi.py            # Pydantic schemas for AQI & meteorology
│   │   │   └── response.py       # Standard envelope (success, data, is_demo_data)
│   │   ├── services/
│   │   │   └── aqi_service.py    # NAQI calculation, diurnal models & station registry
│   │   └── api/
│   │       └── v1/
│   │           ├── api.py        # V1 API router
│   │           └── endpoints/
│   │               ├── health.py # Health & readiness check endpoint
│   │               └── aqi.py    # Station list, current AQI & diurnal forecast
│   └── tests/
│       ├── test_api.py           # Pytest test suite covering endpoints & calculations
│       └── verify_backend.py     # Standalone verification runner
├── firestore.rules               # Cloud Firestore security rules with user-scoped isolation
├── .gitignore                    # Git ignore configuration
└── README.md                     # Project documentation
```

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite 6, TypeScript 5, Tailwind CSS 3, Recharts 2, Lucide React |
| **Backend** | Python 3.10+, FastAPI, Pydantic v2, Uvicorn, Httpx |
| **AI Layer** | Google Gemini API (Structured JSON generation & conversational guidance) |
| **Database** | Firebase Authentication, Cloud Firestore (Rule-enforced tenant isolation) |
| **Deployment Targets** | Vercel (Frontend SPA), Google Cloud Run (Backend container) |

---

## 🛡️ Core Engineering Principles

1. **Zero Synthetic AQI Hallucination**: Ambient air quality numbers and pollutant concentrations are never fabricated. All demonstration data is strictly flagged as `is_demo_data: true` with primary source attribution (`CPCB / CAAQMS`).
2. **Server-Side Key Isolation**: Gemini API keys and cloud credentials reside exclusively on the backend. No secret is exposed to browser bundles.
3. **CPCB NAQI Standards**: Strict alignment with Indian National Air Quality Index 6-band categorization (Good, Satisfactory, Moderate, Poor, Very Poor, Severe) and comparisons against WHO 24-hr guidelines.
4. **Diurnal Inversion Modeling**: Captures the micro-meteorology of winter smog in Northern India (nocturnal surface radiation temperature inversion causing 6:00 AM – 9:30 AM spikes and 1:30 PM – 4:00 PM atmospheric mixing troughs).

---

## 🚀 Local Development Setup

### 1. Backend (FastAPI)
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate   # On Windows
# source venv/bin/activate # On Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Run test suite
python -m pytest tests -v

# Start development server
python -m uvicorn app.main:app --reload --port 8000
```
API Documentation will be available at: `http://localhost:8000/docs`

### 2. Frontend (React + Vite)
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run type check and build
npm run build

# Start local development server
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🗺️ 7-Module Product Roadmap

- [x] **Module 1: Air Quality Dashboard** (Initial implementation complete with responsive UI, pollutant breakdown, diurnal forecast, family vulnerability guard, and CPCB baseline data).
- [ ] **Module 2: AI Daily Routine Planner** (Smog-adjusted commute, school, and outdoor schedule optimizer powered by Gemini).
- [ ] **Module 3: Indoor Air Quality Assistant** (CADR calculation, room volume sizing, HEPA filter lifetime tracking, and optimal aeration windows).
- [ ] **Module 4: Gemini-Powered Hindi/English Chatbot** (Contextual voice/text assistant explaining symptoms, masks, and winter care).
- [ ] **Module 5: Sustainable Mobility Assistant** (Low-exposure routes, public transit vs. driving emission comparison, EV incentives).
- [ ] **Module 6: Environmental Impact Tracker** (Household emission reductions, carbon avoidance, community milestones).
- [ ] **Module 7: Family Profile & Preferences** (Multi-generational medical condition tracking and push notification triggers).
