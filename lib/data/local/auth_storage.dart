import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:hive_flutter/hive_flutter.dart';
import '../../core/constants.dart';
import '../models/user_model.dart';

const _boxName = 'auth_box';

final authStorageProvider = Provider<AuthStorage>((ref) => AuthStorage());

class AuthStorage {
  Box<String>? _box;

  Future<Box<String>> _open() async {
    _box ??= await Hive.openBox<String>(_boxName);
    return _box!;
  }

  Future<void> saveSession({
    required String accessToken,
    required String refreshToken,
    required UserModel user,
  }) async {
    final box = await _open();
    await box.putAll({
      tokenKey: accessToken,
      refreshTokenKey: refreshToken,
      userKey: jsonEncode(user.toJson()),
    });
  }

  Future<String?> getAccessToken() async {
    final box = await _open();
    return box.get(tokenKey);
  }

  Future<UserModel?> getUser() async {
    final box = await _open();
    final raw = box.get(userKey);
    if (raw == null) return null;
    return UserModel.fromJson(jsonDecode(raw) as Map<String, dynamic>);
  }

  Future<bool> hasSession() async {
    final token = await getAccessToken();
    return token != null && token.isNotEmpty;
  }

  Future<void> clear() async {
    final box = await _open();
    await box.deleteAll([tokenKey, refreshTokenKey, userKey]);
  }
}
