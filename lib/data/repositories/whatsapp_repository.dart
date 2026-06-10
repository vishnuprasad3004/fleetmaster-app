import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/network/api_client.dart';
import '../models/whatsapp_model.dart';

final whatsappRepositoryProvider = Provider<WhatsAppRepository>((ref) {
  return WhatsAppRepository(ref.watch(dioProvider));
});

class WhatsAppRepository {
  WhatsAppRepository(this._dio);

  final Dio _dio;

  Future<WhatsAppConfigModel> getConfig() async {
    return apiCall(() async {
      final res = await _dio.get('/whatsapp/config');
      return WhatsAppConfigModel.fromJson(res.data);
    });
  }

  Future<WhatsAppConfigModel> updateConfig(WhatsAppConfigModel config) async {
    return apiCall(() async {
      final res = await _dio.put('/whatsapp/config', data: config.toJson());
      return WhatsAppConfigModel.fromJson(res.data);
    });
  }

  Future<List<AlertRuleModel>> getAlertRules() async {
    return apiCall(() async {
      final res = await _dio.get('/whatsapp/alert-rules');
      final rules = res.data['rules'] as List<dynamic>;
      return rules.map((e) => AlertRuleModel.fromJson(e as Map<String, dynamic>)).toList();
    });
  }

  Future<AlertRuleModel> updateAlertRule(String id, AlertRuleModel rule) async {
    return apiCall(() async {
      final res = await _dio.put('/whatsapp/alert-rules/$id', data: rule.toJson());
      return AlertRuleModel.fromJson(res.data);
    });
  }

  Future<DailySummaryConfigModel> getDailySummaryConfig() async {
    return apiCall(() async {
      final res = await _dio.get('/whatsapp/daily-summary');
      return DailySummaryConfigModel.fromJson(res.data);
    });
  }

  Future<DailySummaryConfigModel> updateDailySummaryConfig(DailySummaryConfigModel config) async {
    return apiCall(() async {
      final res = await _dio.put('/whatsapp/daily-summary', data: config.toJson());
      return DailySummaryConfigModel.fromJson(res.data);
    });
  }

  Future<void> sendTestMessage() async {
    return apiCall(() async {
      await _dio.post('/whatsapp/test');
    });
  }
}
