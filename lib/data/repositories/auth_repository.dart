import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/api_client.dart';
import '../local/auth_storage.dart';
import '../models/user_model.dart';

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(ref.watch(dioProvider), ref.watch(authStorageProvider));
});

class AuthRepository {
  AuthRepository(this._dio, this._storage);

  final Dio _dio;
  final AuthStorage _storage;

  Future<AuthSession> login(String email, String password) async {
    return apiCall(() async {
      final res = await _dio.post('/auth/login', data: {'email': email, 'password': password});
      final data = res.data['data'] as Map<String, dynamic>;
      final session = AuthSession.fromLoginData(data);
      await _storage.saveSession(
        accessToken: session.accessToken,
        refreshToken: session.refreshToken,
        user: session.user,
      );
      return session;
    });
  }

  Future<UserModel> register({
    required String email,
    required String username,
    required String password,
    String? firstName,
    String? lastName,
    String? phoneNumber,
  }) async {
    return apiCall(() async {
      final res = await _dio.post('/auth/register', data: {
        'email': email,
        'username': username,
        'password': password,
        if (firstName != null) 'first_name': firstName,
        if (lastName != null) 'last_name': lastName,
        if (phoneNumber != null) 'phone_number': phoneNumber,
      });
      return UserModel.fromJson(res.data['data'] as Map<String, dynamic>);
    });
  }

  Future<UserModel?> restoreSession() async {
    if (!await _storage.hasSession()) return null;
    try {
      final res = await _dio.get('/auth/me');
      return UserModel.fromJson(res.data['data'] as Map<String, dynamic>);
    } catch (_) {
      await _storage.clear();
      return null;
    }
  }

  Future<void> logout() => _storage.clear();
}
