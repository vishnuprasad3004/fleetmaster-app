import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/services/api_service.dart';
import '../data/models/dashboard_model.dart';

// Real API providers for production data
final realDashboardStatsProvider = FutureProvider.autoDispose<DashboardStats>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  return await apiService.getDashboardStats();
});

final realAlertsProvider = FutureProvider.autoDispose<List<AlertModel>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  final alertsData = await apiService.getAlerts();
  
  return alertsData.map((alert) => AlertModel(
    id: alert['id'] ?? '',
    title: alert['title'] ?? '',
    description: alert['description'] ?? '',
    priority: alert['priority'] ?? 'info',
    category: alert['category'] ?? 'general',
    createdAt: DateTime.parse(alert['created_at'] ?? DateTime.now().toIso8601String()),
  )).toList();
});

final realRecentActivityProvider = FutureProvider.autoDispose<List<RecentActivity>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  return await apiService.getRecentActivity();
});

// Vehicle related providers
final realVehicleLocationsProvider = FutureProvider.autoDispose<List<VehicleLocation>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  final locationsData = await apiService.getVehicleLocations();
  
  return locationsData.map((location) => VehicleLocation(
    id: location['registration_number'] ?? '',
    driver: location['driver_name'] ?? 'Unknown',
    location: '${location['current_location'] ?? 'Unknown'}',
    speed: '${location['speed'] ?? 0} km/h',
    status: _mapVehicleStatus(location['status']),
    eta: location['eta'] ?? 'N/A',
    lastUpdate: location['last_update'] ?? 'Unknown',
  )).toList();
});

// Maintenance related providers  
final realMaintenanceDashboardProvider = FutureProvider.autoDispose<MaintenanceDashboard>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  final data = await apiService.getMaintenanceDashboard();
  
  return MaintenanceDashboard(
    upcomingServices: data['upcoming_services'] ?? 0,
    overdueServices: data['overdue_services'] ?? 0,
    totalCostThisMonth: (data['total_cost_this_month'] ?? 0.0).toDouble(),
    avgServiceCost: (data['avg_service_cost'] ?? 0.0).toDouble(),
  );
});

// Fuel related providers
final realFuelDashboardProvider = FutureProvider.autoDispose<FuelDashboard>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  final data = await apiService.getFuelDashboard();
  
  return FuelDashboard(
    totalFuelConsumed: (data['total_fuel_consumed'] ?? 0.0).toDouble(),
    avgFuelEfficiency: (data['avg_fuel_efficiency'] ?? 0.0).toDouble(),
    totalFuelCost: (data['total_fuel_cost'] ?? 0.0).toDouble(),
    costPerKm: (data['cost_per_km'] ?? 0.0).toDouble(),
  );
});

// Helper functions
VehicleStatus _mapVehicleStatus(String? status) {
  switch (status?.toLowerCase()) {
    case 'active':
    case 'running':
      return VehicleStatus.running;
    case 'idle':
      return VehicleStatus.idle;
    case 'maintenance':
    case 'service':
      return VehicleStatus.maintenance;
    default:
      return VehicleStatus.idle;
  }
}

// Models for the new data structures
class AlertModel {
  final String id;
  final String title;
  final String description;
  final String priority;
  final String category;
  final DateTime createdAt;

  AlertModel({
    required this.id,
    required this.title,
    required this.description,
    required this.priority,
    required this.category,
    required this.createdAt,
  });
}

class VehicleLocation {
  final String id;
  final String driver;
  final String location;
  final String speed;
  final VehicleStatus status;
  final String eta;
  final String lastUpdate;

  VehicleLocation({
    required this.id,
    required this.driver,
    required this.location,
    required this.speed,
    required this.status,
    required this.eta,
    required this.lastUpdate,
  });
}

enum VehicleStatus { running, idle, maintenance }

class MaintenanceDashboard {
  final int upcomingServices;
  final int overdueServices;
  final double totalCostThisMonth;
  final double avgServiceCost;

  MaintenanceDashboard({
    required this.upcomingServices,
    required this.overdueServices,
    required this.totalCostThisMonth,
    required this.avgServiceCost,
  });
}

class FuelDashboard {
  final double totalFuelConsumed;
  final double avgFuelEfficiency;
  final double totalFuelCost;
  final double costPerKm;

  FuelDashboard({
    required this.totalFuelConsumed,
    required this.avgFuelEfficiency,
    required this.totalFuelCost,
    required this.costPerKm,
  });
}