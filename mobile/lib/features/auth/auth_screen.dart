import 'package:flutter/material.dart';

import '../../core/auth/auth_service.dart';
import '../../core/localization/app_strings.dart';
import '../../shared/widgets/navimed_brand.dart';

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key, required this.authService, this.onAuthenticated});

  final AuthService authService;
  final VoidCallback? onAuthenticated;

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  final email = TextEditingController();
  final password = TextEditingController();
  bool loading = false;
  bool registerMode = false;
  String? message;

  @override
  void dispose() {
    email.dispose();
    password.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (email.text.trim().isEmpty || password.text.isEmpty) {
      setState(() => message = AppStrings(Localizations.localeOf(context)).authInvalidInput);
      return;
    }
    setState(() {
      loading = true;
      message = null;
    });
    final strings = AppStrings(Localizations.localeOf(context));
    try {
      if (registerMode) {
        final response = await widget.authService.signUp(email.text.trim(), password.text);
        if (!mounted) return;
        if (response.session != null) {
          widget.onAuthenticated?.call();
        } else {
          setState(() => message = strings.registrationSubmitted);
        }
      } else {
        await widget.authService.signInWithPassword(email.text.trim(), password.text);
        if (mounted) widget.onAuthenticated?.call();
      }
    } catch (_) {
      if (mounted) setState(() => message = registerMode ? strings.registrationFailed : strings.authFailed);
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> _resetPassword() async {
    if (email.text.trim().isEmpty) {
      setState(() => message = AppStrings(Localizations.localeOf(context)).authInvalidInput);
      return;
    }
    setState(() {
      loading = true;
      message = null;
    });
    final strings = AppStrings(Localizations.localeOf(context));
    try {
      await widget.authService.resetPassword(email.text.trim());
      if (mounted) setState(() => message = strings.resetSubmitted);
    } catch (_) {
      if (mounted) setState(() => message = strings.resetFailed);
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final strings = AppStrings(Localizations.localeOf(context));
    if (!widget.authService.isConfigured) {
      return Scaffold(
        appBar: AppBar(title: Text(strings.signIn)),
        body: Center(child: Padding(padding: const EdgeInsets.all(24), child: Text(strings.authNotConfigured))),
      );
    }
    return Scaffold(
      appBar: AppBar(title: Text(registerMode ? strings.createAccount : strings.signIn)),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const NaviMedBrand(),
          const SizedBox(height: 12),
          Text(strings.authBoundary),
          const SizedBox(height: 24),
          TextField(controller: email, keyboardType: TextInputType.emailAddress, decoration: InputDecoration(labelText: strings.email)),
          const SizedBox(height: 12),
          TextField(controller: password, obscureText: true, decoration: InputDecoration(labelText: strings.password)),
          const SizedBox(height: 20),
          FilledButton(onPressed: loading ? null : _submit, child: Text(loading ? strings.loading : (registerMode ? strings.createAccount : strings.signIn))),
          if (!registerMode)
            TextButton(onPressed: loading ? null : _resetPassword, child: Text(strings.resetPassword)),
          TextButton(
            onPressed: loading ? null : () => setState(() { registerMode = !registerMode; message = null; }),
            child: Text(registerMode ? strings.haveAccount : strings.needAccount),
          ),
          if (message != null) ...[
            const SizedBox(height: 12),
            Text(message!, style: Theme.of(context).textTheme.bodyMedium),
          ],
        ],
      ),
    );
  }
}
