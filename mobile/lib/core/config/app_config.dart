class AppConfig {
  const AppConfig({required this.apiBaseUrl, required this.supabaseUrl, required this.supabaseAnonKey, required this.environment});

  factory AppConfig.fromEnvironment() {
    return const AppConfig(
      apiBaseUrl: String.fromEnvironment('NAVIMED_API_BASE_URL', defaultValue: 'http://10.0.2.2:8000/v1'),
      supabaseUrl: String.fromEnvironment('SUPABASE_URL'),
      supabaseAnonKey: String.fromEnvironment('SUPABASE_ANON_KEY'),
      environment: String.fromEnvironment('NAVIMED_ENV', defaultValue: 'development'),
    );
  }

  final String apiBaseUrl;
  final String supabaseUrl;
  final String supabaseAnonKey;
  final String environment;

  bool get isConfigured => supabaseUrl.isNotEmpty && supabaseAnonKey.isNotEmpty;
}
