TradingDash
===========

TradingDash is a trading analytics dashboard with a Django REST backend and a
Flutter frontend. It provides option-chain analytics, snapshot ingestion,
futures dashboard support, and market alerts.

Requirements
------------

- Python and pip
- Flutter SDK
- Docker with Docker Compose (for local PostgreSQL and Redis)

Start local services
--------------------

From the repository root:

    docker compose -f docker/docker-compose.yml up -d db redis

Configure backend/.env with the required settings for your environment. Keep
secrets in this ignored local file; do not commit credentials.

Start the backend
-----------------

From the repository root, install the backend dependencies and migrate:

    cd backend
    py -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver

Start the Flutter frontend
--------------------------

In another terminal:

    cd tradingdash_frontend
    flutter pub get
    flutter run -d chrome

NSE option snapshots
--------------------

When an NSE OPTIONS instrument is selected in the frontend, the app requests a
fresh option-chain snapshot from the backend and displays the returned
dashboard data. Supported index options are NIFTY, BANKNIFTY, FINNIFTY,
MIDCPNIFTY, and NIFTYNXT50. The 60-second dashboard polling reads stored data;
it does not fetch another snapshot.

The backend can also fetch a snapshot manually from the backend directory:

    .\.venv\Scripts\python.exe manage.py fetch_option_chain --symbol FINNIFTY

API and provider configuration details are in backend/README.md. The bundled
provider supports NSE option chains; MCX and futures data require a compatible
provider configured through MARKET_DATA_PROVIDERS.
