// API Configuration
const String apiBaseUrl = 'http://localhost:8000';
const String apiVersion = '/v1';

// Timeouts
const int connectTimeout = 10000; // 10 seconds
const int receiveTimeout = 10000; // 10 seconds

// Storage Keys
const String tokenKey = 'access_token';
const String refreshTokenKey = 'refresh_token';
const String userKey = 'user';

// Durations
const Duration tokenRefreshThreshold = Duration(minutes: 1);
const Duration apiRetryDelay = Duration(seconds: 1);

// UI Constants
const double defaultPadding = 16.0;
const double defaultBorderRadius = 12.0;
const double defaultElevation = 2.0;
