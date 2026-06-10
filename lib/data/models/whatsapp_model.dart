class WhatsAppConfigModel {
  WhatsAppConfigModel({
    required this.id,
    required this.phoneNumber,
    required this.isEnabled,
    this.dailySummaryEnabled = true,
    this.alertsEnabled = true,
    this.summaryTime = '09:00',
    this.createdAt,
  });

  final String id;
  final String phoneNumber;
  final bool isEnabled;
  final bool dailySummaryEnabled;
  final bool alertsEnabled;
  final String summaryTime;
  final String? createdAt;

  factory WhatsAppConfigModel.fromJson(Map<String, dynamic> json) {
    return WhatsAppConfigModel(
      id: json['id'] as String,
      phoneNumber: json['phone_number'] as String,
      isEnabled: json['is_enabled'] as bool? ?? false,
      dailySummaryEnabled: json['daily_summary_enabled'] as bool? ?? true,
      alertsEnabled: json['alerts_enabled'] as bool? ?? true,
      summaryTime: json['summary_time'] as String? ?? '09:00',
      createdAt: json['created_at']?.toString(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'phone_number': phoneNumber,
      'is_enabled': isEnabled,
      'daily_summary_enabled': dailySummaryEnabled,
      'alerts_enabled': alertsEnabled,
      'summary_time': summaryTime,
      'created_at': createdAt,
    };
  }
}

class AlertRuleModel {
  AlertRuleModel({
    required this.id,
    required this.alertType,
    required this.isEnabled,
    required this.notifyBeforeDays,
    this.notifyAtTime = '09:00',
  });

  final String id;
  final AlertType alertType;
  final bool isEnabled;
  final int notifyBeforeDays;
  final String notifyAtTime;

  factory AlertRuleModel.fromJson(Map<String, dynamic> json) {
    return AlertRuleModel(
      id: json['id'] as String,
      alertType: AlertType.values.firstWhere(
        (e) => e.name == json['alert_type'],
        orElse: () => AlertType.insuranceExpiry,
      ),
      isEnabled: json['is_enabled'] as bool? ?? true,
      notifyBeforeDays: json['notify_before_days'] as int? ?? 7,
      notifyAtTime: json['notify_at_time'] as String? ?? '09:00',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'alert_type': alertType.name,
      'is_enabled': isEnabled,
      'notify_before_days': notifyBeforeDays,
      'notify_at_time': notifyAtTime,
    };
  }
}

enum AlertType {
  insuranceExpiry,
  permitExpiry,
  pucExpiry,
  serviceDue,
  paymentOverdue,
  driverLicenseExpiry,
}

extension AlertTypeExtension on AlertType {
  String get displayName {
    switch (this) {
      case AlertType.insuranceExpiry:
        return 'Insurance Expiry';
      case AlertType.permitExpiry:
        return 'Permit Expiry';
      case AlertType.pucExpiry:
        return 'PUC Expiry';
      case AlertType.serviceDue:
        return 'Service Due';
      case AlertType.paymentOverdue:
        return 'Payment Overdue';
      case AlertType.driverLicenseExpiry:
        return 'Driver License Expiry';
    }
  }

  String get icon {
    switch (this) {
      case AlertType.insuranceExpiry:
        return '📋';
      case AlertType.permitExpiry:
        return '📄';
      case AlertType.pucExpiry:
        return '🔬';
      case AlertType.serviceDue:
        return '🔧';
      case AlertType.paymentOverdue:
        return '💰';
      case AlertType.driverLicenseExpiry:
        return '🪪';
    }
  }
}

class DailySummaryConfigModel {
  DailySummaryConfigModel({
    required this.includeRevenue,
    required this.includeExpenses,
    required this.includeProfit,
    required this.includeOutstanding,
    required this.includeActiveVehicles,
    required this.includeAlerts,
  });

  final bool includeRevenue;
  final bool includeExpenses;
  final bool includeProfit;
  final bool includeOutstanding;
  final bool includeActiveVehicles;
  final bool includeAlerts;

  factory DailySummaryConfigModel.fromJson(Map<String, dynamic> json) {
    return DailySummaryConfigModel(
      includeRevenue: json['include_revenue'] as bool? ?? true,
      includeExpenses: json['include_expenses'] as bool? ?? true,
      includeProfit: json['include_profit'] as bool? ?? true,
      includeOutstanding: json['include_outstanding'] as bool? ?? true,
      includeActiveVehicles: json['include_active_vehicles'] as bool? ?? true,
      includeAlerts: json['include_alerts'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'include_revenue': includeRevenue,
      'include_expenses': includeExpenses,
      'include_profit': includeProfit,
      'include_outstanding': includeOutstanding,
      'include_active_vehicles': includeActiveVehicles,
      'include_alerts': includeAlerts,
    };
  }
}
