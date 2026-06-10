import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/models/fuel_model.dart';
import '../data/repositories/fuel_repository.dart';

final fuelDashboardProvider = FutureProvider.autoDispose<FuelDashboardModel>((ref) {
  final repo = ref.watch(fuelRepositoryProvider);
  return repo.getDashboard();
});

final fuelLogsProvider = FutureProvider.autoDispose<List<FuelLogModel>>((ref) {
  final repo = ref.watch(fuelRepositoryProvider);
  return repo.getFuelLogs();
});

final vehicleFuelLogsProvider = FutureProvider.family.autoDispose<List<FuelLogModel>, String>((ref, vehicleId) {
  final repo = ref.watch(fuelRepositoryProvider);
  return repo.getVehicleFuelLogs(vehicleId);
});

final vehicleFuelAnalyticsProvider = FutureProvider.family.autoDispose<VehicleFuelAnalyticsModel, String>((ref, vehicleId) {
  final repo = ref.watch(fuelRepositoryProvider);
  return repo.getVehicleAnalytics(vehicleId);
});
