import 'dart:convert';
import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

class WebSocketService {
  WebSocketChannel? _channel;
  StreamSubscription? _subscription;
  final StreamController<Map<String, dynamic>> _messageController = StreamController.broadcast();
  bool _isConnected = false;
  String? _accessToken;
  
  static const String wsUrl = 'ws://localhost:8000/ws';

  Stream<Map<String, dynamic>> get messages => _messageController.stream;
  bool get isConnected => _isConnected;

  Future<void> connect(String accessToken) async {
    if (_isConnected) return;

    try {
      _accessToken = accessToken;
      _channel = WebSocketChannel.connect(
        Uri.parse('$wsUrl?token=$accessToken'),
      );

      _subscription = _channel!.stream.listen(
        (data) {
          try {
            final message = jsonDecode(data as String) as Map<String, dynamic>;
            _messageController.add(message);
          } catch (e) {
            print('Error parsing WebSocket message: $e');
          }
        },
        onError: (error) {
          print('WebSocket error: $error');
          _isConnected = false;
          _reconnect();
        },
        onDone: () {
          print('WebSocket connection closed');
          _isConnected = false;
          _reconnect();
        },
      );

      _isConnected = true;
      print('WebSocket connected successfully');
    } catch (e) {
      print('Failed to connect WebSocket: $e');
      _reconnect();
    }
  }

  void _reconnect() async {
    if (!_isConnected && _accessToken != null) {
      await Future.delayed(const Duration(seconds: 5));
      connect(_accessToken!);
    }
  }

  void sendMessage(Map<String, dynamic> message) {
    if (_isConnected && _channel != null) {
      _channel!.sink.add(jsonEncode(message));
    }
  }

  // Subscribe to specific event types
  Stream<Map<String, dynamic>> subscribeToVehicleUpdates() {
    return messages.where((message) => 
        message['type'] == 'vehicle_location_update' || 
        message['type'] == 'vehicle_status_update');
  }

  Stream<Map<String, dynamic>> subscribeToAlerts() {
    return messages.where((message) => 
        message['type'] == 'alert_created' || 
        message['type'] == 'alert_updated');
  }

  Stream<Map<String, dynamic>> subscribeToDashboardUpdates() {
    return messages.where((message) => 
        message['type'] == 'dashboard_update' ||
        message['type'] == 'trip_update' ||
        message['type'] == 'fuel_update' ||
        message['type'] == 'maintenance_update');
  }

  void requestVehicleLocationUpdates() {
    sendMessage({
      'type': 'subscribe',
      'channel': 'vehicle_locations',
    });
  }

  void requestDashboardUpdates() {
    sendMessage({
      'type': 'subscribe',
      'channel': 'dashboard_stats',
    });
  }

  void disconnect() {
    _isConnected = false;
    _subscription?.cancel();
    _channel?.sink.close();
    _messageController.close();
  }
}

// Providers for WebSocket integration
final webSocketServiceProvider = Provider<WebSocketService>((ref) {
  return WebSocketService();
});

final vehicleLocationUpdatesProvider = StreamProvider.autoDispose<Map<String, dynamic>>((ref) {
  final webSocketService = ref.watch(webSocketServiceProvider);
  return webSocketService.subscribeToVehicleUpdates();
});

final dashboardUpdatesProvider = StreamProvider.autoDispose<Map<String, dynamic>>((ref) {
  final webSocketService = ref.watch(webSocketServiceProvider);
  return webSocketService.subscribeToDashboardUpdates();
});

final alertUpdatesProvider = StreamProvider.autoDispose<Map<String, dynamic>>((ref) {
  final webSocketService = ref.watch(webSocketServiceProvider);
  return webSocketService.subscribeToAlerts();
});