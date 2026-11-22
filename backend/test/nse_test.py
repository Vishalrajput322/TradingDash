import time
import requests
import pandas as pd

BASE_URL = "https://www.nseindia.com"
HOME_URL = BASE_URL + "/option-chain"
CONTRACT_INFO_URL = BASE_URL + "/api/option-chain-contract-info"
CHAIN_URL = BASE_URL + "/api/option-chain-v3"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",  # no 'br' unless brotli is installed
    "Referer": HOME_URL,
    "Connection": "keep-alive",
}


def create_session() -> requests.Session:
    """Create a session with NSE cookies by visiting the website first."""
    session = requests.Session()
    session.headers.update(HEADERS)
    session.get(BASE_URL, timeout=10)
    session.get(HOME_URL, timeout=10)
    return session


def get_json(session: requests.Session, url: str, params: dict) -> dict:
    response = session.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_option_chain(symbol: str = "NIFTY", expiry: str | None = None,
                       retries: int = 3) -> tuple[dict, str]:
    """Return (raw v3 JSON, expiry used)."""
    symbol = symbol.upper()
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            session = create_session()

            # Step 1: get available expiries
            if expiry is None:
                info = get_json(session, CONTRACT_INFO_URL, {"symbol": symbol})
                expiry = info["expiryDates"][0]  # nearest expiry

            # Step 2: get the option chain for that expiry
            data = get_json(
                session,
                CHAIN_URL,
                {"type": "Indices", "symbol": symbol, "expiry": expiry},
            )
            if data:
                return data, expiry
            last_error = ValueError("Empty response from NSE")
        except (requests.RequestException, ValueError, KeyError, IndexError) as e:
            last_error = e

        print(f"Attempt {attempt} failed: {last_error}. Retrying...")
        time.sleep(2 * attempt)

    raise RuntimeError(f"Could not fetch option chain for {symbol}: {last_error}")


def parse_option_chain(data: dict) -> tuple[float, pd.DataFrame]:
    records = data.get("records")
    if not records:
        raise RuntimeError(f"Unexpected response layout. Top-level keys: {list(data.keys())}")

    spot = records["underlyingValue"]
    rows = [
        {
            "Strike": item["strikePrice"],
            "CE_LTP": (item.get("CE") or {}).get("lastPrice"),
            "PE_LTP": (item.get("PE") or {}).get("lastPrice"),
        }
        for item in records["data"]
    ]
    df = pd.DataFrame(rows).sort_values("Strike").reset_index(drop=True)
    return spot, df


def main(symbol: str = "NIFTY"):
    data, expiry = fetch_option_chain(symbol)
    spot, df = parse_option_chain(data)

    print(f"Symbol : {symbol.upper()}")
    print(f"Expiry : {expiry}")
    print(f"Spot   : {spot}\n")
    print(df.head(10).to_string())


if __name__ == "__main__":
    main("NIFTY")