from django.test import TestCase
from unittest.mock import patch

from market_data.services.nse_service import NSEClient
from market_data.services.providers import parse_expiry_date


class NSEClientTests(TestCase):
    def test_equity_option_chain_uses_equities_contract_type(self):
        client = object.__new__(NSEClient)
        with (
            patch.object(client, "_get_nearest_expiry", return_value="05-Jan-2027"),
            patch.object(
                client,
                "_get_json",
                side_effect=[
                    {"expiryDates": ["05-Jan-2027"]},
                    {"records": {"data": []}},
                ],
            ) as get_json,
        ):
            client.option_chain("RELIANCE", asset_class="EQUITY")

        self.assertEqual(get_json.call_args_list[-1].args[1]["type"], "Equities")

    def test_nse_provider_rejects_commodity_option_chains(self):
        client = object.__new__(NSEClient)

        with self.assertRaisesRegex(ValueError, "do not support asset class"):
            client.option_chain("GOLD", asset_class="COMMODITY")

    def test_expiry_parser_accepts_iso_dates_from_external_providers(self):
        self.assertEqual(
            parse_expiry_date("2027-01-05").isoformat(),
            "2027-01-05",
        )