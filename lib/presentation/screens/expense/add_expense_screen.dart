import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../providers/trips_provider.dart';
import '../../widgets/async_state.dart';

class AddExpenseScreen extends ConsumerStatefulWidget {
  const AddExpenseScreen({super.key});

  @override
  ConsumerState<AddExpenseScreen> createState() => _AddExpenseScreenState();
}

class _AddExpenseScreenState extends ConsumerState<AddExpenseScreen> {
  String? _vehicleId;
  String _fuelType = 'diesel';
  final _amount = TextEditingController();
  final _quantity = TextEditingController(text: '1');
  final _odometer = TextEditingController();
  final _station = TextEditingController();
  bool _saving = false;

  @override
  void dispose() {
    _amount.dispose();
    _quantity.dispose();
    _odometer.dispose();
    _station.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (_vehicleId == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Select a vehicle')));
      return;
    }
    final amount = double.tryParse(_amount.text) ?? 0;
    final qty = double.tryParse(_quantity.text) ?? 0;
    final odo = double.tryParse(_odometer.text) ?? 0;
    if (amount <= 0 || qty <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Enter valid amount and quantity')));
      return;
    }

    setState(() => _saving = true);
    try {
      await ref.read(tripsRepositoryProvider).createFuelRecord(
            vehicleId: _vehicleId!,
            fuelType: _fuelType,
            quantity: qty,
            ratePerLiter: amount / qty,
            totalAmount: amount,
            odometerReading: odo,
            stationName: _station.text.isEmpty ? null : _station.text,
          );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Fuel expense saved')));
        context.pop();
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final vehiclesAsync = ref.watch(vehiclesForFormsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Add Expense'), leading: const BackButton()),
      body: vehiclesAsync.when(
        loading: () => const LoadingView(),
        error: (e, _) => ErrorView(message: e.toString()),
        data: (vehicles) {
          _vehicleId ??= vehicles.isNotEmpty ? vehicles.first.id : null;

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                DropdownButtonFormField<String>(
                  value: _fuelType,
                  decoration: const InputDecoration(labelText: 'Expense Type'),
                  items: const [
                    DropdownMenuItem(value: 'diesel', child: Text('Fuel (Diesel)')),
                    DropdownMenuItem(value: 'petrol', child: Text('Fuel (Petrol)')),
                    DropdownMenuItem(value: 'cng', child: Text('Fuel (CNG)')),
                  ],
                  onChanged: (v) => setState(() => _fuelType = v ?? 'diesel'),
                ),
                const SizedBox(height: 14),
                DropdownButtonFormField<String>(
                  value: _vehicleId,
                  decoration: const InputDecoration(labelText: 'Vehicle'),
                  items: vehicles.map((v) => DropdownMenuItem(value: v.id, child: Text(v.label))).toList(),
                  onChanged: (v) => setState(() => _vehicleId = v),
                ),
                const SizedBox(height: 14),
                TextField(controller: _amount, decoration: const InputDecoration(labelText: 'Total Amount (₹)'), keyboardType: TextInputType.number),
                const SizedBox(height: 14),
                TextField(controller: _quantity, decoration: const InputDecoration(labelText: 'Quantity (Liters)'), keyboardType: TextInputType.number),
                const SizedBox(height: 14),
                TextField(controller: _odometer, decoration: const InputDecoration(labelText: 'Odometer (km)'), keyboardType: TextInputType.number),
                const SizedBox(height: 14),
                TextField(controller: _station, decoration: const InputDecoration(labelText: 'Station Name (optional)')),
                const SizedBox(height: 28),
                ElevatedButton(
                  onPressed: _saving ? null : _save,
                  child: _saving
                      ? const SizedBox(height: 22, width: 22, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                      : const Text('Save Expense'),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
