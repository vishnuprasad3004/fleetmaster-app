import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../config/theme/app_colors.dart';
import '../../../data/models/fuel_model.dart';
import '../../../providers/fuel_provider.dart';
import '../../../utils/formatters.dart';
import '../../widgets/async_state.dart';

class FuelLogScreen extends ConsumerWidget {
  const FuelLogScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final logsAsync = ref.watch(fuelLogsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Fuel Logs'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => context.push('/fuel/add'),
          ),
        ],
      ),
      body: logsAsync.when(
        loading: () => const LoadingView(),
        error: (e, _) => ErrorView(message: e.toString(), onRetry: () => ref.invalidate(fuelLogsProvider)),
        data: (logs) {
          if (logs.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.local_gas_station_outlined, size: 64, color: AppColors.textMuted),
                  const SizedBox(height: 16),
                  const Text('No fuel logs yet', style: TextStyle(color: AppColors.textSecondary)),
                  const SizedBox(height: 16),
                  ElevatedButton.icon(
                    onPressed: () => context.push('/fuel/add'),
                    icon: const Icon(Icons.add),
                    label: const Text('Add Fuel Entry'),
                  ),
                ],
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: () => ref.invalidate(fuelLogsProvider),
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: logs.length,
              itemBuilder: (context, index) {
                final log = logs[index];
                return _FuelLogCard(log: log);
              },
            ),
          );
        },
      ),
    );
  }
}

class _FuelLogCard extends StatelessWidget {
  const _FuelLogCard({required this.log});

  final FuelLogModel log;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () => _showLogDetails(context, log),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      log.vehicleNumber,
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppColors.primary.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      '${log.quantity.toStringAsFixed(1)} L',
                      style: TextStyle(color: AppColors.primary, fontSize: 11, fontWeight: FontWeight.w600),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.calendar_today, size: 16, color: AppColors.textSecondary),
                  const SizedBox(width: 6),
                  Text(formatDate(log.date), style: const TextStyle(color: AppColors.textSecondary, fontSize: 13)),
                  const SizedBox(width: 16),
                  Icon(Icons.account_balance_wallet, size: 16, color: AppColors.textSecondary),
                  const SizedBox(width: 6),
                  Text(formatCurrency(log.totalCost), style: const TextStyle(color: AppColors.textSecondary, fontSize: 13)),
                ],
              ),
              if (log.fuelStation != null) ...[
                const SizedBox(height: 8),
                Row(
                  children: [
                    Icon(Icons.location_on, size: 16, color: AppColors.textSecondary),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(log.fuelStation!, style: const TextStyle(color: AppColors.textSecondary, fontSize: 13)),
                    ),
                  ],
                ),
              ],
              if (log.odometerReading != null) ...[
                const SizedBox(height: 8),
                Row(
                  children: [
                    Icon(Icons.speed, size: 16, color: AppColors.textSecondary),
                    const SizedBox(width: 6),
                    Text('${formatDistance(log.odometerReading!.toDouble())} km', style: const TextStyle(color: AppColors.textSecondary, fontSize: 13)),
                    const SizedBox(width: 16),
                    Icon(Icons.route, size: 16, color: AppColors.textSecondary),
                    const SizedBox(width: 6),
                    Text('${log.mileage.toStringAsFixed(1)} km/L', style: const TextStyle(color: AppColors.textSecondary, fontSize: 13)),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  void _showLogDetails(BuildContext context, FuelLogModel log) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.5,
        minChildSize: 0.4,
        maxChildSize: 0.9,
        builder: (context, scrollController) => Container(
          decoration: const BoxDecoration(color: Colors.white, borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
          child: ListView(
            controller: scrollController,
            padding: const EdgeInsets.all(20),
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  margin: const EdgeInsets.only(bottom: 20),
                  decoration: BoxDecoration(color: AppColors.border, borderRadius: BorderRadius.circular(2)),
                ),
              ),
              Text(log.vehicleNumber, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              const SizedBox(height: 20),
              _DetailRow(label: 'Date', value: formatDate(log.date)),
              _DetailRow(label: 'Quantity', value: '${log.quantity.toStringAsFixed(1)} L'),
              _DetailRow(label: 'Cost per Liter', value: '₹${log.costPerLiter.toStringAsFixed(2)}'),
              _DetailRow(label: 'Total Cost', value: formatCurrency(log.totalCost)),
              if (log.fuelStation != null) _DetailRow(label: 'Fuel Station', value: log.fuelStation!),
              if (log.fuelType != null) _DetailRow(label: 'Fuel Type', value: log.fuelType!),
              if (log.odometerReading != null) _DetailRow(label: 'Odometer', value: '${formatDistance(log.odometerReading!.toDouble())} km'),
              if (log.mileage > 0) _DetailRow(label: 'Mileage', value: '${log.mileage.toStringAsFixed(1)} km/L'),
              if (log.driverName != null) _DetailRow(label: 'Driver', value: log.driverName!),
            ],
          ),
        ),
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  const _DetailRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: AppColors.textSecondary)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }
}
