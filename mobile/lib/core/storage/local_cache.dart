import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

class LocalCache {
  static const schemaVersionKey = 'navimed.local.schemaVersion';
  static const providerCacheKey = 'navimed.cache.providers';
  static const appointmentCacheKey = 'navimed.cache.appointments';
  static const pharmacyCacheKey = 'navimed.cache.pharmacy';

  Future<void> migrateIfNeeded() async {
    final prefs = await SharedPreferencesAsync();
    final current = await prefs.getInt(schemaVersionKey) ?? 0;
    if (current == 0) {
      // v1 introduces namespaced safe-read caches. No authoritative business data is deleted.
      await prefs.setInt(schemaVersionKey, 1);
    }
  }

  Future<void> saveJson(String key, Object value) async {
    final prefs = await SharedPreferencesAsync();
    await prefs.setString(key, jsonEncode(value));
  }

  Future<Object?> readJson(String key) async {
    final prefs = await SharedPreferencesAsync();
    final raw = await prefs.getString(key);
    if (raw == null) return null;
    return jsonDecode(raw);
  }
}
