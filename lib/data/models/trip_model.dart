class TripModel {
  TripModel({
    required this.id,
    required this.tripNumber,
    required this.status,
    this.originName,
    this.destinationName,
    this.revenue,
    this.profit,
    this.vehicleId,
    this.vehicleRegistration,
    this.driverName,
    this.updatedAt,
  });

  final String id;
  final String tripNumber;
  final String status;
  final String? vehicleId;
  final String? originName;
  final String? destinationName;
  final double? revenue;
  final double? profit;
  final String? vehicleRegistration;
  final String? driverName;
  final String? updatedAt;

  String get routeLabel {
    if (originName != null && destinationName != null) {
      return '$originName → $destinationName';
    }
    return '—';
  }

  factory TripModel.fromJson(Map<String, dynamic> json) {
    return TripModel(
      id: json['id'] as String,
      tripNumber: json['trip_number'] as String? ?? '',
      status: json['status'] is String ? json['status'] as String : json['status'].toString(),
      vehicleId: json['vehicle_id'] as String?,
      originName: json['origin_name'] as String?,
      destinationName: json['destination_name'] as String?,
      revenue: (json['revenue'] as num?)?.toDouble(),
      profit: (json['profit'] as num?)?.toDouble(),
      vehicleRegistration: null,
      driverName: null,
      updatedAt: json['updated_at']?.toString(),
    );
  }
}

class TripStatsModel {
  TripStatsModel({
    required this.totalTrips,
    required this.completedTrips,
    required this.tripsInProgress,
    required this.totalRevenue,
    required this.totalCosts,
    required this.totalProfit,
    required this.totalDistance,
  });

  final int totalTrips;
  final int completedTrips;
  final int tripsInProgress;
  final double totalRevenue;
  final double totalCosts;
  final double totalProfit;
  final double totalDistance;

  factory TripStatsModel.fromJson(Map<String, dynamic> json) {
    return TripStatsModel(
      totalTrips: json['total_trips'] as int? ?? 0,
      completedTrips: json['completed_trips'] as int? ?? 0,
      tripsInProgress: json['trips_in_progress'] as int? ?? 0,
      totalRevenue: (json['total_revenue'] as num?)?.toDouble() ?? 0,
      totalCosts: (json['total_costs'] as num?)?.toDouble() ?? 0,
      totalProfit: (json['total_profit'] as num?)?.toDouble() ?? 0,
      totalDistance: (json['total_distance'] as num?)?.toDouble() ?? 0,
    );
  }
}

class ProfitAnalysisModel {
  ProfitAnalysisModel({
    this.mostProfitableVehicleId,
    this.mostProfitableAmount = 0,
    this.leastProfitableVehicleId,
    this.leastProfitableAmount = 0,
  });

  final String? mostProfitableVehicleId;
  final double mostProfitableAmount;
  final String? leastProfitableVehicleId;
  final double leastProfitableAmount;

  factory ProfitAnalysisModel.fromJson(Map<String, dynamic> json) {
    return ProfitAnalysisModel(
      mostProfitableVehicleId: json['most_profitable_vehicle_id'] as String?,
      mostProfitableAmount: (json['most_profitable_amount'] as num?)?.toDouble() ?? 0,
      leastProfitableVehicleId: json['least_profitable_vehicle_id'] as String?,
      leastProfitableAmount: (json['least_profitable_amount'] as num?)?.toDouble() ?? 0,
    );
  }
}
