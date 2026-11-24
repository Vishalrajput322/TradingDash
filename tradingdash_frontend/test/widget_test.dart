import 'package:flutter_test/flutter_test.dart';
import 'package:tradingdash_frontend/models/dashboard_overview.dart';

void main() {
  test('DashboardOverview parses backend payload', () {
    final data = DashboardOverview.fromJson({
      'symbol': 'NIFTY',
      'pcr': 1.25,
      'market_bias': 'BULLISH',
      'max_pain': 24500,
      'top_call_long_buildup': [
        {
          'strike_price': 24700,
          'oi_change': 1250,
          'buildup_type': 'CALL_BUYING',
        },
      ],
      'top_put_long_buildup': [
        {'strike_price': 24400, 'oi_change': 980, 'buildup_type': 'PUT_BUYING'},
      ],
      'snapshot_timestamp': '2026-11-24T14:56:38+05:30',
    });

    expect(data.symbol, 'NIFTY');
    expect(data.pcr, 1.25);
    expect(data.alertCount, 0);
    expect(data.topCallLongBuildup!.first['strike_price'], 24700);
    expect(data.snapshotTimestamp, '2026-11-24T14:56:38+05:30');
  });

  test('DashboardOverview parses futures payload', () {
    final data = DashboardOverview.fromJson({
      'symbol': 'GOLD',
      'exchange': 'MCX',
      'product': 'FUTURES',
      'last_price': 125025.5,
      'price_change': 25.5,
      'open_interest': 120,
      'oi_change': 20,
      'volume': 450,
      'expiry_date': '2027-01-05',
      'snapshot_timestamp': '2026-11-24T15:00:00+05:30',
    });

    expect(data.exchange, 'MCX');
    expect(data.product, 'FUTURES');
    expect(data.lastPrice, 125025.5);
    expect(data.priceChange, 25.5);
    expect(data.expiryDate, '2027-01-05');
  });
}
