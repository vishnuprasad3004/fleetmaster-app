import 'package:flutter/material.dart';
import '../../../config/theme/app_colors.dart';
import '../../widgets/app_search_bar.dart';
import '../../widgets/status_badge.dart';

/// Customer ledger API is planned — demo data until backend module ships.
class CustomerLedgerScreen extends StatelessWidget {
  const CustomerLedgerScreen({super.key});

  static const _customers = [
    ('Sharma Logistics', '₹1,24,000', 45, BadgeTone.danger),
    ('Patel Transport Co.', '₹86,500', 12, BadgeTone.warning),
    ('Mumbai Freight Ltd.', '₹42,000', 0, BadgeTone.success),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Customer Ledger'), leading: const BackButton()),
      body: Column(
        children: [
          Container(
            width: double.infinity,
            margin: const EdgeInsets.all(16),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(color: AppColors.infoBg, borderRadius: BorderRadius.circular(10)),
            child: const Text(
              'Live ledger sync coming soon. Showing sample data for UI preview.',
              style: TextStyle(fontSize: 12, color: AppColors.info),
            ),
          ),
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 16),
            child: AppSearchBar(hint: 'Search customers...'),
          ),
          const SizedBox(height: 12),
          Expanded(
            child: ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: _customers.length,
              separatorBuilder: (_, __) => const SizedBox(height: 10),
              itemBuilder: (context, i) {
                final (name, amount, days, tone) = _customers[i];
                return Card(
                  child: ListTile(
                    title: Text(name, style: const TextStyle(fontWeight: FontWeight.w600)),
                    subtitle: days > 0
                        ? Text('$days days overdue', style: const TextStyle(color: AppColors.danger, fontSize: 12))
                        : const Text('On time', style: TextStyle(color: AppColors.success, fontSize: 12)),
                    trailing: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(amount, style: const TextStyle(fontWeight: FontWeight.bold)),
                        const SizedBox(height: 4),
                        StatusBadge(label: days > 0 ? 'Overdue' : 'Clear', tone: tone),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
