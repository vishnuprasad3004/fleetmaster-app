class DriverModel {
  DriverModel({
    required this.id,
    required this.fullName,
    required this.licenseNumber,
    required this.status,
    required this.avgRating,
    this.isLicenseExpired = false,
    this.licenseDaysToExpiry,
    this.currentVehicleRegistration,
  });

  final String id;
  final String fullName;
  final String licenseNumber;
  final String status;
  final double avgRating;
  final bool isLicenseExpired;
  final int? licenseDaysToExpiry;
  final String? currentVehicleRegistration;

  bool get isActive => status == 'active';

  factory DriverModel.fromJson(Map<String, dynamic> json) {
    return DriverModel(
      id: json['id'] as String,
      fullName: json['full_name'] as String,
      licenseNumber: json['license_number'] as String? ?? '—',
      status: json['status'] as String? ?? 'inactive',
      avgRating: (json['avg_rating'] as num?)?.toDouble() ?? 0,
      isLicenseExpired: json['is_license_expired'] as bool? ?? false,
      licenseDaysToExpiry: json['license_days_to_expiry'] as int?,
      currentVehicleRegistration: json['current_vehicle_registration'] as String?,
    );
  }
}
