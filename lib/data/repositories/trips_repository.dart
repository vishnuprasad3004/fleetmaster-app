import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/api_client.dart';
import '../models/trip_model.dart';

final tripsRepositoryProvider = Provider<TripsRepository>((ref) {
  return TripsRepository(ref.watch(dioProvider));
});

class TripsRepository {
  TripsRepository(this._dio);

  final Dio _dio;

  Future<List<TripModel>> getTrips({String? status}) async {
    return apiCall(() async {
      final res = await _dio.get('/trips/', queryParameters: {
        if (status != null) 'status': status,
        'limit': 50,
      });
      final trips = res.data['trips'] as List<dynamic>;
      return trips.map((e) => TripModel.fromJson(e as Map<String, dynamic>)).toList();
    });
  }

  Future<TripStatsModel> getStats({int days = 30}) async {
    return apiCall(() async {
      final res = await _dio.get('/trips/stats', queryParameters: {'days': days});
      return TripStatsModel.fromJson(res.data as Map<String, dynamic>);
    });
  }

  Future<ProfitAnalysisModel> getProfitAnalysis({int days = 30}) async {
    return apiCall(() async {
      final res = await _dio.get('/trips/profit-analysis', queryParameters: {'days': days});
      return ProfitAnalysisModel.fromJson(res.data as Map<String, dynamic>);
    });
  }

  Future<void> createFuelRecord({
    required String vehicleId,
    required String fuelType,
    required double quantity,
    required double ratePerLiter,
    required double totalAmount,
    required double odometerReading,
    String? stationName,
    String? receiptNumber,
  }) async {
    return apiCall(() async {
      await _dio.post('/trips/fuel/', data: {
        'vehicle_id': vehicleId,
        'fuel_type': fuelType,
        'quantity': quantity,
        'rate_per_liter': ratePerLiter,
        'total_amount': totalAmount,
        'odometer_reading': odometerReading,
        if (stationName != null) 'station_name': stationName,
        if (receiptNumber != null) 'receipt_number': receiptNumber,
      });
    });
  }
}
