import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/api_client.dart';
import '../models/driver_model.dart';

final driversRepositoryProvider = Provider<DriversRepository>((ref) {
  return DriversRepository(ref.watch(dioProvider));
});

class DriversRepository {
  DriversRepository(this._dio);

  final Dio _dio;

  Future<List<DriverModel>> getDrivers({String? status, String? query}) async {
    return apiCall(() async {
      final Response res;
      if (query != null && query.trim().isNotEmpty) {
        res = await _dio.get('/drivers/search', queryParameters: {'q': query.trim(), 'limit': 100});
      } else {
        res = await _dio.get('/drivers/', queryParameters: {
          if (status != null) 'status': status,
          'limit': 100,
        });
      }
      final drivers = res.data['drivers'] as List<dynamic>;
      return drivers.map((e) => DriverModel.fromJson(e as Map<String, dynamic>)).toList();
    });
  }
}
