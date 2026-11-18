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

## 🔥 Firebase Authentication & Cloud Firestore Setup

AirSaathi AI supports dual operational modes:
- **Guest / Demonstration Mode**: Operates out-of-the-box with zero credentials required. User preferences and routine selections are stored in temporary browser memory.
- **Authenticated Cloud Persistence Mode**: Full user accounts, family vulnerability settings, indoor appliance tracking, and commuting histories are securely persisted in Cloud Firestore under authenticated user tenancy.

### Step 1: Create a Firebase Project
1. Navigate to the [Firebase Console](https://console.firebase.google.com/).
2. Click **Add project**, provide a project name (e.g., `airsaathi-ai`), and proceed with creation.

### Step 2: Enable Email/Password Authentication
1. In your Firebase Console, open **Build** > **Authentication**.
2. Click **Get Started**, choose **Email/Password** from the Sign-in providers list.
3. Toggle **Enable** for Email/Password and click **Save**.

### Step 3: Provision Cloud Firestore
1. In the Firebase Console, open **Build** > **Firestore Database**.
2. Click **Create database**, select a region (e.g. `asia-south1` for Mumbai, India), and select **Production mode**.
3. Apply the security rules defined in [firestore.rules](file:///C:/Users/gupta/Desktop/AirSaathi-AI/firestore.rules) either via the Firebase Console **Rules** tab or using the Firebase CLI (`firebase deploy --only firestore:rules`).

### Step 4: Configure Frontend Web Credentials
1. In Firebase Console, go to **Project Settings** > **General** > **Your apps** and click the **Web** icon (`</>`).
2. Register the web app and copy the configuration keys.
3. In `frontend/`, create `.env` (or `.env.local`) using [frontend/.env.example](file:///C:/Users/gupta/Desktop/AirSaathi-AI/frontend/.env.example):
   ```bash
   VITE_FIREBASE_API_KEY=AIzaSy...
   VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=your-project
   VITE_FIREBASE_APP_ID=1:123456789012:web:abcdef...
   VITE_API_BASE_URL=http://localhost:8000
   ```

### Step 5: Configure Backend Admin SDK
1. In Firebase Console, go to **Project Settings** > **Service accounts**.
2. Click **Generate new private key** and download the JSON key.
3. Store the key file in a secure local path (outside Git) and configure `backend/.env` using [backend/.env.example](file:///C:/Users/gupta/Desktop/AirSaathi-AI/backend/.env.example):
   ```bash
   FIREBASE_PROJECT_ID=your-project
   FIREBASE_SERVICE_ACCOUNT_PATH=/absolute/path/to/serviceAccountKey.json
   ```
   *(Alternatively, for cloud deployments such as Cloud Run, rely on Google Application Default Credentials or stringified `FIREBASE_SERVICE_ACCOUNT_JSON`)*.

---

## 🗺️ 7-Module Product Roadmap

- [x] **Module 1: Air Quality Dashboard** (Real-time CPCB telemetry, NAQI breakpoint calculations, diurnal inversion modeling, multi-station selection).
- [x] **Module 2: AI Daily Routine Planner** (Smog-aware commute, school, and outdoor exercise scheduler powered by Google Gemini with expert-rule fallback).
- [x] **Module 3: Indoor Air Quality Assistant** (Room volume sizing, CADR calculations, HEPA filtration guidance, and safe aeration windows).
- [x] **Module 4: Gemini-Powered Hindi/English Chatbot** (Bilingual environmental consultation with CPCB context injection).
- [x] **Module 5: Sustainable Mobility Assistant** (AQI-aware commute planner with city-specific transit verification, passenger-level emission math, and CEA grid factor).
- [x] **Core Infrastructure: External Weather Service** (Real-time ambient weather via Open-Meteo with caching and graceful demo fallback).
- [x] **Core Infrastructure: Firebase Authentication & Cloud Firestore** (Email/Password registration, session tokens, tenant-isolated Firestore rules, and guest mode).
- [ ] **Module 6: Environmental Impact Tracker** (Household emission reductions, carbon avoidance, community milestones).
- [ ] **Module 7: Family Profile & Preferences** (Multi-generational medical condition tracking and push notification triggers).
