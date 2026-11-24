import 'package:dio/dio.dart';
import '../constants/api_constants.dart';
import '../../services/token_storage.dart';

class DioClient {
  static final Dio dio = _createDio();

  static Dio _createDio() {
    final client = Dio(
      BaseOptions(
        baseUrl: ApiConstants.baseUrl,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 10),
        headers: {'Accept': 'application/json'},
      ),
    );

    client.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await TokenStorage.getAccessToken();
          if (token != null && token.isNotEmpty) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (DioException err, handler) async {
          // Attempt automatic token refresh on 401 Unauthorized
          if (err.response?.statusCode == 401 &&
              err.requestOptions.extra['isRetry'] != true &&
              !err.requestOptions.path.contains('/api/auth/')) {
            final refreshToken = await TokenStorage.getRefreshToken();
            if (refreshToken != null && refreshToken.isNotEmpty) {
              try {
                final refreshClient = Dio(
                  BaseOptions(
                    baseUrl: ApiConstants.baseUrl,
                    connectTimeout: const Duration(seconds: 10),
                    receiveTimeout: const Duration(seconds: 10),
                  ),
                );

                final response = await refreshClient.post(
                  ApiConstants.tokenRefresh,
                  data: {'refresh': refreshToken},
                );

                if (response.statusCode == 200) {
                  final newAccess = response.data['access'] as String;
                  final newRefresh =
                      (response.data['refresh'] as String?) ?? refreshToken;

                  await TokenStorage.saveTokens(
                    access: newAccess,
                    refresh: newRefresh,
                  );

                  // Retry the original request with the new access token
                  final retryOptions = err.requestOptions;
                  retryOptions.headers['Authorization'] = 'Bearer $newAccess';
                  retryOptions.extra['isRetry'] = true;

                  final retryResponse = await client.fetch(retryOptions);
                  return handler.resolve(retryResponse);
                }
              } catch (_) {
                await TokenStorage.clearTokens();
              }
            }
          }
          return handler.next(err);
        },
      ),
    );

    return client;
  }
}
