import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/models/driver_model.dart';
import '../data/repositories/drivers_repository.dart';

class DriversQuery {
  const DriversQuery({this.status, this.search = ''});

  final String? status;
  final String search;

  @override
  bool operator ==(Object other) =>
      other is DriversQuery && other.status == status && other.search == search;

  @override
  int get hashCode => Object.hash(status, search);
}

final driversQueryProvider = StateProvider<DriversQuery>((ref) => const DriversQuery());

final driversListProvider = FutureProvider.autoDispose<List<DriverModel>>((ref) {
  final query = ref.watch(driversQueryProvider);
  return ref.watch(driversRepositoryProvider).getDrivers(
        status: query.status,
        query: query.search.isEmpty ? null : query.search,
      );
});
