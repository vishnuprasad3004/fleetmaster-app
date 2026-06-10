import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/api_client.dart';
import '../models/maintenance_model.dart';

final maintenanceRepositoryProvider = Provider<MaintenanceRepository>((ref) {
  return MaintenanceRepository(ref.watch(dioProvider));
});

class MaintenanceRepository {
  MaintenanceRepository(this._dio);

  final Dio _dio;

  Future<MaintenanceDashboardModel> getDashboard() async {
    return apiCall(() async {
      final res = await _dio.get('/maintenance/dashboard');
      return MaintenanceDashboardModel.fromJson(res.data);
    });
  }

  Future<List<MaintenanceRecordModel>> getRecords() async {
    return apiCall(() async {
      final res = await _dio.get('/maintenance/records');
      final records = res.data['records'] as List<dynamic>;
      return records.map((e) => MaintenanceRecordModel.fromJson(e as Map<String, dynamic>)).toList();
    });
  }

  Future<List<MaintenanceRecordModel>> getVehicleRecords(String vehicleId) async {
    return apiCall(() async {
      final res = await _dio.get('/maintenance/vehicle/$vehicleId');
      final records = res.data['records'] as List<dynamic>;
      return records.map((e) => MaintenanceRecordModel.fromJson(e as Map<String, dynamic>)).toList();
    });
  }

  Future<List<MaintenanceRecordModel>> getUpcomingServices() async {
    return apiCall(() async {
      final res = await _dio.get('/maintenance/upcoming');
      final records = res.data['records'] as List<dynamic>;
      return records.map((e) => MaintenanceRecordModel.fromJson(e as Map<String, dynamic>)).toList();
    });
  }

  Future<List<MaintenanceRecordModel>> getServiceRecords() async {
    return apiCall(() async {
      final res = await _dio.get('/maintenance/records', queryParameters: {'type': 'service'});
      final records = res.data['records'] as List<dynamic>;
      return records.map((e) => MaintenanceRecordModel.fromJson(e as Map<String, dynamic>)).toList();
    });
  }

  Future<List<MaintenanceRecordModel>> getRepairRecords() async {
    return apiCall(() async {
      final res = await _dio.get('/maintenance/records', queryParameters: {'type': 'repair'});
      final records = res.data['records'] as List<dynamic>;
      return records.map((e) => MaintenanceRecordModel.fromJson(e as Map<String, dynamic>)).toList();
    });
  }

  Future<MaintenanceRecordModel> createRecord(MaintenanceRecordModel record) async {
    return apiCall(() async {
      final res = await _dio.post('/maintenance/records', data: record.toJson());
      return MaintenanceRecordModel.fromJson(res.data);
    });
  }

  Future<MaintenanceRecordModel> updateRecord(String id, MaintenanceRecordModel record) async {
    return apiCall(() async {
      final res = await _dio.put('/maintenance/records/$id', data: record.toJson());
      return MaintenanceRecordModel.fromJson(res.data);
    });
  }

  Future<void> deleteRecord(String id) async {
    return apiCall(() async {
      await _dio.delete('/maintenance/records/$id');
    });
  }
}
