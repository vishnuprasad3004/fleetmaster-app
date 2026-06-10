import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/api_client.dart';
import '../models/dashboard_model.dart';

final dashboardRepositoryProvider = Provider<DashboardRepository>((ref) {
  return DashboardRepository(ref.watch(dioProvider));
});

class DashboardRepository {
  DashboardRepository(this._dio);

  final Dio _dio;

  Future<DashboardStats> getStats() async {
    return apiCall(() async {
      final res = await _dio.get('/dashboard/stats');
      return DashboardStats.fromJson(res.data as Map<String, dynamic>);
    });
  }

  Future<List<AlertModel>> getAlerts() async {
    return apiCall(() async {
      final res = await _dio.get('/dashboard/alerts');
      final list = res.data as List<dynamic>;
      return list.map((e) => AlertModel.fromJson(e as Map<String, dynamic>)).toList();
    });
  }

  Future<List<ActivityModel>> getRecentActivity() async {
    return apiCall(() async {
      final res = await _dio.get('/dashboard/recent-activity');
      final list = res.data as List<dynamic>;
      return list.map((e) => ActivityModel.fromJson(e as Map<String, dynamic>)).toList();
    });
  }
}
