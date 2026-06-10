import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/models/trip_model.dart';
import '../data/repositories/trips_repository.dart';
import '../data/repositories/vehicles_repository.dart';

final tripsListProvider = FutureProvider.autoDispose<List<TripModel>>((ref) {
  return ref.watch(tripsRepositoryProvider).getTrips();
});

final tripStatsProvider = FutureProvider.autoDispose<TripStatsModel>((ref) {
  return ref.watch(tripsRepositoryProvider).getStats(days: 30);
});

final profitAnalysisProvider = FutureProvider.autoDispose<ProfitAnalysisModel>((ref) {
  return ref.watch(tripsRepositoryProvider).getProfitAnalysis(days: 30);
});

class ProfitVehicleRank {
  ProfitVehicleRank({required this.registration, required this.profit});

  final String registration;
  final double profit;
}

final profitVehicleRanksProvider = FutureProvider.autoDispose<List<ProfitVehicleRank>>((ref) async {
  final trips = await ref.watch(tripsRepositoryProvider).getTrips();
  final vehicles = await ref.watch(vehiclesRepositoryProvider).getVehicles();
  final regById = {for (final v in vehicles) v.id: v.registrationNumber};

  final profitByVehicle = <String, double>{};
  for (final t in trips) {
    if (t.vehicleId == null || t.profit == null) continue;
    profitByVehicle[t.vehicleId!] = (profitByVehicle[t.vehicleId!] ?? 0) + t.profit!;
  }

  final sorted = profitByVehicle.entries.toList()
    ..sort((a, b) => b.value.compareTo(a.value));

  if (sorted.isNotEmpty) {
    return sorted.take(5).map((e) => ProfitVehicleRank(
          registration: regById[e.key] ?? e.key,
          profit: e.value,
        )).toList();
  }

  final analysis = await ref.watch(tripsRepositoryProvider).getProfitAnalysis(days: 30);
  final ranks = <ProfitVehicleRank>[];
  if (analysis.mostProfitableVehicleId != null && analysis.mostProfitableAmount != 0) {
    ranks.add(ProfitVehicleRank(
      registration: regById[analysis.mostProfitableVehicleId] ?? 'Top vehicle',
      profit: analysis.mostProfitableAmount,
    ));
  }
  if (ranks.isEmpty && vehicles.isNotEmpty) {
    return vehicles.take(3).map((v) => ProfitVehicleRank(registration: v.registrationNumber, profit: 0)).toList();
  }
  return ranks;
});

final vehiclesForFormsProvider = FutureProvider.autoDispose<List<({String id, String label})>>((ref) async {
  final vehicles = await ref.watch(vehiclesRepositoryProvider).getVehicles();
  return vehicles.map((v) => (id: v.id, label: v.registrationNumber)).toList();
});
