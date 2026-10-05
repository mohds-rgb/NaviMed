import 'dart:convert';

import 'package:http/http.dart' as http;

import '../auth/auth_service.dart';

class ApiException implements Exception {
  const ApiException(this.statusCode, this.code, this.message);
  final int statusCode;
  final String code;
  final String message;

  @override
  String toString() => '$code ($statusCode): $message';
}

class ApiClient {
  ApiClient({required this.baseUrl, required this.authService, http.Client? client}) : _client = client ?? http.Client();

  final String baseUrl;
  final AuthService authService;
  final http.Client _client;

  Uri _uri(String path, [Map<String, String>? query]) {
    final base = Uri.parse(baseUrl);
    final normalizedBase = base.path.endsWith('/') ? base.path.substring(0, base.path.length - 1) : base.path;
    return base.replace(path: '$normalizedBase/$path', queryParameters: query);
  }

  Future<dynamic> get(String path, {Map<String, String>? query}) async {
    final headers = <String, String>{'Accept': 'application/json'};
    final token = authService.accessToken;
    if (token != null) headers['Authorization'] = 'Bearer $token';
    final response = await _client.get(_uri(path, query), headers: headers);
    return _decode(response);
  }

  Future<dynamic> post(String path, Map<String, dynamic> body, {required String idempotencyKey}) async {
    final headers = <String, String>{
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'Idempotency-Key': idempotencyKey,
    };
    final token = authService.accessToken;
    if (token != null) headers['Authorization'] = 'Bearer $token';
    final response = await _client.post(_uri(path), headers: headers, body: jsonEncode(body));
    return _decode(response);
  }

  dynamic _decode(http.Response response) {
    dynamic decoded;
    try {
      decoded = response.body.isEmpty ? null : jsonDecode(response.body);
    } catch (_) {
      throw ApiException(response.statusCode, 'INVALID_RESPONSE', 'Server returned an invalid response.');
    }
    if (response.statusCode >= 400) {
      final error = decoded is Map<String, dynamic> ? decoded['error'] : null;
      final code = error is Map ? '${error['code'] ?? 'REQUEST_FAILED'}' : 'REQUEST_FAILED';
      final message = error is Map ? '${error['message'] ?? 'Request failed.'}' : 'Request failed.';
      throw ApiException(response.statusCode, code, message);
    }
    if (decoded is Map<String, dynamic> && decoded.containsKey('data')) return decoded['data'];
    return decoded;
  }
}
