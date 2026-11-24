# Backend market data

The backend stores option-chain snapshots for NSE/MCX instruments and futures
quotes in a separate futures snapshot table. Instruments are classified by
exchange (`NSE` or `MCX`) and asset class (`INDEX`, `EQUITY`, or `COMMODITY`).
Existing instruments default to NSE index classification; set the correct
classification when registering stock or commodity instruments in Django admin.

## Configuring market data providers

Set `MARKET_DATA_PROVIDERS` to a JSON object mapping exchange codes to Python
import paths. The default configuration uses the existing NSE option-chain
client:

```text
MARKET_DATA_PROVIDERS={"NSE":"market_data.services.nse_service.NSEClient","MCX":"your_provider.MCXClient"}
```

Provider classes must implement:

- `option_chain(symbol, expiry=None, asset_class="INDEX")`, returning
  `(payload, expiry_string)` with the expiry in `DD-Mon-YYYY` or `YYYY-MM-DD`.
  The payload must use the normalized
  `records.data` option-chain shape consumed by `SnapshotService`.
- `futures_quote(symbol, expiry=None)`, returning a mapping with `expiry_date`
  (`YYYY-MM-DD`), `last_price`, and optional integer fields `open_interest`,
  `oi_change`, and `volume`. An optional ISO-8601 `timestamp` is also accepted.

The bundled NSE client currently fetches option chains only. No MCX adapter or
futures quote feed is bundled; those integrations require a compatible provider
and its credentials/configuration.

## Snapshot commands

Run these from the backend directory after configuring the database and
provider:

```powershell
python manage.py fetch_option_chain --symbol NIFTY
python manage.py fetch_futures_quote --symbol GOLD --expiry 2027-01-05
```

The instrument must already exist and be active. Select the exchange and asset
class on its admin record before fetching data.

The dashboard endpoint accepts `symbol`, `exchange` (`NSE` or `MCX`), and
`product` (`OPTIONS` or `FUTURES`) query parameters. For example:

```text
/api/analytics/dashboard/overview/?symbol=GOLD&exchange=MCX&product=FUTURES
```

When an NSE index is selected for OPTIONS in the Flutter dashboard, it posts
the selected symbol to `/api/analytics/dashboard/refresh/`. The backend fetches
the latest option chain, saves a snapshot, and returns fresh dashboard data.
Supported NSE index symbols are NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, and
NIFTYNXT50. This fetch is on demand; the 60-second dashboard polling does not
fetch a new option chain.
