import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/models/dashboard_model.dart';
import '../data/repositories/dashboard_repository.dart';

final dashboardStatsProvider = FutureProvider.autoDispose<DashboardStats>((ref) {
  return ref.watch(dashboardRepositoryProvider).getStats();
});

final dashboardAlertsProvider = FutureProvider.autoDispose<List<AlertModel>>((ref) {
  return ref.watch(dashboardRepositoryProvider).getAlerts();
});

final recentActivityProvider = FutureProvider.autoDispose<List<ActivityModel>>((ref) {
  return ref.watch(dashboardRepositoryProvider).getRecentActivity();
});
