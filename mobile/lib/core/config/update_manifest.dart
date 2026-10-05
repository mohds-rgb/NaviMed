import 'dart:convert';

import 'package:crypto/crypto.dart';
import 'package:http/http.dart' as http;

class UpdateManifest {
  const UpdateManifest({required this.appId, required this.versionName, required this.versionCode, required this.minimumSupportedVersionCode, required this.apkUrl, required this.sha256, required this.releaseChannel, required this.migrationVersion, required this.apiCompatibility});

  factory UpdateManifest.fromJson(Map<String, dynamic> json) => UpdateManifest(
        appId: '${json['appId']}',
        versionName: '${json['versionName']}',
        versionCode: (json['versionCode'] as num).toInt(),
        minimumSupportedVersionCode: (json['minimumSupportedVersionCode'] as num).toInt(),
        apkUrl: '${json['apkUrl']}',
        sha256: '${json['sha256']}',
        releaseChannel: '${json['releaseChannel']}',
        migrationVersion: (json['migrationVersion'] as num).toInt(),
        apiCompatibility: '${json['apiCompatibility']}',
      );

  final String appId;
  final String versionName;
  final int versionCode;
  final int minimumSupportedVersionCode;
  final String apkUrl;
  final String sha256;
  final String releaseChannel;
  final int migrationVersion;
  final String apiCompatibility;
}

class UpdateManifestClient {
  Future<UpdateManifest> fetch(Uri uri) async {
    final response = await http.get(uri);
    if (response.statusCode != 200) throw StateError('Update manifest unavailable.');
    return UpdateManifest.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  Future<bool> verifyApkBytes(List<int> bytes, String expectedSha256) async {
    final actual = sha256.convert(bytes).toString();
    return actual.toLowerCase() == expectedSha256.toLowerCase();
  }
}
