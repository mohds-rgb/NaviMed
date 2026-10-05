import 'package:flutter/material.dart';

import '../../core/api/api_client.dart';
import '../../core/auth/auth_service.dart';
import '../../core/config/app_config.dart';
import '../../core/localization/app_strings.dart';
import 'provider_detail_screen.dart';

class ProvidersScreen extends StatefulWidget {
  const ProvidersScreen({super.key, required this.authService});

  final AuthService authService;

  @override
  State<ProvidersScreen> createState() => _ProvidersScreenState();
}

class _ProvidersScreenState extends State<ProvidersScreen> {
  late final ApiClient api;
  late Future<List<dynamic>> future;

  @override
  void initState() {
    super.initState();
    api = ApiClient(baseUrl: AppConfig.fromEnvironment().apiBaseUrl, authService: widget.authService);
    future = _load();
  }

  Future<List<dynamic>> _load() async {
    final result = await api.get('providers');
    return result is List ? result : <dynamic>[];
  }

  @override
  Widget build(BuildContext context) {
    final strings = AppStrings(Localizations.localeOf(context));
    return FutureBuilder<List<dynamic>>(
      future: future,
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) return Center(child: Text(strings.loading));
        if (snapshot.hasError) return Center(child: Padding(padding: const EdgeInsets.all(20), child: Text(strings.noData)));
        final providers = snapshot.data ?? [];
        if (providers.isEmpty) return Center(child: Text(strings.noData));
        return RefreshIndicator(
          onRefresh: () async => setState(() => future = _load()),
          child: ListView.separated(
            padding: const EdgeInsets.all(20),
            itemCount: providers.length,
            separatorBuilder: (_, __) => const SizedBox(height: 10),
            itemBuilder: (context, index) {
              final item = Map<String, dynamic>.from(providers[index] as Map);
              return Card(
                child: ListTile(
                  leading: const CircleAvatar(child: Icon(Icons.person_outline)),
                  title: Text('${item['display_name'] ?? item['displayName'] ?? ''}'),
                  subtitle: Text('${item['specialty'] ?? ''}'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => ProviderDetailScreen(provider: item, authService: widget.authService))),
                ),
              );
            },
          ),
        );
      },
    );
  }
}
