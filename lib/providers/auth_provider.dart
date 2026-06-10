import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hive/hive.dart';
import '../data/services/api_service.dart';

// Auth state model
class AuthState {
  final User? user;
  final String? accessToken;
  final String? refreshToken;
  final bool isLoading;
  final String? error;

  AuthState({
    this.user,
    this.accessToken,
    this.refreshToken,
    this.isLoading = false,
    this.error,
  });

  AuthState copyWith({
    User? user,
    String? accessToken,
    String? refreshToken,
    bool? isLoading,
    String? error,
  }) {
    return AuthState(
      user: user ?? this.user,
      accessToken: accessToken ?? this.accessToken,
      refreshToken: refreshToken ?? this.refreshToken,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

class User {
  final String id;
  final String email;
  final String firstName;
  final String lastName;
  final String? businessName;

  User({
    required this.id,
    required this.email,
    required this.firstName,
    required this.lastName,
    this.businessName,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      email: json['email'],
      firstName: json['first_name'],
      lastName: json['last_name'],
      businessName: json['business_name'],
    );
  }

  String get fullName => '$firstName $lastName';
}

// Auth notifier
class AuthNotifier extends StateNotifier<AuthState> {
  final ApiService _apiService;
  final Box _secureBox;

  AuthNotifier(this._apiService, this._secureBox) : super(AuthState()) {
    _loadSavedAuth();
  }

  Future<void> _loadSavedAuth() async {
    final token = _secureBox.get('access_token');
    final refreshToken = _secureBox.get('refresh_token');
    final userJson = _secureBox.get('user');

    if (token != null && userJson != null) {
      final user = User.fromJson(Map<String, dynamic>.from(userJson));
      state = state.copyWith(
        user: user,
        accessToken: token,
        refreshToken: refreshToken,
      );
    }
  }

  Future<void> login(String email, String password) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final response = await _apiService.login(email, password);
      
      final user = User.fromJson(response['user']);
      final accessToken = response['access_token'];
      final refreshToken = response['refresh_token'];

      // Save to secure storage
      await _secureBox.put('access_token', accessToken);
      await _secureBox.put('refresh_token', refreshToken);
      await _secureBox.put('user', response['user']);

      state = state.copyWith(
        user: user,
        accessToken: accessToken,
        refreshToken: refreshToken,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
      rethrow;
    }
  }

  Future<void> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    String? businessName,
  }) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final response = await _apiService.register(
        email: email,
        password: password,
        firstName: firstName,
        lastName: lastName,
        businessName: businessName,
      );

      final user = User.fromJson(response['user']);
      final accessToken = response['access_token'];
      final refreshToken = response['refresh_token'];

      // Save to secure storage
      await _secureBox.put('access_token', accessToken);
      await _secureBox.put('refresh_token', refreshToken);
      await _secureBox.put('user', response['user']);

      state = state.copyWith(
        user: user,
        accessToken: accessToken,
        refreshToken: refreshToken,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
      rethrow;
    }
  }

  Future<void> logout() async {
    // Clear secure storage
    await _secureBox.delete('access_token');
    await _secureBox.delete('refresh_token');
    await _secureBox.delete('user');

    state = AuthState();
  }

  Future<void> refreshToken() async {
    final refreshToken = state.refreshToken;
    if (refreshToken == null) {
      await logout();
      return;
    }

    try {
      // Implement refresh token logic with your backend
      // final response = await _apiService.refreshToken(refreshToken);
      // Update tokens...
    } catch (e) {
      await logout();
    }
  }
}

// Providers
final secureBoxProvider = Provider<Box>((ref) {
  throw UnimplementedError('secureBoxProvider must be initialized');
});

final authNotifierProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final apiService = ref.watch(apiServiceProvider);
  final secureBox = ref.watch(secureBoxProvider);
  return AuthNotifier(apiService, secureBox);
});

final authStateProvider = Provider<AuthState>((ref) {
  return ref.watch(authNotifierProvider);
});

final isLoggedInProvider = Provider<bool>((ref) {
  return ref.watch(authStateProvider).user != null;
});