import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user_model.dart';
import '../models/dashboard_model.dart';
import '../models/vehicle_model.dart';
import '../models/driver_model.dart';

class ApiService {
  final Dio _dio;
  static const String baseUrl = 'http://localhost:8001'; // Updated backend URL

  ApiService() : _dio = Dio(BaseOptions(
    baseUrl: baseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
  )) {
    _setupInterceptors();
  }

  void _setupInterceptors() {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        // Add JWT token to requests
        final token = _getStoredToken();
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onError: (error, handler) {
        if (error.response?.statusCode == 401) {
          // Handle token expiry - redirect to login
          _handleTokenExpiry();
        }
        handler.next(error);
      },
    ));
  }

  // Authentication APIs
  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await _dio.post('/auth/login', data: {
        'email': email,
        'password': password,
      });
      return response.data;
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    String? businessName,
  }) async {
    try {
      final response = await _dio.post('/auth/register', data: {
        'email': email,
        'password': password,
        'first_name': firstName,
        'last_name': lastName,
        'business_name': businessName,
      });
      return response.data;
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Dashboard APIs
  Future<DashboardStats> getDashboardStats() async {
    try {
      final response = await _dio.get('/dashboard/stats');
      return DashboardStats.fromJson(response.data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<List<RecentActivity>> getRecentActivity() async {
    try {
      final response = await _dio.get('/dashboard/activity');
      return (response.data['items'] as List)
          .map((item) => RecentActivity.fromJson(item))
          .toList();
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Vehicle APIs
  Future<List<VehicleModel>> getVehicles({
    String? status,
    int page = 1,
    int limit = 20,
  }) async {
    try {
      final response = await _dio.get('/vehicles/', queryParameters: {
        if (status != null) 'status': status,
        'page': page,
        'limit': limit,
      });
      return (response.data['items'] as List)
          .map((item) => VehicleModel.fromJson(item))
          .toList();
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<VehicleModel> createVehicle(Map<String, dynamic> vehicleData) async {
    try {
      final response = await _dio.post('/vehicles/', data: vehicleData);
      return VehicleModel.fromJson(response.data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<VehicleModel> updateVehicle(String vehicleId, Map<String, dynamic> updates) async {
    try {
      final response = await _dio.put('/vehicles/$vehicleId', data: updates);
      return VehicleModel.fromJson(response.data);
    } catch (e) {
      throw _handleError(e);
    }
  }
  // Driver APIs
  Future<List<DriverModel>> getDrivers({
    String? status,
    int page = 1,
    int limit = 20,
  }) async {
    try {
      final response = await _dio.get('/drivers/', queryParameters: {
        if (status != null) 'status': status,
        'page': page,
        'limit': limit,
      });
      return (response.data['items'] as List)
          .map((item) => DriverModel.fromJson(item))
          .toList();
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<DriverModel> createDriver(Map<String, dynamic> driverData) async {
    try {
      final response = await _dio.post('/drivers/', data: driverData);
      return DriverModel.fromJson(response.data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Live Tracking APIs
  Future<List<Map<String, dynamic>>> getVehicleLocations() async {
    try {
      final response = await _dio.get('/vehicles/locations');
      return List<Map<String, dynamic>>.from(response.data['vehicles']);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Maintenance APIs
  Future<Map<String, dynamic>> getMaintenanceDashboard() async {
    try {
      final response = await _dio.get('/maintenance/dashboard');
      return response.data;
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<List<Map<String, dynamic>>> getUpcomingMaintenance() async {
    try {
      final response = await _dio.get('/maintenance/upcoming');
      return List<Map<String, dynamic>>.from(response.data['items']);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Fuel APIs
  Future<Map<String, dynamic>> getFuelDashboard() async {
    try {
      final response = await _dio.get('/fuel/dashboard');
      return response.data;
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<List<Map<String, dynamic>>> getFuelLogs({
    String? vehicleId,
    String? driverId,
    int page = 1,
    int limit = 20,
  }) async {
    try {
      final response = await _dio.get('/fuel/', queryParameters: {
        if (vehicleId != null) 'vehicle_id': vehicleId,
        if (driverId != null) 'driver_id': driverId,
        'page': page,
        'limit': limit,
      });
      return List<Map<String, dynamic>>.from(response.data['items']);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Alerts APIs
  Future<List<Map<String, dynamic>>> getAlerts() async {
    try {
      final response = await _dio.get('/dashboard/alerts');
      return List<Map<String, dynamic>>.from(response.data['alerts']);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Helper methods
  String? _getStoredToken() {
    // Implement token retrieval from secure storage
    // This will be connected to your auth provider
    return null;
  }

  void _handleTokenExpiry() {
    // Implement logout and redirect to login
    // This will be connected to your auth provider
  }

  Exception _handleError(dynamic error) {
    if (error is DioException) {
      switch (error.type) {
        case DioExceptionType.connectionTimeout:
        case DioExceptionType.sendTimeout:
        case DioExceptionType.receiveTimeout:
          return Exception('Connection timeout. Please check your internet connection.');
        case DioExceptionType.badResponse:
          final statusCode = error.response?.statusCode;
          final message = error.response?.data?['detail'] ?? 'Server error occurred';
          return Exception('Error $statusCode: $message');
        case DioExceptionType.cancel:
          return Exception('Request was cancelled');
        case DioExceptionType.unknown:
          return Exception('Network error occurred');
        default:
          return Exception('Unexpected error occurred');
      }
    }
    return Exception('Unknown error: $error');
  }
}

// Provider for API service
final apiServiceProvider = Provider<ApiService>((ref) {
  return ApiService();
});