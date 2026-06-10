import 'package:intl/intl.dart';

final _currency = NumberFormat.currency(locale: 'en_IN', symbol: '₹', decimalDigits: 0);
final _compact = NumberFormat.compact(locale: 'en_IN');

String formatCurrency(num value) => _currency.format(value);

String formatCompactCurrency(num value) {
  if (value.abs() >= 100000) return '₹${_compact.format(value / 100000)}L';
  if (value.abs() >= 1000) return '₹${_compact.format(value / 1000)}K';
  return formatCurrency(value);
}

String formatDistance(num km) => '${km.toStringAsFixed(0)} km';
