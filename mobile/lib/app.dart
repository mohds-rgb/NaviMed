import 'package:flutter/material.dart';

import 'core/auth/auth_service.dart';
import 'core/config/app_config.dart';
import 'core/localization/app_strings.dart';
import 'core/theme/app_theme.dart';
import 'features/appointments/appointments_screen.dart';
import 'features/home/home_screen.dart';
import 'features/pharmacy/pharmacy_screen.dart';
import 'features/providers/providers_screen.dart';
import 'features/settings/settings_screen.dart';

class NaviMedApp extends StatefulWidget {
  const NaviMedApp({super.key, required this.config, required this.authService});

  final AppConfig config;
  final AuthService authService;

  @override
  State<NaviMedApp> createState() => _NaviMedAppState();
}

class _NaviMedAppState extends State<NaviMedApp> {
  Locale _locale = const Locale('ar');

  void _setLanguage(Locale locale) => setState(() => _locale = locale);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'NaviMed',
      theme: buildAppTheme(),
      locale: _locale,
      supportedLocales: const [Locale('ar'), Locale('en')],
      home: _AppShell(authService: widget.authService, locale: _locale, onLanguageChanged: _setLanguage),
    );
  }
}

class _AppShell extends StatefulWidget {
  const _AppShell({required this.authService, required this.locale, required this.onLanguageChanged});

  final AuthService authService;
  final Locale locale;
  final ValueChanged<Locale> onLanguageChanged;

  @override
  State<_AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<_AppShell> {
  int _index = 0;

  @override
  Widget build(BuildContext context) {
    final strings = AppStrings(widget.locale);
    final screens = [
      HomeScreen(onSelectTab: (i) => setState(() => _index = i), strings: strings),
      ProvidersScreen(authService: widget.authService),
      AppointmentsScreen(authService: widget.authService),
      const PharmacyScreen(),
      SettingsScreen(locale: widget.locale, onLanguageChanged: widget.onLanguageChanged, authService: widget.authService),
    ];

    return Directionality(
      textDirection: widget.locale.languageCode == 'ar' ? TextDirection.rtl : TextDirection.ltr,
      child: Scaffold(
        body: SafeArea(child: screens[_index]),
        bottomNavigationBar: NavigationBar(
          selectedIndex: _index,
          onDestinationSelected: (value) => setState(() => _index = value),
          destinations: [
            NavigationDestination(icon: const Icon(Icons.home_outlined), label: strings.home),
            NavigationDestination(icon: const Icon(Icons.medical_services_outlined), label: strings.providers),
            NavigationDestination(icon: const Icon(Icons.event_note_outlined), label: strings.appointments),
            NavigationDestination(icon: const Icon(Icons.local_pharmacy_outlined), label: strings.pharmacies),
            NavigationDestination(icon: const Icon(Icons.settings_outlined), label: strings.settings),
          ],
        ),
      ),
    );
  }
}
