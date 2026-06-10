import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/api_client.dart';
import '../models/vehicle_model.dart';

final vehiclesRepositoryProvider = Provider<VehiclesRepository>((ref) {
  return VehiclesRepository(ref.watch(dioProvider));
});

class VehiclesRepository {
  VehiclesRepository(this._dio);

  final Dio _dio;

  Future<List<VehicleModel>> getVehicles({String? status, String? query}) async {
    return apiCall(() async {
      final Response res;
      if (query != null && query.trim().isNotEmpty) {
        res = await _dio.get('/vehicles/search', queryParameters: {'q': query.trim(), 'limit': 100});
      } else {
        res = await _dio.get('/vehicles/', queryParameters: {
          if (status != null) 'status': status,
          'limit': 100,
        });
      }
      final vehicles = res.data['vehicles'] as List<dynamic>;
      return vehicles.map((e) => VehicleModel.fromJson(e as Map<String, dynamic>)).toList();
    });
  }
}
