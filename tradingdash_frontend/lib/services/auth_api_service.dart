import 'package:dio/dio.dart';
import '../core/constants/api_constants.dart';
import '../core/network/dio_client.dart';
import '../models/user_model.dart';
import 'token_storage.dart';

class AuthApiService {
  final Dio _dio = DioClient.dio;

  Future<User> login({
    required String username,
    required String password,
  }) async {
    try {
      final response = await _dio.post(
        ApiConstants.login,
        data: {
          'username': username.trim(),
          'password': password,
        },
      );

      final access = response.data['access'] as String;
      final refresh = response.data['refresh'] as String;

      await TokenStorage.saveTokens(access: access, refresh: refresh);

      // Fetch the full user details and profile
      return await getCurrentUser();
    } on DioException catch (e) {
      final errorMsg = _extractErrorMessage(e);
      throw Exception(errorMsg);
    }
  }

  Future<User> register({
    required String username,
    required String email,
    required String password,
  }) async {
    try {
      final response = await _dio.post(
        ApiConstants.register,
        data: {
          'username': username.trim(),
          'email': email.trim(),
          'password': password,
          'password2': password,
        },
      );

      final access = response.data['access'] as String;
      final refresh = response.data['refresh'] as String;

      await TokenStorage.saveTokens(access: access, refresh: refresh);

      return User.fromJson(response.data['user'] as Map<String, dynamic>);
    } on DioException catch (e) {
      final errorMsg = _extractErrorMessage(e);
      throw Exception(errorMsg);
    }
  }

  Future<User> getCurrentUser() async {
    try {
      final response = await _dio.get(ApiConstants.me);
      return User.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      final errorMsg = _extractErrorMessage(e);
      throw Exception(errorMsg);
    }
  }

  Future<UserProfile> updateProfile(UserProfile profile) async {
    try {
      final response = await _dio.patch(
        ApiConstants.profile,
        data: profile.toJson(),
      );
      return UserProfile.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      final errorMsg = _extractErrorMessage(e);
      throw Exception(errorMsg);
    }
  }

  Future<void> logout() async {
    await TokenStorage.clearTokens();
  }

  String _extractErrorMessage(DioException e) {
    if (e.response?.data != null && e.response?.data is Map) {
      final data = e.response!.data as Map;
      if (data.containsKey('detail')) {
        return data['detail'].toString();
      }
      final firstKey = data.keys.first;
      final val = data[firstKey];
      if (val is List && val.isNotEmpty) {
        return '${firstKey.toString().toUpperCase()}: ${val.first}';
      }
      return data.toString();
    }
    return e.message ?? 'An unexpected network error occurred.';
  }
}
