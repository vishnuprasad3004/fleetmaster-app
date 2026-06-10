import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/models/vehicle_model.dart';
import '../data/repositories/vehicles_repository.dart';

class VehiclesQuery {
  const VehiclesQuery({this.status, this.search = ''});

  final String? status;
  final String search;

  @override
  bool operator ==(Object other) =>
      other is VehiclesQuery && other.status == status && other.search == search;

  @override
  int get hashCode => Object.hash(status, search);
}

final vehiclesQueryProvider = StateProvider<VehiclesQuery>((ref) => const VehiclesQuery());

final vehiclesListProvider = FutureProvider.autoDispose<List<VehicleModel>>((ref) {
  final query = ref.watch(vehiclesQueryProvider);
  final repo = ref.watch(vehiclesRepositoryProvider);
  return repo.getVehicles(
    status: query.status,
    query: query.search.isEmpty ? null : query.search,
  );
});

final allDocumentsProvider = FutureProvider.autoDispose<List<({VehicleModel vehicle, VehicleDocumentModel doc})>>((ref) async {
  final vehicles = await ref.watch(vehiclesRepositoryProvider).getVehicles();
  final items = <({VehicleModel vehicle, VehicleDocumentModel doc})>[];
  for (final v in vehicles) {
    for (final d in v.documents) {
      items.add((vehicle: v, doc: d));
    }
  }
  return items;
});
