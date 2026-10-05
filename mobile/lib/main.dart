import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'app.dart';
import 'core/auth/auth_service.dart';
import 'core/config/app_config.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final config = AppConfig.fromEnvironment();
  SupabaseClient? supabaseClient;

  if (config.supabaseUrl.isNotEmpty && config.supabaseAnonKey.isNotEmpty) {
    await Supabase.initialize(url: config.supabaseUrl, anonKey: config.supabaseAnonKey);
    supabaseClient = Supabase.instance.client;
  }

  runApp(NaviMedApp(config: config, authService: AuthService(supabaseClient)));
}
