class DashboardStats {
  DashboardStats({
    required this.overview,
    required this.financial,
    required this.operations,
    required this.alerts,
  });

  final DashboardOverview overview;
  final DashboardFinancial financial;
  final DashboardOperations operations;
  final DashboardAlerts alerts;

  factory DashboardStats.fromJson(Map<String, dynamic> json) {
    return DashboardStats(
      overview: DashboardOverview.fromJson(json['overview'] as Map<String, dynamic>? ?? {}),
      financial: DashboardFinancial.fromJson(json['financial'] as Map<String, dynamic>? ?? {}),
      operations: DashboardOperations.fromJson(json['operations'] as Map<String, dynamic>? ?? {}),
      alerts: DashboardAlerts.fromJson(json['alerts'] as Map<String, dynamic>? ?? {}),
    );
  }
}

class DashboardOverview {
  DashboardOverview({
    this.totalVehicles = 0,
    this.activeVehicles = 0,
    this.totalDrivers = 0,
    this.activeDrivers = 0,
    this.tripsInProgress = 0,
    this.completedTripsToday = 0,
  });

  final int totalVehicles;
  final int activeVehicles;
  final int totalDrivers;
  final int activeDrivers;
  final int tripsInProgress;
  final int completedTripsToday;

  factory DashboardOverview.fromJson(Map<String, dynamic> json) {
    return DashboardOverview(
      totalVehicles: json['total_vehicles'] as int? ?? 0,
      activeVehicles: json['active_vehicles'] as int? ?? 0,
      totalDrivers: json['total_drivers'] as int? ?? 0,
      activeDrivers: json['active_drivers'] as int? ?? 0,
      tripsInProgress: json['trips_in_progress'] as int? ?? 0,
      completedTripsToday: json['completed_trips_today'] as int? ?? 0,
    );
  }
}

class DashboardFinancial {
  DashboardFinancial({
    this.totalRevenue = 0,
    this.totalCosts = 0,
    this.totalProfit = 0,
    this.fuelCost = 0,
    this.maintenanceCost = 0,
    this.revenueGrowth = 0,
    this.profitGrowth = 0,
  });

  final double totalRevenue;
  final double totalCosts;
  final double totalProfit;
  final double fuelCost;
  final double maintenanceCost;
  final double revenueGrowth;
  final double profitGrowth;

  factory DashboardFinancial.fromJson(Map<String, dynamic> json) {
    return DashboardFinancial(
      totalRevenue: (json['total_revenue'] as num?)?.toDouble() ?? 0,
      totalCosts: (json['total_costs'] as num?)?.toDouble() ?? 0,
      totalProfit: (json['total_profit'] as num?)?.toDouble() ?? 0,
      fuelCost: (json['fuel_cost'] as num?)?.toDouble() ?? 0,
      maintenanceCost: (json['maintenance_cost'] as num?)?.toDouble() ?? 0,
      revenueGrowth: (json['revenue_growth'] as num?)?.toDouble() ?? 0,
      profitGrowth: (json['profit_growth'] as num?)?.toDouble() ?? 0,
    );
  }
}

class DashboardOperations {
  DashboardOperations({
    this.totalDistance = 0,
    this.totalFuelConsumed = 0,
    this.avgEfficiencyScore = 0,
    this.totalRefuels = 0,
    this.totalServices = 0,
    this.activeVehicles = 0,
    this.vehiclesInService = 0,
    this.activeTrips = 0,
    this.averageSpeed = 0,
  });

  final double totalDistance;
  final double totalFuelConsumed;
  final double avgEfficiencyScore;
  final int totalRefuels;
  final int totalServices;
  final int activeVehicles;
  final int vehiclesInService;
  final int activeTrips;
  final double averageSpeed;

  factory DashboardOperations.fromJson(Map<String, dynamic> json) {
    return DashboardOperations(
      totalDistance: (json['total_distance'] as num?)?.toDouble() ?? 0,
      totalFuelConsumed: (json['total_fuel_consumed'] as num?)?.toDouble() ?? 0,
      avgEfficiencyScore: (json['avg_efficiency_score'] as num?)?.toDouble() ?? 0,
      totalRefuels: json['total_refuels'] as int? ?? 0,
      totalServices: json['total_services'] as int? ?? 0,
      activeVehicles: json['active_vehicles'] as int? ?? 0,
      vehiclesInService: json['vehicles_in_service'] as int? ?? 0,
      activeTrips: json['active_trips'] as int? ?? 0,
      averageSpeed: (json['average_speed'] as num?)?.toDouble() ?? 0,
    );
  }
}

class DashboardAlerts {
  DashboardAlerts({
    this.vehiclesWithExpiredDocs = 0,
    this.vehiclesDueForService = 0,
    this.driversWithExpiredLicense = 0,
    this.driversLicenseExpiringSoon = 0,
  });

  final int vehiclesWithExpiredDocs;
  final int vehiclesDueForService;
  final int driversWithExpiredLicense;
  final int driversLicenseExpiringSoon;

  int get criticalCount =>
      vehiclesWithExpiredDocs + driversWithExpiredLicense;

  factory DashboardAlerts.fromJson(Map<String, dynamic> json) {
    return DashboardAlerts(
      vehiclesWithExpiredDocs: json['vehicles_with_expired_docs'] as int? ?? 0,
      vehiclesDueForService: json['vehicles_due_for_service'] as int? ?? 0,
      driversWithExpiredLicense: json['drivers_with_expired_license'] as int? ?? 0,
      driversLicenseExpiringSoon: json['drivers_license_expiring_soon'] as int? ?? 0,
    );
  }
}

class AlertModel {
  AlertModel({
    required this.id,
    required this.type,
    required this.category,
    required this.title,
    required this.description,
    required this.priority,
    required this.createdAt,
  });

  final String id;
  final String type;
  final String category;
  final String title;
  final String description;
  final String priority;
  final DateTime createdAt;

  factory AlertModel.fromJson(Map<String, dynamic> json) {
    return AlertModel(
      id: json['id'] as String? ?? '',
      type: json['type'] as String? ?? 'info',
      category: json['category'] as String? ?? '',
      title: json['title'] as String? ?? '',
      description: json['description'] as String? ?? '',
      priority: json['priority'] as String? ?? 'low',
      createdAt: DateTime.parse(json['created_at'] as String? ?? DateTime.now().toIso8601String()),
    );
  }
}

class ActivityModel {
  ActivityModel({
    required this.id,
    required this.title,
    required this.description,
    required this.type,
    required this.timestamp,
    this.metadata,
  });

  final String id;
  final String title;
  final String description;
  final String type;
  final DateTime timestamp;
  final Map<String, dynamic>? metadata;

  factory ActivityModel.fromJson(Map<String, dynamic> json) {
    return ActivityModel(
      id: json['id'] as String? ?? '',
      title: json['title'] as String? ?? 'Activity',
      description: json['description'] as String? ?? '',
      type: json['type'] as String? ?? 'general',
      timestamp: DateTime.parse(json['timestamp'] as String? ?? DateTime.now().toIso8601String()),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }
}

// Alias for consistency with API service
typedef RecentActivity = ActivityModel;
