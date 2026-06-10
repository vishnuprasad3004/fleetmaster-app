import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:fleetmaster/presentation/screens/auth/login_screen.dart';
import 'package:fleetmaster/presentation/screens/auth/register_screen.dart';
import 'package:fleetmaster/presentation/screens/main/main_shell.dart';
import 'package:fleetmaster/presentation/screens/splash_screen.dart';
import 'package:fleetmaster/presentation/screens/alerts/alerts_screen.dart';
import 'package:fleetmaster/presentation/screens/documents/documents_screen.dart';
import 'package:fleetmaster/presentation/screens/expense/add_expense_screen.dart';
import 'package:fleetmaster/presentation/screens/ledger/customer_ledger_screen.dart';
import 'package:fleetmaster/presentation/screens/trips/trips_screen.dart';
import 'package:fleetmaster/presentation/screens/maintenance/maintenance_dashboard_screen.dart';
import 'package:fleetmaster/presentation/screens/maintenance/service_history_screen.dart';
import 'package:fleetmaster/presentation/screens/maintenance/repair_history_screen.dart';
import 'package:fleetmaster/presentation/screens/maintenance/upcoming_services_screen.dart';
import 'package:fleetmaster/presentation/screens/maintenance/add_service_screen.dart';
import 'package:fleetmaster/presentation/screens/maintenance/add_repair_screen.dart';
import 'package:fleetmaster/presentation/screens/fuel/fuel_dashboard_screen.dart';
import 'package:fleetmaster/presentation/screens/fuel/fuel_log_screen.dart';
import 'package:fleetmaster/presentation/screens/fuel/add_fuel_screen.dart';
import 'package:fleetmaster/presentation/screens/fuel/vehicle_fuel_analytics_screen.dart';
import 'package:fleetmaster/presentation/screens/whatsapp/whatsapp_settings_screen.dart';
import 'package:fleetmaster/presentation/screens/whatsapp/whatsapp_config_screen.dart';
import 'package:fleetmaster/presentation/screens/whatsapp/alert_rules_screen.dart';
import 'package:fleetmaster/presentation/screens/whatsapp/daily_summary_screen.dart';
import 'package:fleetmaster/presentation/screens/vehicles/vehicle_detail_screen.dart';
import 'package:fleetmaster/presentation/screens/drivers/driver_detail_screen.dart';
import 'package:fleetmaster/providers/auth_provider.dart';

final goRouterProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authStateProvider);

  return GoRouter(
    initialLocation: '/splash',
    refreshListenable: _RouterRefresh(ref),
    redirect: (context, state) {
      final path = state.matchedLocation;
      final isLoading = authState.isLoading;
      final user = authState.valueOrNull;
      final isAuthed = user != null;

      if (path == '/splash') {
        if (isLoading) return null;
        return isAuthed ? '/home' : '/login';
      }

      final isAuthRoute = path == '/login' || path == '/register';
      if (!isLoading && !isAuthed && !isAuthRoute) return '/login';
      if (!isLoading && isAuthed && isAuthRoute) return '/home';
      return null;
    },
    routes: [
      GoRoute(path: '/splash', builder: (context, state) => const SplashScreen()),
      GoRoute(path: '/login', builder: (context, state) => const LoginScreen()),
      GoRoute(path: '/register', builder: (context, state) => const RegisterScreen()),
      GoRoute(path: '/home', builder: (context, state) => const MainShell()),
      GoRoute(path: '/alerts', builder: (context, state) => const AlertsScreen()),
      GoRoute(path: '/documents', builder: (context, state) => const DocumentsScreen()),
      GoRoute(path: '/ledger', builder: (context, state) => const CustomerLedgerScreen()),
      GoRoute(path: '/expense/add', builder: (context, state) => const AddExpenseScreen()),
      GoRoute(path: '/trips', builder: (context, state) => const TripsScreen()),
      // Maintenance Module Routes
      GoRoute(path: '/maintenance', builder: (context, state) => const MaintenanceDashboardScreen()),
      GoRoute(path: '/maintenance/service/history', builder: (context, state) => const ServiceHistoryScreen()),
      GoRoute(path: '/maintenance/repair/history', builder: (context, state) => const RepairHistoryScreen()),
      GoRoute(path: '/maintenance/upcoming', builder: (context, state) => const UpcomingServicesScreen()),
      GoRoute(path: '/maintenance/service/add', builder: (context, state) => const AddServiceScreen()),
      GoRoute(path: '/maintenance/repair/add', builder: (context, state) => const AddRepairScreen()),
      // Fuel Module Routes
      GoRoute(path: '/fuel', builder: (context, state) => const FuelDashboardScreen()),
      GoRoute(path: '/fuel/logs', builder: (context, state) => const FuelLogScreen()),
      GoRoute(path: '/fuel/add', builder: (context, state) => const AddFuelScreen()),
      GoRoute(path: '/fuel/analytics/:vehicleId', builder: (context, state) {
        final vehicleId = state.pathParameters['vehicleId']!;
        return VehicleFuelAnalyticsScreen(vehicleId: vehicleId);
      }),
      // WhatsApp Module Routes
      GoRoute(path: '/whatsapp', builder: (context, state) => const WhatsAppSettingsScreen()),
      GoRoute(path: '/whatsapp/config', builder: (context, state) => const WhatsAppConfigScreen()),
      GoRoute(path: '/whatsapp/alerts', builder: (context, state) => const AlertRulesScreen()),
      GoRoute(path: '/whatsapp/summary', builder: (context, state) => const DailySummaryScreen()),
      // Vehicle Detail Route
      GoRoute(path: '/vehicles/:vehicleId', builder: (context, state) {
        final vehicleId = state.pathParameters['vehicleId']!;
        return VehicleDetailScreen(vehicleId: vehicleId);
      }),
      // Driver Detail Route
      GoRoute(path: '/drivers/:driverId', builder: (context, state) {
        final driverId = state.pathParameters['driverId']!;
        return DriverDetailScreen(driverId: driverId);
      }),
    ],
  );
});

class _RouterRefresh extends ChangeNotifier {
  _RouterRefresh(this._ref) {
    _ref.listen(authStateProvider, (_, __) => notifyListeners());
  }

  final Ref _ref;
}
