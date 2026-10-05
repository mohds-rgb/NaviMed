import 'package:flutter/material.dart';

import '../../core/api/api_client.dart';
import '../../core/auth/auth_service.dart';
import '../../core/config/app_config.dart';
import '../../core/localization/app_strings.dart';

class PharmacyScreen extends StatefulWidget {
  const PharmacyScreen({super.key});

  @override
  State<PharmacyScreen> createState() => _PharmacyScreenState();
}

class _PharmacyScreenState extends State<PharmacyScreen> {
  String? city;
  List<String> cities = [];
  bool loading = true;
  List<dynamic> items = [];
  final ApiClient _api = ApiClient(baseUrl: AppConfig.fromEnvironment().apiBaseUrl, authService: AuthService(null));

  @override
  void initState() {
    super.initState();
    _loadCities();
  }

  Future<void> _loadCities() async {
    try {
      final result = await _api.get('public/cities');
      final loaded = result is List ? result.map((e) => '$e').toList() : <String>[];
      if (mounted) {
        setState(() {
          cities = loaded;
          city = loaded.isEmpty ? null : loaded.first;
        });
        if (city != null) await _loadDuty();
      }
    } catch (_) {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> _loadDuty() async {
    if (city == null) return;
    setState(() => loading = true);
    try {
      final result = await _api.get('public/pharmacies/on-duty', query: {'city': city!});
      if (mounted) setState(() { items = result is List ? result : []; loading = false; });
    } catch (_) {
      if (mounted) setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final strings = AppStrings(Localizations.localeOf(context));
    if (loading && cities.isEmpty) return Center(child: Text(strings.loading));
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        if (cities.isNotEmpty) DropdownButtonFormField<String>(value: city, decoration: InputDecoration(labelText: strings.city), items: cities.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(), onChanged: (value) { setState(() => city = value); _loadDuty(); }),
        const SizedBox(height: 16),
        if (items.isEmpty) Text(strings.noData),
        ...items.map((raw) {
          final item = Map<String, dynamic>.from(raw as Map);
          return Padding(padding: const EdgeInsets.only(bottom: 10), child: Card(child: ListTile(leading: const CircleAvatar(child: Icon(Icons.local_pharmacy_outlined)), title: Text('${item['pharmacy_display_name'] ?? ''}'), subtitle: Text('${item['branch_display_name'] ?? ''}\n${item['address_summary'] ?? ''}'))));
        }),
      ],
    );
  }
}
