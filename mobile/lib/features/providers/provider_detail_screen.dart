import 'package:flutter/material.dart';

import '../../core/api/api_client.dart';
import '../../core/auth/auth_service.dart';
import '../../core/config/app_config.dart';
import '../../core/localization/app_strings.dart';

class ProviderDetailScreen extends StatefulWidget {
  const ProviderDetailScreen({super.key, required this.provider, required this.authService});

  final Map<String, dynamic> provider;
  final AuthService authService;

  @override
  State<ProviderDetailScreen> createState() => _ProviderDetailScreenState();
}

class _ProviderDetailScreenState extends State<ProviderDetailScreen> {
  late final ApiClient api;
  late Future<List<dynamic>> future;

  @override
  void initState() {
    super.initState();
    api = ApiClient(baseUrl: AppConfig.fromEnvironment().apiBaseUrl, authService: widget.authService);
    future = _loadAvailability();
  }

  Future<List<dynamic>> _loadAvailability() async {
    final result = await api.get('providers/${widget.provider['id']}/availability');
    return result is List ? result : <dynamic>[];
  }

  Future<void> _book(Map<String, dynamic> slot, AppStrings strings) async {
    try {
      final key = 'mobile-book-${DateTime.now().microsecondsSinceEpoch}';
      final hold = await api.post('appointments/holds', {'slot_id': '${slot['id']}'}, idempotencyKey: '$key-hold') as Map;
      final appointment = await api.post('appointments', {'hold_id': '${hold['id']}'}, idempotencyKey: '$key-appointment');
      if (!mounted) return;
      await showDialog<void>(context: context, builder: (context) => AlertDialog(title: Text(strings.bookingCreated), content: Text('$appointment'), actions: [TextButton(onPressed: () => Navigator.pop(context), child: Text(strings.close))]));
    } catch (error) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$error')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final strings = AppStrings(Localizations.localeOf(context));
    return Scaffold(
      appBar: AppBar(title: Text(strings.provider)),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text('${widget.provider['display_name'] ?? widget.provider['displayName'] ?? ''}', style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800)),
          const SizedBox(height: 8),
          Text('${widget.provider['specialty'] ?? ''}'),
          const SizedBox(height: 18),
          Text(strings.serverAuthoritative),
          const SizedBox(height: 8),
          Text(strings.bookingPolicyNotice),
          const SizedBox(height: 24),
          Text(strings.availableSlots, style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
          const SizedBox(height: 10),
          FutureBuilder<List<dynamic>>(
            future: future,
            builder: (context, snapshot) {
              if (snapshot.connectionState != ConnectionState.done) return Text(strings.loading);
              if (snapshot.hasError) return Text(strings.noData);
              final slots = snapshot.data ?? [];
              if (slots.isEmpty) return Text(strings.noData);
              return Column(children: slots.map((raw) {
                final slot = Map<String, dynamic>.from(raw as Map);
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Card(
                    child: ListTile(
                      title: Text('${slot['start_at'] ?? ''}'),
                      subtitle: Text('${slot['status'] ?? ''}'),
                      trailing: FilledButton(onPressed: slot['status'] == 'available' ? () => _book(slot, strings) : null, child: Text(strings.book)),
                    ),
                  ),
                );
              }).toList());
            },
          ),
        ],
      ),
    );
  }
}
