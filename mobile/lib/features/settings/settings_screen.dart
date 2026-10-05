import 'package:flutter/material.dart';

import '../../core/auth/auth_service.dart';
import '../../core/localization/app_strings.dart';
import '../auth/auth_screen.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key, required this.locale, required this.onLanguageChanged, required this.authService});

  final Locale locale;
  final ValueChanged<Locale> onLanguageChanged;
  final AuthService authService;

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  Future<void> _handleAuth() async {
    if (widget.authService.session == null) {
      await Navigator.of(context).push(MaterialPageRoute(builder: (_) => AuthScreen(authService: widget.authService)));
    } else {
      await widget.authService.signOut();
    }
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final strings = AppStrings(widget.locale);
    final signedIn = widget.authService.session != null;
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Text(strings.settingsTitle, style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800)),
        const SizedBox(height: 12),
        Text(strings.language),
        RadioListTile(value: const Locale('ar'), groupValue: widget.locale, onChanged: (v) { if (v != null) widget.onLanguageChanged(v); }, title: const Text('العربية')),
        RadioListTile(value: const Locale('en'), groupValue: widget.locale, onChanged: (v) { if (v != null) widget.onLanguageChanged(v); }, title: const Text('English')),
        const Divider(height: 32),
        Text(signedIn ? strings.signedIn : strings.signedOut),
        const SizedBox(height: 10),
        FilledButton.tonalIcon(
          onPressed: widget.authService.isConfigured ? _handleAuth : null,
          icon: Icon(signedIn ? Icons.logout : Icons.login),
          label: Text(signedIn ? strings.signOut : strings.signIn),
        ),
      ],
    );
  }
}
