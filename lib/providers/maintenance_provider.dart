import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/models/maintenance_model.dart';
import '../data/repositories/maintenance_repository.dart';

final maintenanceDashboardProvider = FutureProvider.autoDispose<MaintenanceDashboardModel>((ref) {
  final repo = ref.watch(maintenanceRepositoryProvider);
  return repo.getDashboard();
});

final maintenanceRecordsProvider = FutureProvider.autoDispose<List<MaintenanceRecordModel>>((ref) {
  final repo = ref.watch(maintenanceRepositoryProvider);
  return repo.getRecords();
});

final vehicleMaintenanceRecordsProvider = FutureProvider.family.autoDispose<List<MaintenanceRecordModel>, String>((ref, vehicleId) {
  final repo = ref.watch(maintenanceRepositoryProvider);
  return repo.getVehicleRecords(vehicleId);
});

final upcomingServicesProvider = FutureProvider.autoDispose<List<MaintenanceRecordModel>>((ref) {
  final repo = ref.watch(maintenanceRepositoryProvider);
  return repo.getUpcomingServices();
});

final serviceRecordsProvider = FutureProvider.autoDispose<List<MaintenanceRecordModel>>((ref) {
  final repo = ref.watch(maintenanceRepositoryProvider);
  return repo.getServiceRecords();
});

final repairRecordsProvider = FutureProvider.autoDispose<List<MaintenanceRecordModel>>((ref) {
  final repo = ref.watch(maintenanceRepositoryProvider);
  return repo.getRepairRecords();
});
