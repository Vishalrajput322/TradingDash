# TradingDash Project Progress

Updated: 2026-11-24

## Project overview

TradingDash is a trading analytics dashboard with a Django REST backend and a Flutter frontend. The backend contains market-data ingestion, option-chain snapshots, analytics, and alerting components. The frontend displays selected-symbol analytics from the dashboard API.

## Implemented

### Backend

- Django REST API with analytics endpoints, including `GET /api/analytics/dashboard/overview/?symbol=NIFTY`.
- Analytics services for PCR, max pain, open-interest changes/build-up, and smart-money flow.
- Option-chain snapshot and market-data service components.
- Instruments now have exchange and asset-class metadata; futures snapshots have a separate model and dashboard response.
- Dashboard API and Flutter selectors now support NSE/MCX and options/futures product selection.
- NSE index options include NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, and NIFTYNXT50. Selecting an NSE OPTIONS instrument fetches and stores a fresh option-chain snapshot before returning dashboard data.
- Data-provider loading is exchange-configurable through `MARKET_DATA_PROVIDERS`; NSE stock option-chain requests use the equity contract type.
- Alert engine and notification integrations.
- Custom User model (`accounts.User`) and Trader Profile (`accounts.UserProfile`) with automatic profile generation signals.
- JWT authentication endpoints: `/api/auth/register/`, `/api/auth/login/`, `/api/auth/refresh/`, `/api/auth/me/`, `/api/auth/profile/`.
- CORS middleware configured for local Flutter web origins (`localhost` and `127.0.0.1`) in debug mode. Additional origins can be configured with `CORS_ALLOWED_ORIGINS`.

MCX and futures feeds are not bundled. The provider interface and snapshot commands are documented in [backend/README.md](../backend/README.md); a compatible provider and its credentials are still needed to populate those products with live data.

### Frontend

- Flutter dashboard with NSE index selection, on-demand snapshot refresh, and 60-second read-only polling.
- Dashboard cards for PCR, market bias, max pain, and alert count, plus call/put build-up summaries.
- API client and model parsing for the backend dashboard payload.
- Responsive metric grid and loading, error, and retry states.
- JWT authentication client with persistent `shared_preferences` storage, automatic `Bearer` header injection, and silent 401 token refresh in `DioClient`.
- Full authentication & profile management UI: tabbed `AuthDialog` (Log In / Sign Up), `ProfileDialog` for notification channels (Telegram Chat ID, WhatsApp phone) and default trading preferences, plus dynamic user avatar/status chip on the AppBar.

## Verification completed

- `flutter analyze` — passed with 0 issues.
- `flutter test` — all 4 tests passed (dashboard models + user/profile models).
- Backend accounts unit tests (`python manage.py test accounts`) — 3/3 passed.
- Focused Django dashboard and market-data tests — passed.
- Django `manage.py check` and migration consistency check using `backend/.venv` — passed.
- Flutter options and futures payload tests — passed.
- Live CORS preflight to the dashboard endpoint — returned HTTP 200 and an allowed local Flutter origin.
- FINNIFTY selection now triggers the on-demand snapshot refresh; the user confirmed the flow is working.

The preflight check confirms browser-origin access is configured. A full live dashboard-data response was not verified as part of these checks.

## Roadmap

### Priority 1: Production readiness

**Status: Incomplete.**

- `backend/requirements.txt` includes the backend runtime dependencies, including `django-celery-beat` and `python-decouple`.
- Add `backend/.env.example` with variable names and safe placeholder values only.
- Add a backend `Dockerfile` and document production environment variables, migrations, and deployment startup.
- Keep secrets out of the example file and configure production CORS origins, allowed hosts, database credentials, and secret keys through deployment environment variables.

### Priority 2: Dashboard polish

**Status: Partially complete.**

- The dashboard displays PCR, market bias, max pain, alert count, and call/put build-up summaries.
- Snapshot time is already shown in the footer, but is not a dedicated metric card.
- Add dedicated cards for latest snapshot time, total snapshots stored, current expiry, alert count, and NIFTY spot.
- The frontend currently defaults `alert_count` to zero, while the dashboard service does not currently include that field in its response. Add the backend value before presenting it as live data.
- Verify the backend exposes the required expiry and spot values before wiring those cards.

### Priorities 3–4: Historical analytics and charts

**Status: Not implemented.**

Option-chain snapshots and service-level calculations provide historical data to build on, but no history API endpoints were found. Implement and test:

- `GET /api/analytics/pcr-history/?symbol=NIFTY`
- `GET /api/analytics/max-pain-history/?symbol=NIFTY`
- `GET /api/analytics/market-bias-history/?symbol=NIFTY`

Return timestamped series, for example:

```json
[
  {
    "timestamp": "2026-11-24T15:00:00+05:30",
    "pcr": 1.67
  }
]
```

Once the APIs are available, add PCR history, max-pain trend, and OI-change charts to the Flutter dashboard.

### Priority 5: Deployment

**Status: Not started.**

- Deploy PostgreSQL and Redis alongside the backend.
- Choose a backend host (for example Railway, Hetzner, or DigitalOcean) and deploy Flutter Web to a production URL.
- Verify production environment variables, CORS, migrations, and the dashboard API from the deployed frontend.
- Prioritize a working end-to-end deployment before adding further Telegram or WhatsApp features.

## Additional validation work

- Verify a populated dashboard GET response and confirm that values shown in the UI match the API payload.
- Run the backend test suite, including analytics and alert tests.
- Add end-to-end or API integration coverage for dashboard loading, symbol switching, refresh, and API error states.

## Local development

1. Start the supporting services from the repository root:

   ```powershell
   docker compose -f docker/docker-compose.yml up -d db redis
   ```

2. Configure the backend environment variables and activate the backend virtual environment:

   ```powershell
   .\backend\.venv\Scripts\Activate.ps1
   ```

3. Start Django from the backend directory:

   ```powershell
   cd backend
   python manage.py runserver
   ```

4. Start the Flutter frontend from `tradingdash_frontend`:

   ```powershell
   flutter run -d chrome
   ```
