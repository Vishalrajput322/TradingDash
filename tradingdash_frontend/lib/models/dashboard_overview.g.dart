// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'dashboard_overview.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

DashboardOverview _$DashboardOverviewFromJson(Map<String, dynamic> json) =>
    DashboardOverview(
      symbol: json['symbol'] as String,
      exchange: json['exchange'] as String? ?? 'NSE',
      product: json['product'] as String? ?? 'OPTIONS',
      pcr: (json['pcr'] as num?)?.toDouble(),
      marketBias: json['market_bias'] as String? ?? 'NEUTRAL',
      maxPain: (json['max_pain'] as num?)?.toDouble() ?? 0.0,
      alertCount: (json['alert_count'] as num?)?.toInt() ?? 0,
      topCallBuildup: json['top_call_buildup'] as Map<String, dynamic>?,
      topPutBuildup: json['top_put_buildup'] as Map<String, dynamic>?,
      topCallLongBuildup: (json['top_call_long_buildup'] as List<dynamic>?)
          ?.map((e) => e as Map<String, dynamic>)
          .toList(),
      topPutLongBuildup: (json['top_put_long_buildup'] as List<dynamic>?)
          ?.map((e) => e as Map<String, dynamic>)
          .toList(),
      lastUpdated: json['last_updated'] as String?,
      snapshotTimestamp: json['snapshot_timestamp'] as String?,
      lastPrice: (json['last_price'] as num?)?.toDouble(),
      priceChange: (json['price_change'] as num?)?.toDouble(),
      openInterest: (json['open_interest'] as num?)?.toInt(),
      oiChange: (json['oi_change'] as num?)?.toInt(),
      volume: (json['volume'] as num?)?.toInt(),
      expiryDate: json['expiry_date'] as String?,
    );

Map<String, dynamic> _$DashboardOverviewToJson(DashboardOverview instance) =>
    <String, dynamic>{
      'symbol': instance.symbol,
      'exchange': instance.exchange,
      'product': instance.product,
      'pcr': instance.pcr,
      'market_bias': instance.marketBias,
      'max_pain': instance.maxPain,
      'last_price': instance.lastPrice,
      'price_change': instance.priceChange,
      'open_interest': instance.openInterest,
      'oi_change': instance.oiChange,
      'volume': instance.volume,
      'expiry_date': instance.expiryDate,
      'alert_count': instance.alertCount,
      'top_call_buildup': instance.topCallBuildup,
      'top_put_buildup': instance.topPutBuildup,
      'top_call_long_buildup': instance.topCallLongBuildup,
      'top_put_long_buildup': instance.topPutLongBuildup,
      'last_updated': instance.lastUpdated,
      'snapshot_timestamp': instance.snapshotTimestamp,
    };
