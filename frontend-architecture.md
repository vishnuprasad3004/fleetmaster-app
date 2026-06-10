# FleetMaster - Frontend Architecture (Flutter)

## Project Overview

- **Framework**: Flutter (Dart)
- **Platforms**: iOS, Android, Web
- **State Management**: Riverpod + Provider
- **Navigation**: GoRouter
- **UI Framework**: Material Design 3
- **Minimum SDK**: iOS 12.0, Android 21 (API 21)

## Project Structure

```
flutter_app/
├── android/                    # Android native code
├── ios/                        # iOS native code
├── web/                        # Web build files
├── windows/                    # Windows (optional)
├── macos/                      # macOS (optional)
├── lib/
│   ├── main.dart              # App entry point
│   │
│   ├── config/
│   │   ├── app_config.dart           # App configuration
│   │   ├── env_config.dart           # Environment setup
│   │   ├── constants.dart            # App constants
│   │   └── app_theme.dart            # Theme configuration
│   │
│   ├── core/
│   │   ├── di/
│   │   │   ├── service_locator.dart  # Dependency injection setup
│   │   │   └── providers.dart        # Global providers
│   │   │
│   │   ├── providers/
│   │   │   ├── auth_provider.dart    # Auth state
│   │   │   ├── fleet_provider.dart   # Fleet state
│   │   │   ├── user_provider.dart    # User state
│   │   │   └── settings_provider.dart # Settings state
│   │   │
│   │   ├── services/
│   │   │   ├── api_service.dart      # HTTP client
│   │   │   ├── local_storage_service.dart
│   │   │   ├── notification_service.dart
│   │   │   ├── location_service.dart
│   │   │   ├── connectivity_service.dart
│   │   │   └── analytics_service.dart
│   │   │
│   │   ├── errors/
│   │   │   ├── exceptions.dart       # Custom exceptions
│   │   │   ├── error_handler.dart    # Error handling
│   │   │   └── failure.dart          # Failure models
│   │   │
│   │   ├── utils/
│   │   │   ├── logger.dart           # Logging utility
│   │   │   ├── validators.dart       # Input validators
│   │   │   ├── formatters.dart       # Data formatters
│   │   │   ├── date_utils.dart       # Date utilities
│   │   │   └── math_utils.dart       # Math utilities
│   │   │
│   │   ├── extensions/
│   │   │   ├── string_extension.dart
│   │   │   ├── date_extension.dart
│   │   │   ├── context_extension.dart
│   │   │   ├── build_context_extension.dart
│   │   │   └── num_extension.dart
│   │   │
│   │   └── constants/
│   │       ├── api_constants.dart
│   │       ├── app_strings.dart
│   │       └── dimensions.dart
│   │
│   ├── data/
│   │   ├── datasources/
│   │   │   ├── local/
│   │   │   │   ├── local_data_source.dart
│   │   │   │   ├── user_local_data_source.dart
│   │   │   │   ├── fleet_local_data_source.dart
│   │   │   │   └── hive_boxes.dart
│   │   │   │
│   │   │   └── remote/
│   │   │       ├── api_client.dart
│   │   │       ├── auth_api_client.dart
│   │   │       ├── fleet_api_client.dart
│   │   │       ├── vehicle_api_client.dart
│   │   │       ├── tracking_api_client.dart
│   │   │       └── analytics_api_client.dart
│   │   │
│   │   ├── models/
│   │   │   ├── user/
│   │   │   │   ├── user_model.dart
│   │   │   │   ├── login_response.dart
│   │   │   │   └── user_profile.dart
│   │   │   │
│   │   │   ├── fleet/
│   │   │   │   ├── fleet_model.dart
│   │   │   │   ├── fleet_member.dart
│   │   │   │   └── fleet_stats.dart
│   │   │   │
│   │   │   ├── vehicle/
│   │   │   │   ├── vehicle_model.dart
│   │   │   │   ├── vehicle_status.dart
│   │   │   │   └── vehicle_details.dart
│   │   │   │
│   │   │   ├── driver/
│   │   │   │   ├── driver_model.dart
│   │   │   │   └── driver_stats.dart
│   │   │   │
│   │   │   ├── tracking/
│   │   │   │   ├── gps_point.dart
│   │   │   │   ├── geofence_model.dart
│   │   │   │   └── geofence_alert.dart
│   │   │   │
│   │   │   ├── trip/
│   │   │   │   ├── trip_model.dart
│   │   │   │   └── trip_details.dart
│   │   │   │
│   │   │   └── common/
│   │   │       ├── paginated_response.dart
│   │   │       ├── api_response.dart
│   │   │       └── error_response.dart
│   │   │
│   │   ├── repositories/
│   │   │   ├── auth_repository.dart
│   │   │   ├── fleet_repository.dart
│   │   │   ├── vehicle_repository.dart
│   │   │   ├── driver_repository.dart
│   │   │   ├── tracking_repository.dart
│   │   │   ├── trip_repository.dart
│   │   │   ├── analytics_repository.dart
│   │   │   └── user_repository.dart
│   │   │
│   │   └── local/
│   │       ├── hive_adapters.dart
│   │       └── sqlite_helper.dart
│   │
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── user_entity.dart
│   │   │   ├── fleet_entity.dart
│   │   │   ├── vehicle_entity.dart
│   │   │   ├── driver_entity.dart
│   │   │   ├── trip_entity.dart
│   │   │   └── tracking_entity.dart
│   │   │
│   │   └── usecases/
│   │       ├── auth/
│   │       │   ├── login_usecase.dart
│   │       │   ├── register_usecase.dart
│   │       │   ├── logout_usecase.dart
│   │       │   └── get_current_user_usecase.dart
│   │       │
│   │       ├── fleet/
│   │       │   ├── get_fleets_usecase.dart
│   │       │   ├── create_fleet_usecase.dart
│   │       │   ├── get_fleet_details_usecase.dart
│   │       │   └── update_fleet_usecase.dart
│   │       │
│   │       ├── vehicle/
│   │       │   ├── get_vehicles_usecase.dart
│   │       │   ├── add_vehicle_usecase.dart
│   │       │   ├── get_vehicle_status_usecase.dart
│   │       │   └── update_vehicle_usecase.dart
│   │       │
│   │       └── tracking/
│   │           ├── get_live_tracking_usecase.dart
│   │           ├── get_tracking_history_usecase.dart
│   │           └── create_geofence_usecase.dart
│   │
│   ├── presentation/
│   │   ├── widgets/
│   │   │   ├── common/
│   │   │   │   ├── app_bar_widget.dart
│   │   │   │   ├── bottom_nav_bar.dart
│   │   │   │   ├── loading_widget.dart
│   │   │   │   ├── error_widget.dart
│   │   │   │   ├── empty_state_widget.dart
│   │   │   │   ├── custom_button.dart
│   │   │   │   ├── custom_text_field.dart
│   │   │   │   ├── custom_card.dart
│   │   │   │   ├── dialog_widget.dart
│   │   │   │   ├── bottom_sheet_widget.dart
│   │   │   │   └── avatar_widget.dart
│   │   │   │
│   │   │   ├── fleet/
│   │   │   │   ├── fleet_card.dart
│   │   │   │   ├── fleet_list_item.dart
│   │   │   │   └── fleet_header.dart
│   │   │   │
│   │   │   ├── vehicle/
│   │   │   │   ├── vehicle_card.dart
│   │   │   │   ├── vehicle_list_item.dart
│   │   │   │   ├── vehicle_status_indicator.dart
│   │   │   │   └── vehicle_info_card.dart
│   │   │   │
│   │   │   ├── tracking/
│   │   │   │   ├── map_widget.dart
│   │   │   │   ├── vehicle_marker.dart
│   │   │   │   ├── geofence_widget.dart
│   │   │   │   └── tracking_controls.dart
│   │   │   │
│   │   │   └── common_widgets.dart
│   │   │
│   │   ├── screens/
│   │   │   ├── auth/
│   │   │   │   ├── login_screen.dart
│   │   │   │   ├── register_screen.dart
│   │   │   │   ├── forgot_password_screen.dart
│   │   │   │   ├── verify_email_screen.dart
│   │   │   │   ├── two_factor_screen.dart
│   │   │   │   └── splash_screen.dart
│   │   │   │
│   │   │   ├── home/
│   │   │   │   ├── home_screen.dart
│   │   │   │   ├── dashboard_screen.dart
│   │   │   │   ├── alerts_screen.dart
│   │   │   │   └── quick_actions_screen.dart
│   │   │   │
│   │   │   ├── fleet/
│   │   │   │   ├── fleet_list_screen.dart
│   │   │   │   ├── fleet_detail_screen.dart
│   │   │   │   ├── add_fleet_screen.dart
│   │   │   │   ├── edit_fleet_screen.dart
│   │   │   │   ├── fleet_members_screen.dart
│   │   │   │   ├── add_member_screen.dart
│   │   │   │   └── fleet_settings_screen.dart
│   │   │   │
│   │   │   ├── vehicles/
│   │   │   │   ├── vehicle_list_screen.dart
│   │   │   │   ├── vehicle_detail_screen.dart
│   │   │   │   ├── add_vehicle_screen.dart
│   │   │   │   ├── edit_vehicle_screen.dart
│   │   │   │   ├── vehicle_status_screen.dart
│   │   │   │   └── vehicle_history_screen.dart
│   │   │   │
│   │   │   ├── drivers/
│   │   │   │   ├── driver_list_screen.dart
│   │   │   │   ├── driver_detail_screen.dart
│   │   │   │   ├── add_driver_screen.dart
│   │   │   │   ├── edit_driver_screen.dart
│   │   │   │   └── driver_performance_screen.dart
│   │   │   │
│   │   │   ├── tracking/
│   │   │   │   ├── map_screen.dart
│   │   │   │   ├── vehicle_tracking_screen.dart
│   │   │   │   ├── geofence_list_screen.dart
│   │   │   │   ├── add_geofence_screen.dart
│   │   │   │   └── geofence_details_screen.dart
│   │   │   │
│   │   │   ├── trips/
│   │   │   │   ├── trip_list_screen.dart
│   │   │   │   ├── trip_detail_screen.dart
│   │   │   │   ├── create_trip_screen.dart
│   │   │   │   ├── trip_tracking_screen.dart
│   │   │   │   └── trip_analytics_screen.dart
│   │   │   │
│   │   │   ├── maintenance/
│   │   │   │   ├── maintenance_schedule_screen.dart
│   │   │   │   ├── maintenance_tasks_screen.dart
│   │   │   │   ├── create_task_screen.dart
│   │   │   │   ├── maintenance_records_screen.dart
│   │   │   │   └── create_record_screen.dart
│   │   │   │
│   │   │   ├── analytics/
│   │   │   │   ├── analytics_dashboard_screen.dart
│   │   │   │   ├── vehicle_analytics_screen.dart
│   │   │   │   ├── driver_analytics_screen.dart
│   │   │   │   ├── fuel_analytics_screen.dart
│   │   │   │   ├── report_generator_screen.dart
│   │   │   │   └── report_viewer_screen.dart
│   │   │   │
│   │   │   └── settings/
│   │   │       ├── settings_screen.dart
│   │   │       ├── profile_screen.dart
│   │   │       ├── notification_settings_screen.dart
│   │   │       ├── security_settings_screen.dart
│   │   │       ├── integration_settings_screen.dart
│   │   │       └── about_screen.dart
│   │   │
│   │   ├── controllers/
│   │   │   ├── auth_controller.dart
│   │   │   ├── fleet_controller.dart
│   │   │   ├── vehicle_controller.dart
│   │   │   ├── tracking_controller.dart
│   │   │   ├── trip_controller.dart
│   │   │   ├── analytics_controller.dart
│   │   │   └── settings_controller.dart
│   │   │
│   │   ├── themes/
│   │   │   ├── app_colors.dart
│   │   │   ├── app_text_styles.dart
│   │   │   ├── app_theme.dart
│   │   │   └── responsive_sizes.dart
│   │   │
│   │   └── navigation/
│   │       ├── app_router.dart
│   │       ├── route_names.dart
│   │       └── route_transitions.dart
│   │
│   ├── features/ (Feature-specific code)
│   │   ├── auth/
│   │   ├── fleet/
│   │   ├── vehicles/
│   │   ├── tracking/
│   │   ├── maintenance/
│   │   ├── drivers/
│   │   ├── trips/
│   │   └── analytics/
│   │
│   └── main.dart
│
├── test/                       # Unit & Widget tests
│   ├── unit/
│   ├── widget/
│   └── integration/
│
├── pubspec.yaml               # Flutter dependencies
├── pubspec.lock
├── analysis_options.yaml       # Linting rules
└── README.md
```

## State Management (Riverpod)

### Auth Provider Example

```dart
// lib/core/providers/auth_provider.dart

final authServiceProvider = Provider((ref) => AuthService());

final authStateProvider = StateNotifierProvider<AuthStateNotifier, AuthState>(
  (ref) => AuthStateNotifier(ref.watch(authServiceProvider)),
);

final currentUserProvider = FutureProvider<User?>((ref) {
  final authService = ref.watch(authServiceProvider);
  return authService.getCurrentUser();
});
```

### Fleet Provider Example

```dart
final fleetsProvider = FutureProvider.family<List<Fleet>, String>(
  (ref, fleetFilter) async {
    final fleetService = ref.watch(fleetServiceProvider);
    return fleetService.getFleets(filter: fleetFilter);
  },
);

final selectedFleetProvider = StateProvider<Fleet?>((ref) => null);

final fleetMembersProvider = FutureProvider.family<List<FleetMember>, String>(
  (ref, fleetId) async {
    final fleetService = ref.watch(fleetServiceProvider);
    return fleetService.getFleetMembers(fleetId);
  },
);
```

## Navigation Structure (GoRouter)

```dart
// lib/presentation/navigation/app_router.dart

final appRouterProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authStateProvider);
  
  return GoRouter(
    initialLocation: authState.isLoading ? '/splash' : '/login',
    routes: [
      GoRoute(
        path: '/splash',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/register',
        builder: (context, state) => const RegisterScreen(),
      ),
      ShellRoute(
        builder: (context, state, child) => MainLayout(child: child),
        routes: [
          GoRoute(
            path: '/home',
            builder: (context, state) => const HomeScreen(),
          ),
          GoRoute(
            path: '/fleets',
            builder: (context, state) => const FleetListScreen(),
            routes: [
              GoRoute(
                path: ':fleetId',
                builder: (context, state) => FleetDetailScreen(
                  fleetId: state.params['fleetId']!,
                ),
              ),
            ],
          ),
          GoRoute(
            path: '/vehicles',
            builder: (context, state) => const VehicleListScreen(),
          ),
          GoRoute(
            path: '/tracking',
            builder: (context, state) => const MapScreen(),
          ),
          GoRoute(
            path: '/analytics',
            builder: (context, state) => const AnalyticsDashboardScreen(),
          ),
        ],
      ),
    ],
  );
});
```

## Key Dependencies

```yaml
dependencies:
  # Core
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.0
  
  # State Management
  riverpod: ^2.4.0
  riverpod_annotation: ^2.3.0
  flutter_riverpod: ^2.4.0
  
  # Navigation
  go_router: ^11.0.0
  
  # HTTP & API
  dio: ^5.3.0
  retrofit: ^4.1.0
  
  # Local Storage
  hive: ^2.2.0
  hive_flutter: ^1.1.0
  sqflite: ^2.3.0
  
  # UI & Design
  google_fonts: ^6.1.0
  animations: ^2.0.0
  cached_network_image: ^3.3.0
  
  # Maps & Location
  google_maps_flutter: ^2.5.0
  geolocator: ^10.1.0
  location: ^5.0.0
  geocoding: ^3.0.0
  
  # Utilities
  intl: ^0.19.0
  uuid: ^4.0.0
  timeago: ^3.5.0
  
  # Logging
  logger: ^2.1.0
  
  # JSON Serialization
  json_serializable: ^6.7.0
  json_annotation: ^4.8.0
  
  # Firebase (Phase 2)
  firebase_core: ^2.20.0
  firebase_messaging: ^14.6.0
  firebase_analytics: ^10.4.0
  
  # Charts (Phase 2)
  fl_chart: ^0.63.0
  
  # PDF & Export (Phase 2)
  pdf: ^3.10.0
  printing: ^5.11.0
  
dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0
  build_runner: ^2.4.0
  riverpod_generator: ^2.3.0
  retrofit_generator: ^7.0.0
```

## Responsive Design

```dart
// lib/presentation/themes/responsive_sizes.dart

class ResponsiveSizes {
  static double getScreenWidth(BuildContext context) {
    return MediaQuery.of(context).size.width;
  }
  
  static bool isMobile(BuildContext context) {
    return getScreenWidth(context) < 600;
  }
  
  static bool isTablet(BuildContext context) {
    final width = getScreenWidth(context);
    return width >= 600 && width < 1200;
  }
  
  static bool isDesktop(BuildContext context) {
    return getScreenWidth(context) >= 1200;
  }
  
  static double getPadding(BuildContext context) {
    if (isMobile(context)) return 16;
    if (isTablet(context)) return 24;
    return 32;
  }
}
```

## Offline Support Strategy

- **Local Storage**: Hive for app state and small data
- **SQLite**: For larger datasets, GPS traces
- **Sync Queue**: Queue for pending updates
- **Conflict Resolution**: Last-write-wins strategy

```dart
// lib/core/services/sync_service.dart

class SyncService {
  Future<void> syncPendingChanges() async {
    final pendingTrips = await _getTripSync.getAll();
    final pendingUpdates = await _getVehicleSync.getAll();
    
    try {
      // Sync trips
      for (final trip in pendingTrips) {
        await _tripRepository.syncTrip(trip);
        await _tripSync.delete(trip.id);
      }
      
      // Sync vehicle updates
      for (final update in pendingUpdates) {
        await _vehicleRepository.syncUpdate(update);
        await _vehicleSync.delete(update.id);
      }
    } catch (e) {
      Logger.e('Sync failed', error: e);
      // Retry on next connectivity
    }
  }
}
```

## Testing Strategy

### Unit Tests
- Service/Repository logic
- Utility functions
- Validators

### Widget Tests
- Individual widgets
- Screen layouts
- User interactions

### Integration Tests
- Full feature flows
- API integration
- State management

```dart
// test/unit/validators_test.dart

void main() {
  group('Email Validator', () {
    test('valid email passes', () {
      expect(Validators.isValidEmail('test@example.com'), true);
    });
    
    test('invalid email fails', () {
      expect(Validators.isValidEmail('invalid-email'), false);
    });
  });
}
```

## Performance Optimization

1. **Image Optimization**
   - Use cached network images
   - Compress locally
   - Lazy load lists

2. **State Management**
   - Only rebuild when necessary
   - Use selectors for partial updates
   - Implement .select() for providers

3. **Build Optimization**
   - Code splitting with feature modules
   - Tree shaking unused code
   - ProGuard rules for Android

4. **Memory Management**
   - Dispose controllers properly
   - Clear cached data
   - Monitor memory usage

## Accessibility

- Use semantic widgets
- Provide meaningful labels
- Ensure sufficient color contrast
- Support screen readers
- Keyboard navigation support

---

This architecture provides a scalable, maintainable Flutter application with best practices for state management, navigation, and testing.
