import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/app_theme.dart';
import '../../models/dashboard_overview.dart';
import '../../providers/dashboard_provider.dart';
import '../../widgets/metric_card.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  Color _biasColor(String bias) {
    switch (bias.toUpperCase()) {
      case 'BULLISH':
        return AppTheme.bullish;
      case 'BEARISH':
        return AppTheme.bearish;
      default:
        return AppTheme.neutral;
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selection = ref.watch(dashboardSelectionProvider);
    final dashboardAsync = ref.watch(dashboardProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'TradingDash',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.invalidate(dashboardProvider),
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
            child: Wrap(
              spacing: 16,
              runSpacing: 8,
              children: [
                _selector<String>(
                  label: 'Exchange',
                  value: selection.exchange,
                  values: const ['NSE', 'MCX'],
                  onChanged: (value) => ref
                      .read(dashboardSelectionProvider.notifier)
                      .setExchange(value),
                ),
                _selector<String>(
                  label: 'Product',
                  value: selection.product,
                  values: const ['OPTIONS', 'FUTURES'],
                  onChanged: (value) => ref
                      .read(dashboardSelectionProvider.notifier)
                      .setProduct(value),
                ),
                _selector<String>(
                  label: 'Instrument',
                  value: selection.symbol,
                  values: symbolsByExchange[selection.exchange]!,
                  onChanged: (value) => ref
                      .read(dashboardSelectionProvider.notifier)
                      .setSymbol(value),
                ),
              ],
            ),
          ),
          Expanded(
            child: dashboardAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (err, _) => Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(
                        Icons.wifi_off,
                        size: 48,
                        color: AppTheme.bearish,
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'Failed to load ${selection.exchange} '
                        '${selection.product.toLowerCase()} data\n$err',
                        textAlign: TextAlign.center,
                        style: const TextStyle(color: Colors.white70),
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: () => ref.invalidate(dashboardProvider),
                        child: const Text('Retry'),
                      ),
                    ],
                  ),
                ),
              ),
              data: (data) => _buildContent(context, ref, data),
            ),
          ),
        ],
      ),
    );
  }

  Widget _selector<T extends String>({
    required String label,
    required T value,
    required List<T> values,
    required ValueChanged<T> onChanged,
  }) {
    return SizedBox(
      width: 170,
      child: DropdownButtonFormField<T>(
        initialValue: value,
        decoration: InputDecoration(
          labelText: label,
          isDense: true,
          filled: true,
          fillColor: AppTheme.surface,
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
        ),
        dropdownColor: AppTheme.surface,
        items: values
            .map((item) => DropdownMenuItem(value: item, child: Text(item)))
            .toList(),
        onChanged: (selected) {
          if (selected != null) onChanged(selected);
        },
      ),
    );
  }

  Widget _buildContent(
    BuildContext context,
    WidgetRef ref,
    DashboardOverview data,
  ) {
    final pcrColor = (data.pcr ?? 0) >= 1.0
        ? AppTheme.bullish
        : AppTheme.bearish;
    final biasColor = _biasColor(data.marketBias);
    final isFutures = data.product == 'FUTURES';
    final metricCards = isFutures
        ? [
            MetricCard(
              title: 'Last Price',
              value: data.lastPrice?.toStringAsFixed(2) ?? '--',
              badgeText: data.expiryDate ?? 'Futures',
              accentColor: const Color(0xFF3B82F6),
              icon: Icons.price_change,
            ),
            MetricCard(
              title: 'Price Change',
              value: data.priceChange?.toStringAsFixed(2) ?? '--',
              badgeText: 'Since previous snapshot',
              accentColor: (data.priceChange ?? 0) >= 0
                  ? AppTheme.bullish
                  : AppTheme.bearish,
              icon: Icons.show_chart,
            ),
            MetricCard(
              title: 'Open Interest',
              value: data.openInterest?.toString() ?? '--',
              badgeText: 'Change: ${data.oiChange ?? '--'}',
              accentColor: AppTheme.neutral,
              icon: Icons.bar_chart,
            ),
            MetricCard(
              title: 'Volume',
              value: data.volume?.toString() ?? '--',
              badgeText: data.exchange,
              accentColor: AppTheme.neutral,
              icon: Icons.swap_vert,
            ),
          ]
        : [
            MetricCard(
              title: 'PCR (Put-Call Ratio)',
              value: data.pcr?.toStringAsFixed(2) ?? '--',
              badgeText: data.pcr == null
                  ? 'No data'
                  : (data.pcr! >= 1.0 ? 'Bullish' : 'Bearish'),
              accentColor: pcrColor,
              icon: Icons.balance,
            ),
            MetricCard(
              title: 'Market Bias',
              value: data.marketBias.toUpperCase(),
              badgeText: 'Live Signal',
              accentColor: biasColor,
              icon: Icons.trending_up,
            ),
            MetricCard(
              title: 'Max Pain',
              value: data.maxPain?.toStringAsFixed(0) ?? '--',
              badgeText: '${data.symbol} Strike',
              accentColor: const Color(0xFF3B82F6),
              icon: Icons.gps_fixed,
            ),
            MetricCard(
              title: 'Active Alerts',
              value: '${data.alertCount}',
              badgeText: 'Last 1m Cycle',
              accentColor: AppTheme.neutral,
              icon: Icons.notifications_active,
            ),
          ];

    return RefreshIndicator(
      onRefresh: () => ref.read(dashboardProvider.notifier).refreshSilently(),
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          LayoutBuilder(
            builder: (context, constraints) {
              final crossAxisCount = constraints.maxWidth >= 900 ? 4 : 2;
              final cardRatio = constraints.maxWidth >= 900 ? 1.5 : 1.15;
              return GridView.count(
                crossAxisCount: crossAxisCount,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                mainAxisSpacing: 12,
                crossAxisSpacing: 12,
                childAspectRatio: cardRatio,
                children: metricCards,
              );
            },
          ),
          const SizedBox(height: 16),
          if (!isFutures) ...[
            _buildupTile(
              title: 'Top Call Build-up (Resistance)',
              buildup:
                  data.topCallBuildup ??
                  (data.topCallLongBuildup?.isNotEmpty == true
                      ? data.topCallLongBuildup!.first
                      : null),
              accent: AppTheme.bearish,
            ),
            const SizedBox(height: 12),
            _buildupTile(
              title: 'Top Put Build-up (Support)',
              buildup:
                  data.topPutBuildup ??
                  (data.topPutLongBuildup?.isNotEmpty == true
                      ? data.topPutLongBuildup!.first
                      : null),
              accent: AppTheme.bullish,
            ),
          ],
          const SizedBox(height: 20),
          Center(
            child: Text(
              '${data.exchange} ${data.product} ${data.symbol} • '
              'Last Updated: ${data.lastUpdated ?? data.snapshotTimestamp ?? 'Just now'} '
              '• Auto-refreshes every 60s',
              style: const TextStyle(color: Colors.white38, fontSize: 12),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildupTile({
    required String title,
    required Map<String, dynamic>? buildup,
    required Color accent,
  }) {
    final strike = buildup?['strike_price'] ?? buildup?['strike'] ?? '--';
    final oiChange = buildup?['oi_change'] ?? buildup?['change_in_oi'] ?? '--';
    final label = buildup?['buildup_type'] ?? buildup?['status'] ?? 'No data';

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppTheme.border),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(color: Colors.white60, fontSize: 12),
              ),
              const SizedBox(height: 6),
              Text(
                'Strike: $strike',
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                'OI Change: $oiChange',
                style: const TextStyle(color: Colors.white70, fontSize: 13),
              ),
            ],
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            decoration: BoxDecoration(
              color: accent.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              '$label',
              style: TextStyle(
                color: accent,
                fontWeight: FontWeight.bold,
                fontSize: 12,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
