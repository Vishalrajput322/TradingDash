import time
from typing import Optional

import requests


class NSEClient:
    BASE_URL = "https://www.nseindia.com"
    HOME_URL = f"{BASE_URL}/option-chain"

    CONTRACT_INFO_URL = (
        f"{BASE_URL}/api/option-chain-contract-info"
    )

    CHAIN_URL = (
        f"{BASE_URL}/api/option-chain-v3"
    )

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Referer": HOME_URL,
        "Connection": "keep-alive",
    }

    def __init__(self):
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """
        Create session and load NSE cookies.
        """

        session = requests.Session()
        session.headers.update(self.HEADERS)

        session.get(
            self.BASE_URL,
            timeout=10,
        )

        session.get(
            self.HOME_URL,
            timeout=10,
        )

        return session

    def _get_json(
        self,
        url: str,
        params: dict,
    ) -> dict:
        """
        Perform GET request and return JSON.
        """

        response = self.session.get(
            url,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    def _get_nearest_expiry(
        self,
        symbol: str,
    ) -> str:
        """
        Fetch nearest expiry date from NSE.
        """

        data = self._get_json(
            self.CONTRACT_INFO_URL,
            {"symbol": symbol},
        )

        expiry_dates = data.get("expiryDates", [])

        if not expiry_dates:
            raise ValueError(
                f"No expiry dates found for {symbol}"
            )

        return expiry_dates[0]

    def option_chain(
        self,
        symbol: str = "NIFTY",
        expiry: Optional[str] = None,
        retries: int = 3,
    ) -> tuple[dict, str]:
        """
        Fetch option chain data.

        Returns:
            (data, expiry)
        """

        symbol = symbol.upper()

        last_error = None

        for attempt in range(1, retries + 1):

            try:

                if expiry is None:
                    selected_expiry = (
                        self._get_nearest_expiry(symbol)
                    )
                else:
                    selected_expiry = expiry

                data = self._get_json(
                    self.CHAIN_URL,
                    {
                        "type": "Indices",
                        "symbol": symbol,
                        "expiry": selected_expiry,
                    },
                )

                if not data:
                    raise ValueError(
                        "Received empty response from NSE"
                    )

                return data, selected_expiry

            except Exception as exc:

                last_error = exc

                print(
                    f"Attempt {attempt}/{retries} failed: {exc}"
                )

                if attempt < retries:
                    time.sleep(attempt * 2)

        raise RuntimeError(
            f"Failed to fetch option chain for "
            f"{symbol} after {retries} retries"
        ) from last_error