import 'package:supabase_flutter/supabase_flutter.dart';

class AuthService {
  AuthService(this._client);

  final SupabaseClient? _client;

  bool get isConfigured => _client != null;
  Session? get session => _client?.auth.currentSession;
  String? get accessToken => session?.accessToken;

  Stream<AuthState> get authStateChanges => _client?.auth.onAuthStateChange ?? const Stream<AuthState>.empty();

  Future<AuthResponse> signInWithPassword(String email, String password) {
    final client = _client;
    if (client == null) throw StateError('Supabase Auth is not configured.');
    return client.auth.signInWithPassword(email: email, password: password);
  }

  Future<AuthResponse> signUp(String email, String password) {
    final client = _client;
    if (client == null) throw StateError('Supabase Auth is not configured.');
    return client.auth.signUp(email: email, password: password);
  }

  Future<void> resetPassword(String email) async {
    final client = _client;
    if (client == null) throw StateError('Supabase Auth is not configured.');
    await client.auth.resetPasswordForEmail(email);
  }

  Future<void> signOut() async {
    await _client?.auth.signOut();
  }
}
