import 'package:flutter/foundation.dart' show kIsWeb;

class ApiConstants {
  static String get baseUrl {
    if (kIsWeb) return 'http://127.0.0.1:8000';
    return 'http://10.0.2.2:8000';
  }

  static const String dashboardOverview = '/api/analytics/dashboard/overview/';
  static const String dashboardRefresh = '/api/analytics/dashboard/refresh/';
}
