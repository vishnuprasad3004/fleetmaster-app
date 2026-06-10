import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../config/theme/app_colors.dart';
import '../../../data/models/fuel_model.dart';
import '../../../providers/fuel_provider.dart';
import '../../../utils/formatters.dart';
import '../../widgets/async_state.dart';

class VehicleFuelAnalyticsScreen extends ConsumerWidget {
  const VehicleFuelAnalyticsScreen({super.key, required this.vehicleId});

  final String vehicleId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final analyticsAsync = ref.watch(vehicleFuelAnalyticsProvider(vehicleId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Fuel Analytics'),
      ),
      body: analyticsAsync.when(
        loading: () => const LoadingView(),
        error: (e, _) => ErrorView(message: e.toString(), onRetry: () => ref.invalidate(vehicleFuelAnalyticsProvider(vehicleId))),
        data: (analytics) {
          return RefreshIndicator(
            onRefresh: () => ref.invalidate(vehicleFuelAnalyticsProvider(vehicleId)),
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(analytics.vehicleNumber, style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 24),
                  Row(
                    children: [
                      Expanded(child: _MetricCard(title: 'Total Cost', value: formatCompactCurrency(analytics.totalFuelCost), icon: Icons.account_balance_wallet, color: AppColors.primary)),
                      const SizedBox(width: 12),
                      Expanded(child: _MetricCard(title: 'Total Quantity', value: '${analytics.totalQuantity.toStringAsFixed(0)} L', icon: Icons.local_gas_station, color: AppColors.info)),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(child: _MetricCard(title: 'Avg Mileage', value: '${analytics.averageMileage.toStringAsFixed(1)} km/L', icon: Icons.speed, color: AppColors.success)),
                      const SizedBox(width: 12),
                      Expanded(child: _MetricCard(title: 'Cost/KM', value: '₹${analytics.costPerKm.toStringAsFixed(2)}', icon: Icons.route, color: AppColors.warning)),
                    ],
                  ),
                  const SizedBox(height: 24),
                  Text('Mileage Trend', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
                  const SizedBox(height: 12),
                  _MileageTrendChart(trend: analytics.mileageTrend),
                  const SizedBox(height: 24),
                  Text('Recent Fuel Logs', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
                  const SizedBox(height: 12),
                  ...analytics.fuelLogs.take(5).map((log) => _FuelLogCard(log: log)),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  const _MetricCard({required this.title, required this.value, required this.icon, required this.color});

  final String title;
  final String value;
  final IconData icon;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: color, size: 22),
            const SizedBox(height: 10),
            Text(value, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 2),
            Text(title, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
          ],
        ),
      ),
    );
  }
}

class _MileageTrendChart extends StatelessWidget {
  const _MileageTrendChart({required this.trend});

  final List<double> trend;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: SizedBox(
          height: 120,
          child: trend.isEmpty
              ? const Center(child: Text('No data available', style: TextStyle(color: AppColors.textSecondary)))
              : CustomPaint(
                  painter: _TrendPainter(trend: trend),
                  size: const Size(double.infinity, 120),
                ),
        ),
      ),
    );
  }
}

class _TrendPainter extends CustomPainter {
  _TrendPainter({required this.trend});

  final List<double> trend;

  @override
  void paint(Canvas canvas, Size size) {
    if (trend.isEmpty) return;

    final maxVal = trend.reduce((a, b) => a > b ? a : b);
    final minVal = trend.reduce((a, b) => a < b ? a : b);
    final range = maxVal - minVal == 0 ? 1 : maxVal - minVal;

    final paint = Paint()
      ..color = AppColors.success
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke;

    final fillPaint = Paint()
      ..color = AppColors.success.withValues(alpha: 0.1)
      ..style = PaintingStyle.fill;

    final path = Path();
    final fillPath = Path();

    for (var i = 0; i < trend.length; i++) {
      final x = size.width * (i / (trend.length - 1));
      final y = size.height - ((trend[i] - minVal) / range) * (size.height - 20) - 10;

      if (i == 0) {
        path.moveTo(x, y);
        fillPath.moveTo(x, size.height);
        fillPath.lineTo(x, y);
      } else {
        path.lineTo(x, y);
        fillPath.lineTo(x, y);
      }
    }

    fillPath.lineTo(size.width, size.height);
    fillPath.close();

    canvas.drawPath(fillPaint, fillPaint);
    canvas.drawPath(path, paint);

    for (var i = 0; i < trend.length; i++) {
      final x = size.width * (i / (trend.length - 1));
      final y = size.height - ((trend[i] - minVal) / range) * (size.height - 20) - 10;
      canvas.drawCircle(Offset(x, y), 4, Paint()..color = AppColors.success);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class _FuelLogCard extends StatelessWidget {
  const _FuelLogCard({required this.log});

  final FuelLogModel log;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(formatDate(log.date), style: const TextStyle(fontWeight: FontWeight.w600)),
                Text('${log.quantity.toStringAsFixed(1)} L', style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.w600)),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Icon(Icons.account_balance_wallet, size: 14, color: AppColors.textSecondary),
                const SizedBox(width: 4),
                Text(formatCurrency(log.totalCost), style: const TextStyle(color: AppColors.textSecondary, fontSize: 12)),
                const SizedBox(width: 12),
                Icon(Icons.speed, size: 14, color: AppColors.textSecondary),
                const SizedBox(width: 4),
                Text('${log.mileage.toStringAsFixed(1)} km/L', style: const TextStyle(color: AppColors.textSecondary, fontSize: 12)),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
