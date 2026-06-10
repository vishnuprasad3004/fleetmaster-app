import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/services/api_service.dart';
import '../data/models/vehicle_model.dart';

// Vehicle providers for real API integration
final vehiclesProvider = FutureProvider.autoDispose<List<VehicleModel>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  return await apiService.getVehicles();
});

final activeVehiclesProvider = FutureProvider.autoDispose<List<VehicleModel>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  return await apiService.getVehicles(status: 'active');
});

final vehicleByIdProvider = FutureProvider.family.autoDispose<VehicleModel?, String>((ref, vehicleId) async {
  final vehicles = await ref.watch(vehiclesProvider.future);
  return vehicles.cast<VehicleModel?>().firstWhere(
    (vehicle) => vehicle?.id == vehicleId,
    orElse: () => null,
  );
});

// Vehicle creation/update
final vehicleNotifierProvider = StateNotifierProvider<VehicleNotifier, AsyncValue<void>>((ref) {
  return VehicleNotifier(ref.watch(apiServiceProvider));
});

class VehicleNotifier extends StateNotifier<AsyncValue<void>> {
  final ApiService _apiService;

  VehicleNotifier(this._apiService) : super(const AsyncValue.data(null));

  Future<VehicleModel> createVehicle({
    required String registrationNumber,
    required String vehicleType,
    required String brand,
    required String model,
    String? variant,
    int? year,
    String? color,
    String? fuelType,
    double? fuelCapacity,
    double? mileage,
  }) async {
    state = const AsyncValue.loading();
    
    try {
      final vehicleData = {
        'registration_number': registrationNumber,
        'vehicle_type': vehicleType,
        'brand': brand,
        'model': model,
        if (variant != null) 'variant': variant,
        if (year != null) 'year': year,
        if (color != null) 'color': color,
        if (fuelType != null) 'fuel_type': fuelType,
        if (fuelCapacity != null) 'fuel_capacity': fuelCapacity,
        if (mileage != null) 'mileage': mileage,
      };

      final vehicle = await _apiService.createVehicle(vehicleData);
      state = const AsyncValue.data(null);
      return vehicle;
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
      rethrow;
    }
  }

  Future<VehicleModel> updateVehicle(String vehicleId, Map<String, dynamic> updates) async {
    state = const AsyncValue.loading();
    
    try {
      final vehicle = await _apiService.updateVehicle(vehicleId, updates);
      state = const AsyncValue.data(null);
      return vehicle;
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
      rethrow;
    }
  }
}