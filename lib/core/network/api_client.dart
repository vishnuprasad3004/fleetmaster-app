import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../constants.dart';
import '../../data/local/auth_storage.dart';
import 'api_exception.dart';

final dioProvider = Provider<Dio>((ref) {
  final storage = ref.watch(authStorageProvider);
  final dio = Dio(
    BaseOptions(
      baseUrl: '$apiBaseUrl$apiVersion',
      connectTimeout: const Duration(milliseconds: connectTimeout),
      receiveTimeout: const Duration(milliseconds: receiveTimeout),
      headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
    ),
  );

  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await storage.getAccessToken();
        if (token != null && token.isNotEmpty) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onError: (error, handler) async {
        final response = error.response;
        if (response?.statusCode == 401) {
          await storage.clear();
        }
        handler.next(error);
      },
    ),
  );

  return dio;
});

extension DioErrorX on DioException {
  ApiException toApiException() {
    final data = response?.data;
    String message = 'Something went wrong';
    if (data is Map) {
      message = (data['detail'] ?? data['message'] ?? message).toString();
    } else if (type == DioExceptionType.connectionError) {
      message = 'Cannot reach server. Is the backend running on $apiBaseUrl?';
    }
    return ApiException(message, statusCode: response?.statusCode);
  }
}

Future<T> apiCall<T>(Future<T> Function() fn) async {
  try {
    return await fn();
  } on DioException catch (e) {
    throw e.toApiException();
  }
}
