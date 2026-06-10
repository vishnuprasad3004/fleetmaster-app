class VehicleDocumentModel {
  VehicleDocumentModel({
    required this.id,
    required this.documentType,
    required this.isExpired,
    this.documentNumber,
    this.expiryDate,
    this.daysToExpiry,
  });

  final String id;
  final String documentType;
  final String? documentNumber;
  final String? expiryDate;
  final bool isExpired;
  final int? daysToExpiry;

  factory VehicleDocumentModel.fromJson(Map<String, dynamic> json) {
    return VehicleDocumentModel(
      id: json['id'] as String,
      documentType: json['document_type'] as String,
      documentNumber: json['document_number'] as String?,
      expiryDate: json['expiry_date']?.toString(),
      isExpired: json['is_expired'] as bool? ?? false,
      daysToExpiry: json['days_to_expiry'] as int?,
    );
  }
}

class VehicleModel {
  VehicleModel({
    required this.id,
    required this.registrationNumber,
    required this.brand,
    required this.model,
    required this.status,
    this.variant,
    this.year,
    this.color,
    this.fuelType,
    this.fuelCapacity,
    this.mileage,
    this.currentOdo = 0.0,
    this.currentDriverId,
    this.isServiceDue = false,
    this.documents = const [],
  });

  final String id;
  final String registrationNumber;
  final String brand;
  final String model;
  final String status;
  final String? variant;
  final int? year;
  final String? color;
  final String? fuelType;
  final double? fuelCapacity;
  final double? mileage;
  final double currentOdo;
  final String? currentDriverId;
  final bool isServiceDue;
  final List<VehicleDocumentModel> documents;

  String get displayName => '$brand $model'.trim();

  factory VehicleModel.fromJson(Map<String, dynamic> json) {
    final docs = json['documents'] as List<dynamic>? ?? [];
    return VehicleModel(
      id: json['id'] as String,
      registrationNumber: json['registration_number'] as String,
      brand: json['brand'] as String? ?? '',
      model: json['model'] as String? ?? '',
      status: json['status'] as String? ?? 'inactive',
      variant: json['variant'] as String?,
      year: json['year'] as int?,
      color: json['color'] as String?,
      fuelType: json['fuel_type'] as String?,
      fuelCapacity: (json['fuel_capacity'] as num?)?.toDouble(),
      mileage: (json['mileage'] as num?)?.toDouble(),
      currentOdo: (json['current_odo'] as num?)?.toDouble() ?? 0.0,
      currentDriverId: json['current_driver_id'] as String?,
      isServiceDue: json['is_service_due'] as bool? ?? false,
      documents: docs.map((e) => VehicleDocumentModel.fromJson(e as Map<String, dynamic>)).toList(),
    );
  }
}
