import 'package:dio/dio.dart';
import '../core/constants/api_constants.dart';
import '../core/network/dio_client.dart';
import '../models/dashboard_overview.dart';

class AnalyticsApiService {
  final Dio _dio = DioClient.dio;

  Future<DashboardOverview> getDashboard({
    String symbol = 'NIFTY',
    String exchange = 'NSE',
    String product = 'OPTIONS',
  }) async {
    final response = await _dio.get(
      ApiConstants.dashboardOverview,
      queryParameters: {
        'symbol': symbol,
        'exchange': exchange,
        'product': product,
      },
    );
    return DashboardOverview.fromJson(response.data as Map<String, dynamic>);
  }

  Future<DashboardOverview> refreshOptionsDashboard({
    required String symbol,
  }) async {
    final response = await _dio.post(
      ApiConstants.dashboardRefresh,
      data: {'symbol': symbol},
      options: Options(receiveTimeout: const Duration(seconds: 60)),
    );
    return DashboardOverview.fromJson(response.data as Map<String, dynamic>);
  }
}
