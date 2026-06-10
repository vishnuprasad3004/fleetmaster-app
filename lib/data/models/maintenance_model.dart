class MaintenanceRecordModel {
  MaintenanceRecordModel({
    required this.id,
    required this.vehicleId,
    required this.vehicleNumber,
    required this.type,
    required this.date,
    required this.cost,
    this.workshopName,
    this.workshopContact,
    this.odometerReading,
    this.description,
    this.spareParts = const [],
    this.nextServiceDate,
    this.nextServiceOdometer,
    this.createdAt,
  });

  final String id;
  final String vehicleId;
  final String vehicleNumber;
  final MaintenanceType type;
  final String date;
  final double cost;
  final String? workshopName;
  final String? workshopContact;
  final int? odometerReading;
  final String? description;
  final List<SparePartModel> spareParts;
  final String? nextServiceDate;
  final int? nextServiceOdometer;
  final String? createdAt;

  factory MaintenanceRecordModel.fromJson(Map<String, dynamic> json) {
    final parts = json['spare_parts'] as List<dynamic>? ?? [];
    return MaintenanceRecordModel(
      id: json['id'] as String,
      vehicleId: json['vehicle_id'] as String,
      vehicleNumber: json['vehicle_number'] as String? ?? '',
      type: MaintenanceType.values.firstWhere(
        (e) => e.name == json['type'],
        orElse: () => MaintenanceType.service,
      ),
      date: json['date'] as String,
      cost: (json['cost'] as num).toDouble(),
      workshopName: json['workshop_name'] as String?,
      workshopContact: json['workshop_contact'] as String?,
      odometerReading: json['odometer_reading'] as int?,
      description: json['description'] as String?,
      spareParts: parts.map((e) => SparePartModel.fromJson(e as Map<String, dynamic>)).toList(),
      nextServiceDate: json['next_service_date']?.toString(),
      nextServiceOdometer: json['next_service_odometer'] as int?,
      createdAt: json['created_at']?.toString(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'vehicle_id': vehicleId,
      'vehicle_number': vehicleNumber,
      'type': type.name,
      'date': date,
      'cost': cost,
      'workshop_name': workshopName,
      'workshop_contact': workshopContact,
      'odometer_reading': odometerReading,
      'description': description,
      'spare_parts': spareParts.map((e) => e.toJson()).toList(),
      'next_service_date': nextServiceDate,
      'next_service_odometer': nextServiceOdometer,
      'created_at': createdAt,
    };
  }
}

class SparePartModel {
  SparePartModel({
    required this.name,
    required this.quantity,
    required this.cost,
  });

  final String name;
  final int quantity;
  final double cost;

  factory SparePartModel.fromJson(Map<String, dynamic> json) {
    return SparePartModel(
      name: json['name'] as String,
      quantity: json['quantity'] as int,
      cost: (json['cost'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'quantity': quantity,
      'cost': cost,
    };
  }
}

enum MaintenanceType {
  service,
  repair,
  inspection,
  tyreReplacement,
  batteryReplacement,
  oilChange,
  other,
}

class MaintenanceDashboardModel {
  MaintenanceDashboardModel({
    required this.serviceDueToday,
    required this.serviceDueThisWeek,
    required this.totalMaintenanceCost,
    required this.vehiclesInService,
    required this.costTrend,
    required this.topCostVehicle,
  });

  final int serviceDueToday;
  final int serviceDueThisWeek;
  final double totalMaintenanceCost;
  final int vehiclesInService;
  final List<double> costTrend;
  final VehicleCostModel topCostVehicle;

  factory MaintenanceDashboardModel.fromJson(Map<String, dynamic> json) {
    final trend = json['cost_trend'] as List<dynamic>? ?? [];
    return MaintenanceDashboardModel(
      serviceDueToday: json['service_due_today'] as int? ?? 0,
      serviceDueThisWeek: json['service_due_this_week'] as int? ?? 0,
      totalMaintenanceCost: (json['total_maintenance_cost'] as num?)?.toDouble() ?? 0.0,
      vehiclesInService: json['vehicles_in_service'] as int? ?? 0,
      costTrend: trend.map((e) => (e as num).toDouble()).toList(),
      topCostVehicle: VehicleCostModel.fromJson(json['top_cost_vehicle'] as Map<String, dynamic>? ?? {}),
    );
  }
}

class VehicleCostModel {
  VehicleCostModel({
    required this.vehicleNumber,
    required this.cost,
    required this.costChange,
  });

  final String vehicleNumber;
  final double cost;
  final double costChange;

  factory VehicleCostModel.fromJson(Map<String, dynamic> json) {
    return VehicleCostModel(
      vehicleNumber: json['vehicle_number'] as String? ?? '',
      cost: (json['cost'] as num?)?.toDouble() ?? 0.0,
      costChange: (json['cost_change'] as num?)?.toDouble() ?? 0.0,
    );
  }
}
