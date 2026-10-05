import 'package:flutter/material.dart';

import '../../core/api/api_client.dart';
import '../../core/auth/auth_service.dart';
import '../../core/config/app_config.dart';
import '../../core/localization/app_strings.dart';
import '../auth/auth_screen.dart';

class AppointmentsScreen extends StatefulWidget {
  const AppointmentsScreen({super.key, required this.authService});

  final AuthService authService;

  @override
  State<AppointmentsScreen> createState() => _AppointmentsScreenState();
}

class _AppointmentsScreenState extends State<AppointmentsScreen> {
  late final ApiClient api;
  late Future<List<dynamic>> future;

  @override
  void initState() {
    super.initState();
    api = ApiClient(baseUrl: AppConfig.fromEnvironment().apiBaseUrl, authService: widget.authService);
    future = _load();
  }

  Future<List<dynamic>> _load() async {
    final result = await api.get('appointments');
    return result is List ? result : <dynamic>[];
  }

  Future<void> _cancel(String id) async {
    try {
      await api.post('appointments/$id/cancel', const {}, idempotencyKey: 'mobile-cancel-${DateTime.now().microsecondsSinceEpoch}');
      if (mounted) setState(() => future = _load());
    } catch (error) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$error')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final strings = AppStrings(Localizations.localeOf(context));
    if (widget.authService.session == null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            Text(strings.authRequired),
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: widget.authService.isConfigured
                  ? () async {
                      await Navigator.of(context).push(MaterialPageRoute(builder: (_) => AuthScreen(authService: widget.authService)));
                      if (mounted) setState(() => future = _load());
                    }
                  : null,
              icon: const Icon(Icons.login),
              label: Text(strings.signIn),
            ),
          ]),
        ),
      );
    }
    return RefreshIndicator(
      onRefresh: () async => setState(() => future = _load()),
      child: FutureBuilder<List<dynamic>>(
        future: future,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) return ListView(children: [const SizedBox(height: 180), Center(child: Text(strings.loading))]);
          if (snapshot.hasError) return ListView(children: [const SizedBox(height: 180), Center(child: Text(strings.noData))]);
          final items = snapshot.data ?? [];
          if (items.isEmpty) return ListView(children: [const SizedBox(height: 180), Center(child: Text(strings.noData))]);
          return ListView.separated(
            padding: const EdgeInsets.all(20),
            itemCount: items.length,
            separatorBuilder: (_, __) => const SizedBox(height: 10),
            itemBuilder: (context, index) {
              final item = Map<String, dynamic>.from(items[index] as Map);
              final status = '${item['status'] ?? ''}';
              final id = '${item['id'] ?? ''}';
              final cancellable = {'requested', 'pendingConfirmation', 'confirmed'}.contains(status);
              return Card(
                child: ListTile(
                  leading: const CircleAvatar(child: Icon(Icons.event_available_outlined)),
                  title: Text('${item['scheduled_start_at'] ?? item['scheduledStartAt'] ?? ''}'),
                  subtitle: Text('${strings.status}: $status'),
                  trailing: cancellable
                      ? IconButton(tooltip: strings.cancel, icon: const Icon(Icons.cancel_outlined), onPressed: () => _cancel(id))
                      : null,
                ),
              );
            },
          );
        },
      ),
    );
  }
}
