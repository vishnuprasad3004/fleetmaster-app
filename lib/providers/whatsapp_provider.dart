import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/models/whatsapp_model.dart';
import '../data/repositories/whatsapp_repository.dart';

final whatsappConfigProvider = FutureProvider.autoDispose<WhatsAppConfigModel>((ref) {
  final repo = ref.watch(whatsappRepositoryProvider);
  return repo.getConfig();
});

final alertRulesProvider = FutureProvider.autoDispose<List<AlertRuleModel>>((ref) {
  final repo = ref.watch(whatsappRepositoryProvider);
  return repo.getAlertRules();
});

final dailySummaryConfigProvider = FutureProvider.autoDispose<DailySummaryConfigModel>((ref) {
  final repo = ref.watch(whatsappRepositoryProvider);
  return repo.getDailySummaryConfig();
});
