import 'package:flutter/material.dart';
import '../../../config/theme/app_colors.dart';

class LoadsScreen extends StatefulWidget {
  const LoadsScreen({super.key});

  @override
  State<LoadsScreen> createState() => _LoadsScreenState();
}

class _LoadsScreenState extends State<LoadsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  final List<LoadItem> _availableLoads = [
    LoadItem(
      id: 'LD-001',
      title: 'Steel Rods from Chennai to Bangalore',
      weight: '24 Ton',
      distance: '347 km',
      price: '₹35,000',
      pickup: 'Chennai → Bangalore',
      time: '29 May, 08:00 AM',
      status: LoadStatus.available,
    ),
  ];

  final List<LoadItem> _myBookings = [
    LoadItem(
      id: 'LD-BK-002',
      title: 'TN-38-BC-1001',
      weight: '24 Ton',
      distance: '347 km',
      price: '₹35,000',
      pickup: 'Chennai → Bangalore',
      time: '29 May, 08:00 AM',
      status: LoadStatus.delivering,
      driver: 'Rajesh Kumar',
      vehicle: 'TN-38-BC-1001',
    ),
    LoadItem(
      id: 'LD-BK-003',
      title: 'KA-01-HG-9922',
      weight: '18 Ton',
      distance: '284 km',
      price: '₹22,000',
      pickup: 'Bangalore → Chennai',
      time: '28 May, 02:00 AM',
      status: LoadStatus.delivered,
      driver: 'Suresh Singh',
      vehicle: 'KA-01-HG-9922',
    ),
    LoadItem(
      id: 'LD-BK-004',
      title: 'MH-12-QG-4455',
      weight: '30 Ton',
      distance: '502 km',
      price: '₹45,000',
      pickup: 'Mumbai → Pune',
      time: '27 May, 06:00 PM',
      status: LoadStatus.delivered,
      driver: 'Anil Verma',
      vehicle: 'MH-12-QG-4455',
    ),
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Loads'),
        backgroundColor: AppColors.background,
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Available Loads'),
            Tab(text: 'My Bookings'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          // Available Loads Tab
          _buildAvailableLoads(),
          // My Bookings Tab
          _buildMyBookings(),
        ],
      ),
    );
  }

  Widget _buildAvailableLoads() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _availableLoads.length,
      itemBuilder: (context, index) {
        return AvailableLoadCard(load: _availableLoads[index]);
      },
    );
  }

  Widget _buildMyBookings() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _myBookings.length,
      itemBuilder: (context, index) {
        return BookingLoadCard(load: _myBookings[index]);
      },
    );
  }
}

class AvailableLoadCard extends StatelessWidget {
  final LoadItem load;

  const AvailableLoadCard({required this.load, super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.cardBackground,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: AppColors.successBg,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Text(
                  'Available',
                  style: TextStyle(
                    color: AppColors.success,
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              Text(
                load.price,
                style: const TextStyle(
                  color: AppColors.success,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Title
          Text(
            load.title,
            style: const TextStyle(
              color: AppColors.textPrimary,
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
          ),

          const SizedBox(height: 12),

          // Route
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                const Icon(
                  Icons.route,
                  color: AppColors.textSecondary,
                  size: 16,
                ),
                const SizedBox(width: 8),
                Text(
                  load.pickup,
                  style: const TextStyle(
                    color: AppColors.textSecondary,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // Stats Row
          Row(
            children: [
              _StatChip(Icons.scale, load.weight),
              const SizedBox(width: 12),
              _StatChip(Icons.straighten, load.distance),
              const SizedBox(width: 12),
              _StatChip(Icons.access_time, load.time),
            ],
          ),

          const SizedBox(height: 16),

          // Book Now Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {},
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                padding: const EdgeInsets.symmetric(vertical: 12),
              ),
              child: const Text('Book Now'),
            ),
          ),
        ],
      ),
    );
  }
}

class BookingLoadCard extends StatelessWidget {
  final LoadItem load;

  const BookingLoadCard({required this.load, super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.cardBackground,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with Status
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: _getStatusBgColor(load.status),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  _getStatusText(load.status),
                  style: TextStyle(
                    color: _getStatusColor(load.status),
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              Text(
                load.price,
                style: const TextStyle(
                  color: AppColors.success,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Vehicle and Driver Info
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppColors.surface,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(
                  Icons.local_shipping,
                  color: AppColors.primary,
                  size: 24,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      load.vehicle ?? load.title,
                      style: const TextStyle(
                        color: AppColors.textPrimary,
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    if (load.driver != null) ...[
                      const SizedBox(height: 4),
                      Text(
                        load.driver!,
                        style: const TextStyle(
                          color: AppColors.textSecondary,
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Route
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                const Icon(
                  Icons.route,
                  color: AppColors.textSecondary,
                  size: 16,
                ),
                const SizedBox(width: 8),
                Text(
                  load.pickup,
                  style: const TextStyle(
                    color: AppColors.textSecondary,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // Stats Row
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _StatItem(Icons.scale, load.weight, 'Weight'),
              _StatItem(Icons.straighten, load.distance, 'Distance'),
              const Icon(
                Icons.chevron_right,
                color: AppColors.textMuted,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Color _getStatusColor(LoadStatus status) {
    switch (status) {
      case LoadStatus.available:
        return AppColors.success;
      case LoadStatus.delivering:
        return AppColors.warning;
      case LoadStatus.delivered:
        return AppColors.success;
    }
  }

  Color _getStatusBgColor(LoadStatus status) {
    switch (status) {
      case LoadStatus.available:
        return AppColors.successBg;
      case LoadStatus.delivering:
        return AppColors.warningBg;
      case LoadStatus.delivered:
        return AppColors.successBg;
    }
  }

  String _getStatusText(LoadStatus status) {
    switch (status) {
      case LoadStatus.available:
        return 'Available';
      case LoadStatus.delivering:
        return 'Delivering';
      case LoadStatus.delivered:
        return 'Delivered';
    }
  }
}

class _StatChip extends StatelessWidget {
  final IconData icon;
  final String value;

  const _StatChip(this.icon, this.value);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: AppColors.textSecondary, size: 14),
          const SizedBox(width: 4),
          Text(
            value,
            style: const TextStyle(
              color: AppColors.textSecondary,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  final IconData icon;
  final String value;
  final String label;

  const _StatItem(this.icon, this.value, this.label);

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, color: AppColors.textSecondary, size: 16),
        const SizedBox(width: 6),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              value,
              style: const TextStyle(
                color: AppColors.textPrimary,
                fontWeight: FontWeight.w600,
                fontSize: 14,
              ),
            ),
            Text(
              label,
              style: const TextStyle(
                color: AppColors.textSecondary,
                fontSize: 11,
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class LoadItem {
  final String id;
  final String title;
  final String weight;
  final String distance;
  final String price;
  final String pickup;
  final String time;
  final LoadStatus status;
  final String? driver;
  final String? vehicle;

  LoadItem({
    required this.id,
    required this.title,
    required this.weight,
    required this.distance,
    required this.price,
    required this.pickup,
    required this.time,
    required this.status,
    this.driver,
    this.vehicle,
  });
}

enum LoadStatus { available, delivering, delivered }