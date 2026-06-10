import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/api_client.dart';
import '../models/fuel_model.dart';

final fuelRepositoryProvider = Provider<FuelRepository>((ref) {
  return FuelRepository(ref.watch(dioProvider));
});

class FuelRepository {
  FuelRepository(this._dio);

  final Dio _dio;

  Future<FuelDashboardModel> getDashboard() async {
    return apiCall(() async {
      final res = await _dio.get('/fuel/dashboard');
      return FuelDashboardModel.fromJson(res.data);
    });
  }

  Future<List<FuelLogModel>> getFuelLogs() async {
    return apiCall(() async {
      final res = await _dio.get('/fuel/logs');
      final logs = res.data['logs'] as List<dynamic>;
      return logs.map((e) => FuelLogModel.fromJson(e as Map<String, dynamic>)).toList();
    });
  }

  Future<List<FuelLogModel>> getVehicleFuelLogs(String vehicleId) async {
    return apiCall(() async {
      final res = await _dio.get('/fuel/vehicle/$vehicleId');
      final logs = res.data['logs'] as List<dynamic>;
      return logs.map((e) => FuelLogModel.fromJson(e as Map<String, dynamic>)).toList();
    });
  }

  Future<VehicleFuelAnalyticsModel> getVehicleAnalytics(String vehicleId) async {
    return apiCall(() async {
      final res = await _dio.get('/fuel/vehicle/$vehicleId/analytics');
      return VehicleFuelAnalyticsModel.fromJson(res.data);
    });
  }

  Future<FuelLogModel> createFuelLog(FuelLogModel log) async {
    return apiCall(() async {
      final res = await _dio.post('/fuel/logs', data: log.toJson());
      return FuelLogModel.fromJson(res.data);
    });
  }

  Future<FuelLogModel> updateFuelLog(String id, FuelLogModel log) async {
    return apiCall(() async {
      final res = await _dio.put('/fuel/logs/$id', data: log.toJson());
      return FuelLogModel.fromJson(res.data);
    });
  }

  Future<void> deleteFuelLog(String id) async {
    return apiCall(() async {
      await _dio.delete('/fuel/logs/$id');
    });
  }
}
