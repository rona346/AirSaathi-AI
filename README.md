# AirSaathi AI (एयरसाथी) 🌿🌫️
> **GenAI-Powered Urban Air Quality & Smog Intelligence Platform**

AirSaathi AI is an urban resilience platform built to help families and communities understand toxic winter smog, protect vulnerable populations (infants, seniors, asthmatics), optimize indoor air quality (HEPA CADR and ventilation), adopt low-emission transit routines, and track collective environmental impact. The platform offers a complete bilingual (English and Hindi) experience across all analytics, advisories, and assistant modules.

---

## 🌐 Live Production Deployment

| Layer | Canonical Live URL | Platform / Infrastructure | Notes |
|---|---|---|---|
| **Frontend** | [https://air-saathi-ai.vercel.app](https://air-saathi-ai.vercel.app) | Vercel Edge Network | Single-Page Application (React 18 + Vite 6 + Tailwind CSS) |
| **Backend** | [https://airsaathi-backend-c7voakhfiq-el.a.run.app](https://airsaathi-backend-c7voakhfiq-el.a.run.app) | Google Cloud Run (`asia-south1`, Mumbai) | Containerized FastAPI server via root `Dockerfile` |

### Production Architecture & Routing Flow
- **Relative API Client Routing:** The frontend API client issues requests to relative paths (`/api/v1/*`).
  - **Local Development:** Proxied to `http://localhost:8000` via `frontend/vite.config.ts`.
  - **Production Deployment:** Rewritten directly to the canonical Cloud Run backend service URL via `frontend/vercel.json` (`/api/:path*` -> `https://airsaathi-backend-c7voakhfiq-el.a.run.app/api/:path*`), with a fallback rule (`/(.*)` -> `/index.html`) ensuring seamless client-side routing.
- **Firebase Authentication Domains:** The production Vercel domain (`air-saathi-ai.vercel.app`) is configured in Firebase Authorized Domains for OAuth and email/password sessions.
- **Stateless Cloud Run Runtime:** Deployed with Google Application Default Credentials (ADC), autoscaling from zero, and dynamically binding Uvicorn to the container `$PORT`.

*(Note: The latest bounded Gemini 8-second timeout fix and frontend UI polish improvements have been implemented locally and validated by the test suite, pending deployment in the next release cycle).*

---

## 🏛️ Monorepo Architecture

```
AirSaathi-AI/
├── Dockerfile                    # Cloud Run container build specification (Python 3.10-slim + Uvicorn)
├── firestore.rules               # Cloud Firestore security rules (101 lines: tenant isolation & admin locking)
├── frontend/                     # React 18 + Vite 6 + TypeScript 5 + Tailwind CSS 3
│   ├── vercel.json               # Vercel production rewrites (/api/:path* -> Cloud Run) & SPA fallback
│   ├── vite.config.ts            # Vite bundler configuration with backend proxy (/api -> localhost:8000)
│   ├── tailwind.config.js        # CPCB-aligned color palette & glassmorphism utilities
│   ├── package.json              # Frontend scripts & dependencies
│   └── src/
│       ├── main.tsx              # DOM mounting & Firebase initialization
│       ├── App.tsx               # Main layout, module orchestration & zero-CLS skeleton placeholder
│       ├── types/                # TypeScript data contracts (aqi, routine, indoor, chat, mobility, impact, user)
│       ├── utils/
│       │   ├── aqiUtils.ts       # CPCB bands, color mapping & timestamp helpers
│       │   └── translations.ts   # Comprehensive bilingual (English / Hindi) localization dictionary
│       ├── services/
│       │   ├── api.ts            # Relative /api/v1 client with graceful offline demonstration fallbacks
│       │   └── mockData.ts       # Calibrated CPCB baseline demonstration data
│       ├── context/
│       │   └── AppContext.tsx    # State management (stations, languages, user profile, demo mode flag)
│       └── components/
│           ├── layout/           # Navbar (station selector, bilingual toggle, scrollable tabs) & Footer
│           ├── dashboard/        # DemoDataBanner, AqiCard, PollutantBreakdown, HourlyTrendChart,
│           │                     # HealthRecommendations, VulnerabilityAlerts, QuickModuleNav
│           ├── auth/             # AuthModal (Email/Password registration & sign-in)
│           ├── planner/          # DailyPlanner (Module 2: Smog-aware routine planner)
│           ├── indoor/           # IndoorAssistant (Module 3: CADR, HEPA & ventilation guide)
│           ├── chat/             # ChatAssistant (Module 4: Bilingual Gemini consultation)
│           ├── mobility/         # MobilityAssistant (Module 5: Emission-optimized commute planner)
│           ├── impact/           # ImpactTracker (Module 6: Household carbon & mitigation tracker)
│           └── family/           # FamilyProfileAssistant (Module 7: Multi-generational profiles & advisories)
├── backend/                      # Python 3.10+ + FastAPI + Pydantic v2
│   ├── requirements.txt          # Python dependencies (google-genai, fastapi, firebase-admin, etc.)
│   ├── app/
│   │   ├── main.py               # FastAPI app instance, CORS middleware & lifespan loader
│   │   ├── core/
│   │   │   ├── config.py         # Settings & environment variables (data.gov.in, Gemini, Firebase)
│   │   │   ├── auth.py           # Firebase Auth token verification & user context extraction
│   │   │   ├── firebase.py       # Firebase Admin SDK & Cloud Firestore initialization
│   │   │   └── gemini.py         # Bounded Google GenAI SDK client (8s timeout, 2 retries, fallback)
│   │   ├── models/               # Pydantic schemas (aqi, chat, routine, indoor, mobility, impact, user, weather)
│   │   ├── services/
│   │   │   ├── aqi_service.py    # NAQI breakpoint calculations & diurnal model
│   │   │   ├── live_aqi_provider.py # data.gov.in CPCB CAAQMS provider + DemoAqiProvider fallback
│   │   │   ├── weather_service.py   # Open-Meteo micro-meteorology (dispersion & boundary layer)
│   │   │   ├── cpcb_calculator.py   # Mathematical sub-index calculation routines
│   │   │   ├── emissions_service.py # Transit emission factors & CEA electricity grid math
│   │   │   ├── firestore_service.py # Cloud Firestore CRUD operations under user tenancy
│   │   │   └── ...                  # Module-specific services (routine, indoor, chat, mobility, impact, user)
│   │   └── api/v1/endpoints/     # REST route handlers (health, aqi, routine, indoor, chat, mobility, impact, user, weather)
│   └── tests/                    # 15 pytest test suites (161 tests covering API, services, CPCB, and security)
```

---

## 🛠️ Technology Stack

| Layer | Technologies & Libraries | Verified Specification / Version |
|---|---|---|
| **Frontend** | React, Vite, TypeScript, Tailwind CSS, Recharts, Lucide Icons | React 18.3.1, Vite 6.1.0, TypeScript 5.7.3, Tailwind CSS 3.4.17, Recharts 2.15.1, Lucide React 0.475.0 |
| **Backend** | Python, FastAPI, Pydantic, Uvicorn, Httpx | Python 3.10+, FastAPI 0.110.0+, Pydantic v2.6.0+, Uvicorn 0.28.0+, Httpx 0.27.0+ |
| **AI Layer** | Google GenAI Python SDK | `google-genai==2.24.0` (Client interactions with structured JSON schemas & bounded 8.0s timeout) |
| **Telemetry & Weather** | Open-Meteo API | Temperature, relative humidity, wind speed, wind direction, boundary layer mixing height (15-min TTL caching) |
| **Air Quality Telemetry** | data.gov.in CPCB CAAQMS API | Resource ID `3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69` (Dual-mode: live ingestion when configured, calibrated fallback) |
| **Authentication & Database** | Firebase Authentication & Cloud Firestore | Firebase Web SDK 13.4.0, `firebase-admin>=6.5.0`, 101-line custom `firestore.rules` for tenant isolation |
| **Test Suite** | Pytest & pytest-asyncio | 161 automated test cases across 15 test suites (endpoints, CPCB calculations, emission math, auth & rules) |
| **Production Infrastructure** | Vercel & Google Cloud Run | Vercel Edge Network (Frontend SPA), Cloud Run `asia-south1` (stateless autoscaling backend container) |

---

## 🛡️ Core Engineering Principles

1. **Dual-Mode Ambient Telemetry & Zero Hallucination:**
   - **Live Ingestion Mode:** When `DATAGOVIN_API_KEY` is configured, the backend queries the official data.gov.in CPCB CAAQMS resource (`3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69`) with 15-minute in-memory caching and strict measurement validation (requires at least 3 valid pollutants including PM2.5 or PM10).
   - **Calibrated Baseline Demonstration Mode:** When `DATAGOVIN_API_KEY` is not provided (or `MOCK_MODE=True`), the system operates on realistic, calibrated CPCB winter smog baseline measurements for Delhi-NCR and Mumbai stations. All demonstration payloads are explicitly stamped with `is_demo_data: true` and surfaced with transparent visual badges in the UI. Ambient air numbers are never synthetically invented or falsely presented as live.
2. **Server-Side Key Isolation:** Gemini API keys, data.gov.in API keys, and Firebase service account credentials reside exclusively on the backend. Zero secrets are exposed to client browser bundles.
3. **Bounded GenAI Execution & Sub-Second Fallback:** In the local working tree, Google GenAI interaction calls are bounded to an 8.0-second execution window with 2 HTTP retry attempts (`HttpOptions(timeout=8000, retry_options=HttpRetryOptions(attempts=2))`). If Gemini is unavailable, rate-limited, or exceeds the deadline, the platform automatically returns deterministic mathematical or expert-rule fallbacks, preventing Cloud Run 504 Gateway Timeouts.
4. **CPCB NAQI Standards & Micro-Meteorology:** Strict compliance with Indian National Air Quality Index 6-band categorization (Good, Satisfactory, Moderate, Poor, Very Poor, Severe), WHO 24-hr benchmarks, and diurnal temperature inversion modeling (nocturnal surface radiation inversion causing early morning spikes).
5. **Comprehensive Bilingual Experience:** Complete localization across English (`en`) and Hindi (`hi`) for all 7 modules, navigation tabs, pollutant medical descriptions, and advisory guidelines.

---

## 🚀 Local Development Setup

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- (Optional) Google AI Studio API key (`GEMINI_API_KEY`)
- (Optional) data.gov.in API key (`DATAGOVIN_API_KEY`)

---

### 1. Backend (FastAPI)

> **Important:** All backend modules and tests use absolute package imports prefixed with `backend.` (e.g. `from backend.app.api.v1.api import api_router`). Run all test and server commands from the **repository root**.

```bash
# Clone the repository
git clone https://github.com/rona346/AirSaathi-AI.git
cd AirSaathi-AI

# Create and activate virtual environment
python -m venv backend/venv
.\backend\venv\Scripts\activate      # On Windows (PowerShell)
# source backend/venv/bin/activate    # On Linux/macOS

# Install dependencies
pip install -r backend/requirements.txt

# Run the complete test suite (161 tests, executed from repo root)
python -m pytest backend/tests -v

# Start development server (executed from repo root)
python -m uvicorn backend.app.main:app --reload --port 8000
```
Interactive API documentation will be available at: `http://localhost:8000/docs`

---

### 2. Frontend (React + Vite)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run type check and production build
npm run build

# Start local development server
npm run dev
```
Open `http://localhost:5173` in your browser.

> **API Routing Note:** The frontend communicates via relative `/api/v1` routes. During local development, `frontend/vite.config.ts` automatically proxies `/api` to `http://localhost:8000`. No manual `VITE_API_BASE_URL` configuration is required.

---

## 🔥 Firebase Authentication & Cloud Firestore Setup

AirSaathi AI supports dual operational modes:
- **Guest / Demonstration Mode:** Operates out-of-the-box with zero credentials required. User preferences and routine selections are stored in temporary browser memory.
- **Authenticated Cloud Persistence Mode:** Full user accounts, family vulnerability settings, indoor appliance tracking, and commuting histories are securely persisted in Cloud Firestore under authenticated user tenancy.

### Step 1: Create a Firebase Project
1. Navigate to the [Firebase Console](https://console.firebase.google.com/).
2. Click **Add project**, provide a project name (e.g., `airsaathi-ai`), and proceed with creation.

### Step 2: Enable Email/Password Authentication
1. In your Firebase Console, open **Build** > **Authentication**.
2. Click **Get Started**, choose **Email/Password** from the Sign-in providers list.
3. Toggle **Enable** for Email/Password and click **Save**.

### Step 3: Provision Cloud Firestore & Apply Security Rules
1. In the Firebase Console, open **Build** > **Firestore Database**.
2. Click **Create database**, select a region (e.g. `asia-south1` for Mumbai, India), and select **Production mode**.
3. Apply the security rules defined in [`firestore.rules`](./firestore.rules) either via the Firebase Console **Rules** tab or using the Firebase CLI (`firebase deploy --only firestore:rules`).

### Step 4: Configure Frontend Web Credentials
1. In Firebase Console, go to **Project Settings** > **General** > **Your apps** and click the **Web** icon (`</>`).
2. Register the web app and copy the configuration keys.
3. In `frontend/`, create `.env` (or `.env.local`) using [`frontend/.env.example`](./frontend/.env.example):
   ```bash
   VITE_FIREBASE_API_KEY=AIzaSy...
   VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=your-project
   VITE_FIREBASE_APP_ID=1:123456789012:web:abcdef...
   ```
   *(Note: The frontend uses relative `/api/v1` paths; Vite proxies them locally and Vercel rewrites them in production).*

### Step 5: Configure Backend Admin SDK & Telemetry Keys
1. In Firebase Console, go to **Project Settings** > **Service accounts**.
2. Click **Generate new private key** and download the JSON key.
3. Store the key file in a secure local path (outside Git) and configure `backend/.env` using [`backend/.env.example`](./backend/.env.example):
   ```bash
   FIREBASE_PROJECT_ID=your-project
   FIREBASE_SERVICE_ACCOUNT_PATH=/absolute/path/to/serviceAccountKey.json

   # Optional: Configure Gemini API key for GenAI planner & chatbot
   GEMINI_API_KEY=your_gemini_api_key_here

   # Optional: Configure data.gov.in API key for live CPCB CAAQMS telemetry
   DATAGOVIN_API_KEY=your_datagovin_api_key_here
   ```
   *(Alternatively, for cloud deployments such as Cloud Run, rely on Google Application Default Credentials or stringified `FIREBASE_SERVICE_ACCOUNT_JSON`)*.

---

## 🗺️ 7-Module Product Roadmap

- [x] **Module 1: Air Quality Dashboard** (Dual-mode CPCB telemetry: live data.gov.in CAAQMS ingestion when configured with automatic fallback to calibrated winter smog demonstration baselines, NAQI breakpoint calculations, diurnal inversion modeling, multi-station selection).
- [x] **Module 2: AI Daily Routine Planner** (Smog-aware commute, school, and outdoor exercise scheduler powered by Google Gemini with deterministic expert-rule fallback).
- [x] **Module 3: Indoor Air Quality Assistant** (Room volume sizing, CADR calculations, HEPA filtration guidance, and safe aeration windows).
- [x] **Module 4: Gemini-Powered Hindi/English Chatbot** (Bilingual environmental consultation with CPCB context injection and structured prompt safety).
- [x] **Module 5: Sustainable Mobility Assistant** (AQI-aware commute planner with city-specific transit verification, passenger-level emission math, and CEA grid factor).
- [x] **Module 6: Environmental Impact Tracker** (Household transit emission mitigation math using CEA electricity grid factors, commute activity logging, and carbon savings summaries).
- [x] **Module 7: Family Profile & Personalization** (Multi-generational medical condition tracking, appliance registries, vulnerability-adapted advisory guidelines, and cloud-synced user settings).
- [x] **Core Infrastructure: External Weather Telemetry** (Real-time ambient weather and mixing layer height via Open-Meteo with 15-minute caching and graceful demo fallback).
- [x] **Core Infrastructure: Firebase Authentication & Cloud Firestore** (Email/Password registration, session persistence, 101-line tenant-isolated Firestore security rules, and seamless guest mode).
