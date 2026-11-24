import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/dashboard_overview.dart';
import '../services/analytics_api_service.dart';

final analyticsServiceProvider = Provider<AnalyticsApiService>((ref) {
  return AnalyticsApiService();
});

const Map<String, List<String>> symbolsByExchange = {
  'NSE': ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'NIFTYNXT50'],
  'MCX': [
    'GOLD',
    'GOLDM',
    'SILVER',
    'SILVERM',
    'CRUDEOIL',
    'NATURALGAS',
    'COPPER',
  ],
};

class DashboardSelection {
  final String exchange;
  final String product;
  final String symbol;

  const DashboardSelection({
    this.exchange = 'NSE',
    this.product = 'OPTIONS',
    this.symbol = 'NIFTY',
  });
}

class DashboardSelectionNotifier extends Notifier<DashboardSelection> {
  @override
  DashboardSelection build() => const DashboardSelection();

  void setExchange(String exchange) {
    state = DashboardSelection(
      exchange: exchange,
      product: state.product,
      symbol: symbolsByExchange[exchange]!.first,
    );
  }

  void setProduct(String product) {
    state = DashboardSelection(
      exchange: state.exchange,
      product: product,
      symbol: state.symbol,
    );
  }

  void setSymbol(String symbol) {
    state = DashboardSelection(
      exchange: state.exchange,
      product: state.product,
      symbol: symbol,
    );
  }
}

final dashboardSelectionProvider =
    NotifierProvider<DashboardSelectionNotifier, DashboardSelection>(
      DashboardSelectionNotifier.new,
    );

final dashboardProvider =
    AsyncNotifierProvider<DashboardNotifier, DashboardOverview>(
      DashboardNotifier.new,
    );

class DashboardNotifier extends AsyncNotifier<DashboardOverview> {
  Timer? _pollingTimer;

  @override
  Future<DashboardOverview> build() async {
    final selection = ref.watch(dashboardSelectionProvider);

    _pollingTimer?.cancel();
    _pollingTimer = Timer.periodic(const Duration(seconds: 60), (_) {
      refreshSilently();
    });

    ref.onDispose(() => _pollingTimer?.cancel());

    final analyticsService = ref.read(analyticsServiceProvider);
    if (selection.exchange == 'NSE' && selection.product == 'OPTIONS') {
      return analyticsService.refreshOptionsDashboard(symbol: selection.symbol);
    }

    return analyticsService.getDashboard(
      symbol: selection.symbol,
      exchange: selection.exchange,
      product: selection.product,
    );
  }

  Future<void> refreshSilently() async {
    final selection = ref.read(dashboardSelectionProvider);
    try {
      final freshData = await ref
          .read(analyticsServiceProvider)
          .getDashboard(
            symbol: selection.symbol,
            exchange: selection.exchange,
            product: selection.product,
          );
      if (!ref.mounted) return;
      state = AsyncData(freshData);
    } catch (e, st) {
      if (!ref.mounted) return;
      if (!state.hasValue) {
        state = AsyncError(e, st);
      }
    }
  }
}
