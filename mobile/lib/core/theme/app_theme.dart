import 'package:flutter/material.dart';

ThemeData buildAppTheme() {
  final scheme = ColorScheme.fromSeed(seedColor: const Color(0xFF0F766E), brightness: Brightness.light);
  return ThemeData(
    colorScheme: scheme,
    useMaterial3: true,
    scaffoldBackgroundColor: const Color(0xFFF7FAF9),
    inputDecorationTheme: const InputDecorationTheme(border: OutlineInputBorder(), filled: true),
    cardTheme: const CardThemeData(margin: EdgeInsets.zero, elevation: 0),
  );
}
