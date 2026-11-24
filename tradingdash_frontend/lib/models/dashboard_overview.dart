import 'package:json_annotation/json_annotation.dart';

part 'dashboard_overview.g.dart';

@JsonSerializable()
class DashboardOverview {
  final String symbol;
  @JsonKey(defaultValue: 'NSE')
  final String exchange;

  @JsonKey(defaultValue: 'OPTIONS')
  final String product;

  final double? pcr;

  @JsonKey(name: 'market_bias', defaultValue: 'NEUTRAL')
  final String marketBias;

  @JsonKey(name: 'max_pain', defaultValue: 0.0)
  final double? maxPain;

  @JsonKey(name: 'last_price')
  final double? lastPrice;

  @JsonKey(name: 'price_change')
  final double? priceChange;

  @JsonKey(name: 'open_interest')
  final int? openInterest;

  @JsonKey(name: 'oi_change')
  final int? oiChange;

  final int? volume;

  @JsonKey(name: 'expiry_date')
  final String? expiryDate;

  @JsonKey(name: 'alert_count', defaultValue: 0)
  final int alertCount;

  @JsonKey(name: 'top_call_buildup')
  final Map<String, dynamic>? topCallBuildup;

  @JsonKey(name: 'top_put_buildup')
  final Map<String, dynamic>? topPutBuildup;

  @JsonKey(name: 'top_call_long_buildup')
  final List<Map<String, dynamic>>? topCallLongBuildup;

  @JsonKey(name: 'top_put_long_buildup')
  final List<Map<String, dynamic>>? topPutLongBuildup;

  @JsonKey(name: 'last_updated')
  final String? lastUpdated;

  @JsonKey(name: 'snapshot_timestamp')
  final String? snapshotTimestamp;

  DashboardOverview({
    required this.symbol,
    this.exchange = 'NSE',
    this.product = 'OPTIONS',
    this.pcr,
    required this.marketBias,
    required this.maxPain,
    this.alertCount = 0,
    this.topCallBuildup,
    this.topPutBuildup,
    this.topCallLongBuildup,
    this.topPutLongBuildup,
    this.lastUpdated,
    this.snapshotTimestamp,
    this.lastPrice,
    this.priceChange,
    this.openInterest,
    this.oiChange,
    this.volume,
    this.expiryDate,
  });

  factory DashboardOverview.fromJson(Map<String, dynamic> json) =>
      _$DashboardOverviewFromJson(json);

  Map<String, dynamic> toJson() => _$DashboardOverviewToJson(this);
}
