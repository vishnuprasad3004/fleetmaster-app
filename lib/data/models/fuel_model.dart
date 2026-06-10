class FuelLogModel {
  FuelLogModel({
    required this.id,
    required this.vehicleId,
    required this.vehicleNumber,
    required this.date,
    required this.quantity,
    required this.costPerLiter,
    required this.totalCost,
    this.odometerReading,
    this.fuelStation,
    this.fuelType,
    this.driverId,
    this.driverName,
    this.createdAt,
  });

  final String id;
  final String vehicleId;
  final String vehicleNumber;
  final String date;
  final double quantity;
  final double costPerLiter;
  final double totalCost;
  final int? odometerReading;
  final String? fuelStation;
  final String? fuelType;
  final String? driverId;
  final String? driverName;
  final String? createdAt;

  double get mileage {
    if (odometerReading == null) return 0.0;
    return quantity > 0 ? (odometerReading! / quantity) : 0.0;
  }

  factory FuelLogModel.fromJson(Map<String, dynamic> json) {
    return FuelLogModel(
      id: json['id'] as String,
      vehicleId: json['vehicle_id'] as String,
      vehicleNumber: json['vehicle_number'] as String? ?? '',
      date: json['date'] as String,
      quantity: (json['quantity'] as num).toDouble(),
      costPerLiter: (json['cost_per_liter'] as num).toDouble(),
      totalCost: (json['total_cost'] as num).toDouble(),
      odometerReading: json['odometer_reading'] as int?,
      fuelStation: json['fuel_station'] as String?,
      fuelType: json['fuel_type'] as String?,
      driverId: json['driver_id'] as String?,
      driverName: json['driver_name'] as String?,
      createdAt: json['created_at']?.toString(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'vehicle_id': vehicleId,
      'vehicle_number': vehicleNumber,
      'date': date,
      'quantity': quantity,
      'cost_per_liter': costPerLiter,
      'total_cost': totalCost,
      'odometer_reading': odometerReading,
      'fuel_station': fuelStation,
      'fuel_type': fuelType,
      'driver_id': driverId,
      'driver_name': driverName,
      'created_at': createdAt,
    };
  }
}

class FuelDashboardModel {
  FuelDashboardModel({
    required this.totalFuelCost,
    required this.bestMileageVehicle,
    required this.worstMileageVehicle,
    required this.costTrend,
    required this.averageMileage,
    required this.totalQuantity,
  });

  final double totalFuelCost;
  final VehicleFuelModel bestMileageVehicle;
  final VehicleFuelModel worstMileageVehicle;
  final List<double> costTrend;
  final double averageMileage;
  final double totalQuantity;

  factory FuelDashboardModel.fromJson(Map<String, dynamic> json) {
    final trend = json['cost_trend'] as List<dynamic>? ?? [];
    return FuelDashboardModel(
      totalFuelCost: (json['total_fuel_cost'] as num?)?.toDouble() ?? 0.0,
      bestMileageVehicle: VehicleFuelModel.fromJson(json['best_mileage_vehicle'] as Map<String, dynamic>? ?? {}),
      worstMileageVehicle: VehicleFuelModel.fromJson(json['worst_mileage_vehicle'] as Map<String, dynamic>? ?? {}),
      costTrend: trend.map((e) => (e as num).toDouble()).toList(),
      averageMileage: (json['average_mileage'] as num?)?.toDouble() ?? 0.0,
      totalQuantity: (json['total_quantity'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class VehicleFuelModel {
  VehicleFuelModel({
    required this.vehicleNumber,
    required this.mileage,
    required this.mileageChange,
    required this.totalCost,
  });

  final String vehicleNumber;
  final double mileage;
  final double mileageChange;
  final double totalCost;

  factory VehicleFuelModel.fromJson(Map<String, dynamic> json) {
    return VehicleFuelModel(
      vehicleNumber: json['vehicle_number'] as String? ?? '',
      mileage: (json['mileage'] as num?)?.toDouble() ?? 0.0,
      mileageChange: (json['mileage_change'] as num?)?.toDouble() ?? 0.0,
      totalCost: (json['total_cost'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class VehicleFuelAnalyticsModel {
  VehicleFuelAnalyticsModel({
    required this.vehicleNumber,
    required this.totalFuelCost,
    required this.totalQuantity,
    required this.averageMileage,
    required this.costPerKm,
    required this.fuelLogs,
    required this.mileageTrend,
  });

  final String vehicleNumber;
  final double totalFuelCost;
  final double totalQuantity;
  final double averageMileage;
  final double costPerKm;
  final List<FuelLogModel> fuelLogs;
  final List<double> mileageTrend;

  factory VehicleFuelAnalyticsModel.fromJson(Map<String, dynamic> json) {
    final logs = json['fuel_logs'] as List<dynamic>? ?? [];
    final trend = json['mileage_trend'] as List<dynamic>? ?? [];
    return VehicleFuelAnalyticsModel(
      vehicleNumber: json['vehicle_number'] as String? ?? '',
      totalFuelCost: (json['total_fuel_cost'] as num?)?.toDouble() ?? 0.0,
      totalQuantity: (json['total_quantity'] as num?)?.toDouble() ?? 0.0,
      averageMileage: (json['average_mileage'] as num?)?.toDouble() ?? 0.0,
      costPerKm: (json['cost_per_km'] as num?)?.toDouble() ?? 0.0,
      fuelLogs: logs.map((e) => FuelLogModel.fromJson(e as Map<String, dynamic>)).toList(),
      mileageTrend: trend.map((e) => (e as num).toDouble()).toList(),
    );
  }
}
