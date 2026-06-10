import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../config/theme/app_colors.dart';
import '../../../data/models/fuel_model.dart';
import '../../../data/models/vehicle_model.dart';
import '../../../data/models/driver_model.dart';
import '../../../providers/fuel_provider.dart';
import '../../../providers/vehicles_provider.dart';
import '../../../providers/drivers_provider.dart';
import '../../widgets/async_state.dart';

class AddFuelScreen extends ConsumerStatefulWidget {
  const AddFuelScreen({super.key});

  @override
  ConsumerState<AddFuelScreen> createState() => _AddFuelScreenState();
}

class _AddFuelScreenState extends ConsumerState<AddFuelScreen> {
  final _formKey = GlobalKey<FormState>();
  final _vehicleController = TextEditingController();
  final _dateController = TextEditingController();
  final _quantityController = TextEditingController();
  final _costPerLiterController = TextEditingController();
  final _totalCostController = TextEditingController();
  final _odometerController = TextEditingController();
  final _fuelStationController = TextEditingController();
  final _fuelTypeController = TextEditingController();
  final _driverController = TextEditingController();

  VehicleModel? _selectedVehicle;
  DriverModel? _selectedDriver;

  @override
  void dispose() {
    _vehicleController.dispose();
    _dateController.dispose();
    _quantityController.dispose();
    _costPerLiterController.dispose();
    _totalCostController.dispose();
    _odometerController.dispose();
    _fuelStationController.dispose();
    _fuelTypeController.dispose();
    _driverController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final vehiclesAsync = ref.watch(vehiclesListProvider);
    final driversAsync = ref.watch(driversListProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Add Fuel Entry'),
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            vehiclesAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => ErrorView(message: e.toString(), onRetry: () => ref.invalidate(vehiclesListProvider)),
              data: (vehicles) {
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildVehicleDropdown(vehicles),
                    const SizedBox(height: 16),
                    _buildDateField(),
                    const SizedBox(height: 16),
                    _buildQuantityField(),
                    const SizedBox(height: 16),
                    _buildCostFields(),
                    const SizedBox(height: 16),
                    _buildOdometerField(),
                    const SizedBox(height: 16),
                    _buildFuelStationField(),
                    const SizedBox(height: 16),
                    _buildFuelTypeField(),
                    const SizedBox(height: 16),
                    driversAsync.when(
                      loading: () => const SizedBox.shrink(),
                      error: (_, __) => const SizedBox.shrink(),
                      data: (drivers) {
                        return _buildDriverDropdown(drivers);
                      },
                    ),
                    const SizedBox(height: 24),
                    ElevatedButton(
                      onPressed: _submitForm,
                      child: const Text('Save Fuel Entry'),
                    ),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildVehicleDropdown(List<VehicleModel> vehicles) {
    return DropdownButtonFormField<VehicleModel>(
      decoration: const InputDecoration(
        labelText: 'Select Vehicle',
        prefixIcon: Icon(Icons.local_shipping),
      ),
      items: vehicles.map((v) {
        return DropdownMenuItem(
          value: v,
          child: Text('${v.registrationNumber} - ${v.displayName}'),
        );
      }).toList(),
      onChanged: (value) {
        setState(() {
          _selectedVehicle = value;
          _vehicleController.text = value?.registrationNumber ?? '';
        });
      },
      validator: (value) => value == null ? 'Please select a vehicle' : null,
    );
  }

  Widget _buildDateField() {
    return TextFormField(
      controller: _dateController,
      decoration: const InputDecoration(
        labelText: 'Fuel Date',
        prefixIcon: Icon(Icons.calendar_today),
        suffixIcon: Icon(Icons.arrow_drop_down),
      ),
      readOnly: true,
      onTap: () async {
        final date = await showDatePicker(
          context: context,
          initialDate: DateTime.now(),
          firstDate: DateTime.now().subtract(const Duration(days: 30)),
          lastDate: DateTime.now().add(const Duration(days: 1)),
        );
        if (date != null) {
          _dateController.text = date.toIso8601String().split('T')[0];
        }
      },
      validator: (value) => value?.isEmpty ?? true ? 'Please select a date' : null,
    );
  }

  Widget _buildQuantityField() {
    return TextFormField(
      controller: _quantityController,
      decoration: const InputDecoration(
        labelText: 'Quantity (Liters)',
        prefixIcon: Icon(Icons.local_gas_station),
      ),
      keyboardType: const TextInputType.numberWithOptions(decimal: true),
      onChanged: (_) => _calculateTotalCost(),
      validator: (value) => value?.isEmpty ?? true ? 'Please enter quantity' : null,
    );
  }

  Widget _buildCostFields() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        TextFormField(
          controller: _costPerLiterController,
          decoration: const InputDecoration(
            labelText: 'Cost per Liter (₹)',
            prefixIcon: Icon(Icons.payments),
          ),
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          onChanged: (_) => _calculateTotalCost(),
          validator: (value) => value?.isEmpty ?? true ? 'Please enter cost per liter' : null,
        ),
        const SizedBox(height: 12),
        TextFormField(
          controller: _totalCostController,
          decoration: const InputDecoration(
            labelText: 'Total Cost (₹)',
            prefixIcon: Icon(Icons.account_balance_wallet),
          ),
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          readOnly: true,
          validator: (value) => value?.isEmpty ?? true ? 'Please enter total cost' : null,
        ),
      ],
    );
  }

  Widget _buildOdometerField() {
    return TextFormField(
      controller: _odometerController,
      decoration: const InputDecoration(
        labelText: 'Odometer Reading (km)',
        prefixIcon: Icon(Icons.speed),
      ),
      keyboardType: TextInputType.number,
    );
  }

  Widget _buildFuelStationField() {
    return TextFormField(
      controller: _fuelStationController,
      decoration: const InputDecoration(
        labelText: 'Fuel Station',
        prefixIcon: Icon(Icons.location_on),
      ),
    );
  }

  Widget _buildFuelTypeField() {
    return DropdownButtonFormField<String>(
      decoration: const InputDecoration(
        labelText: 'Fuel Type',
        prefixIcon: Icon(Icons.local_gas_station),
      ),
      items: const [
        DropdownMenuItem(value: 'Diesel', child: Text('Diesel')),
        DropdownMenuItem(value: 'Petrol', child: Text('Petrol')),
        DropdownMenuItem(value: 'CNG', child: Text('CNG')),
        DropdownMenuItem(value: 'Electric', child: Text('Electric')),
      ],
      onChanged: (value) {
        _fuelTypeController.text = value ?? '';
      },
    );
  }

  Widget _buildDriverDropdown(List<DriverModel> drivers) {
    return DropdownButtonFormField<DriverModel>(
      decoration: const InputDecoration(
        labelText: 'Driver (Optional)',
        prefixIcon: Icon(Icons.person),
      ),
      items: drivers.map((d) {
        return DropdownMenuItem(
          value: d,
          child: Text(d.name),
        );
      }).toList(),
      onChanged: (value) {
        setState(() {
          _selectedDriver = value;
          _driverController.text = value?.name ?? '';
        });
      },
    );
  }

  void _calculateTotalCost() {
    final quantity = double.tryParse(_quantityController.text) ?? 0;
    final costPerLiter = double.tryParse(_costPerLiterController.text) ?? 0;
    final total = quantity * costPerLiter;
    _totalCostController.text = total.toStringAsFixed(2);
  }

  void _submitForm() {
    if (_formKey.currentState?.validate() ?? false) {
      final log = FuelLogModel(
        id: '',
        vehicleId: _selectedVehicle?.id ?? '',
        vehicleNumber: _selectedVehicle?.registrationNumber ?? '',
        date: _dateController.text,
        quantity: double.tryParse(_quantityController.text) ?? 0,
        costPerLiter: double.tryParse(_costPerLiterController.text) ?? 0,
        totalCost: double.tryParse(_totalCostController.text) ?? 0,
        odometerReading: int.tryParse(_odometerController.text),
        fuelStation: _fuelStationController.text.isEmpty ? null : _fuelStationController.text,
        fuelType: _fuelTypeController.text.isEmpty ? null : _fuelTypeController.text,
        driverId: _selectedDriver?.id,
        driverName: _selectedDriver?.name,
      );

      // TODO: Call API to save fuel log
      context.pop();
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Fuel entry saved successfully')),
      );
    }
  }
}
