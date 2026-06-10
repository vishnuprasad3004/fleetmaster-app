import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../config/theme/app_colors.dart';
import '../../../providers/fuel_provider.dart';
import '../../../utils/formatters.dart';
import '../../widgets/async_state.dart';
import '../../widgets/dashboard_header.dart';

class FuelDashboardScreen extends ConsumerWidget {
  const FuelDashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dashboardAsync = ref.watch(fuelDashboardProvider);

    return Scaffold(
      appBar: DashboardHeader(
        title: 'Fuel Management',
        onNotificationTap: () => context.push('/alerts'),
      ),
      body: dashboardAsync.when(
        loading: () => const LoadingView(),
        error: (e, _) => ErrorView(message: e.toString(), onRetry: () => ref.invalidate(fuelDashboardProvider)),
        data: (dashboard) {
          return RefreshIndicator(
            onRefresh: () => ref.invalidate(fuelDashboardProvider),
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _BusinessInsightCard(
                    vehicleNumber: dashboard.worstMileageVehicle.vehicleNumber,
                    mileageChange: dashboard.worstMileageVehicle.mileageChange,
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(child: _MetricCard(title: 'Total Fuel Cost (30d)', value: formatCompactCurrency(dashboard.totalFuelCost), icon: Icons.account_balance_wallet, color: AppColors.primary)),
                      const SizedBox(width: 12),
                      Expanded(child: _MetricCard(title: 'Total Quantity', value: '${dashboard.totalQuantity.toStringAsFixed(0)} L', icon: Icons.local_gas_station, color: AppColors.info)),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(child: _MetricCard(title: 'Avg Mileage', value: '${dashboard.averageMileage.toStringAsFixed(1)} km/L', icon: Icons.speed, color: AppColors.success)),
                      const SizedBox(width: 12),
                      Expanded(child: _MetricCard(title: 'Cost/KM', value: '₹${(dashboard.totalFuelCost / (dashboard.totalQuantity * dashboard.averageMileage)).toStringAsFixed(2)}', icon: Icons.route, color: AppColors.warning)),
                    ],
                  ),
                  const SizedBox(height: 24),
                  Text('Best Performing Vehicle', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
                  const SizedBox(height: 12),
                  _VehiclePerformanceCard(
                    vehicleNumber: dashboard.bestMileageVehicle.vehicleNumber,
                    mileage: dashboard.bestMileageVehicle.mileage,
                    change: dashboard.bestMileageVehicle.mileageChange,
                    cost: dashboard.bestMileageVehicle.totalCost,
                    isBest: true,
                  ),
                  const SizedBox(height: 16),
                  Text('Lowest Performing Vehicle', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
                  const SizedBox(height: 12),
                  _VehiclePerformanceCard(
                    vehicleNumber: dashboard.worstMileageVehicle.vehicleNumber,
                    mileage: dashboard.worstMileageVehicle.mileage,
                    change: dashboard.worstMileageVehicle.mileageChange,
                    cost: dashboard.worstMileageVehicle.totalCost,
                    isBest: false,
                  ),
                  const SizedBox(height: 24),
                  Text('Cost Trend (Last 7 Days)', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
                  const SizedBox(height: 12),
                  _CostTrendChart(trend: dashboard.costTrend),
                  const SizedBox(height: 24),
                  ElevatedButton.icon(
                    onPressed: () => context.push('/fuel/add'),
                    icon: const Icon(Icons.add),
                    label: const Text('Add Fuel Entry'),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

class _BusinessInsightCard extends StatelessWidget {
  const _BusinessInsightCard({required this.vehicleNumber, required this.mileageChange});

  final String vehicleNumber;
  final double mileageChange;

  @override
  Widget build(BuildContext context) {
    final isDecrease = mileageChange < 0;
    final color = isDecrease ? AppColors.danger : AppColors.success;
    final icon = isDecrease ? Icons.trending_down : Icons.trending_up;
    final text = isDecrease ? 'dropped' : 'improved';

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              'Vehicle $vehicleNumber fuel efficiency $text ${mileageChange.abs().toStringAsFixed(1)}%.',
              style: TextStyle(color: color, fontWeight: FontWeight.w500, fontSize: 14),
            ),
          ),
        ],
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

class _VehiclePerformanceCard extends StatelessWidget {
  const _VehiclePerformanceCard({required this.vehicleNumber, required this.mileage, required this.change, required this.cost, required this.isBest});

  final String vehicleNumber;
  final double mileage;
  final double change;
  final double cost;
  final bool isBest;

  @override
  Widget build(BuildContext context) {
    final color = isBest ? AppColors.success : AppColors.danger;
    final icon = isBest ? Icons.emoji_events : Icons.warning;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: color, size: 20),
                const SizedBox(width: 8),
                Text(vehicleNumber, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Mileage', style: TextStyle(color: AppColors.textSecondary)),
                Text('${mileage.toStringAsFixed(1)} km/L', style: const TextStyle(fontWeight: FontWeight.w600)),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Change', style: TextStyle(color: AppColors.textSecondary)),
                Text('${change > 0 ? '+' : ''}${change.toStringAsFixed(1)}%', style: TextStyle(color: change >= 0 ? AppColors.success : AppColors.danger, fontWeight: FontWeight.w600)),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Fuel Cost', style: TextStyle(color: AppColors.textSecondary)),
                Text(formatCompactCurrency(cost), style: const TextStyle(fontWeight: FontWeight.w600)),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _CostTrendChart extends StatelessWidget {
  const _CostTrendChart({required this.trend});

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
      ..color = AppColors.primary
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke;

    final fillPaint = Paint()
      ..color = AppColors.primary.withValues(alpha: 0.1)
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
      canvas.drawCircle(Offset(x, y), 4, Paint()..color = AppColors.primary);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
