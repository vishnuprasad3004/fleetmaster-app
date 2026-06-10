import 'package:flutter/material.dart';

/// FleetMaster design system — Dark theme matching the app mockups.
class AppColors {
  // Primary colors
  static const Color primary = Color(0xFF0056D2);
  static const Color primaryLight = Color(0xFF4285F4);
  static const Color primaryDark = Color(0xFF0041A8);

  // Status colors
  static const Color success = Color(0xFF10B981);
  static const Color successBg = Color(0xFF1E3A3A);
  static const Color warning = Color(0xFFFFB800);
  static const Color warningBg = Color(0xFF3A3015);
  static const Color danger = Color(0xFFFF4444);
  static const Color dangerBg = Color(0xFF3A1515);
  static const Color info = Color(0xFF4285F4);
  static const Color infoBg = Color(0xFF1A2332);

  // Dark theme colors
  static const Color background = Color(0xFF0F1419);
  static const Color surface = Color(0xFF1A1F2E);
  static const Color cardBackground = Color(0xFF242938);
  static const Color border = Color(0xFF2A2F3E);
  
  // Text colors
  static const Color white = Color(0xFFFFFFFF);
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textSecondary = Color(0xFFB8BCC8);
  static const Color textMuted = Color(0xFF7C8293);
  
  // Special colors for status indicators
  static const Color running = Color(0xFF10B981);
  static const Color idle = Color(0xFFFFB800);
  static const Color alert = Color(0xFFFF4444);
  
  // Vehicle status colors
  static const Color vehicleRunning = Color(0xFF34D399);
  static const Color vehicleIdle = Color(0xFFFBBF24);
  static const Color vehicleMaintenance = Color(0xFFF87171);
}
