import 'package:flutter_test/flutter_test.dart';

import 'package:navimed/app.dart';
import 'package:navimed/core/auth/auth_service.dart';
import 'package:navimed/core/config/app_config.dart';

void main() {
  testWidgets('NaviMed renders the Arabic-first home shell', (tester) async {
    const config = AppConfig(
      apiBaseUrl: 'http://localhost:8000/v1',
      supabaseUrl: '',
      supabaseAnonKey: '',
      environment: 'test',
    );

    await tester.pumpWidget(NaviMedApp(config: config, authService: AuthService(null)));
    expect(find.text('NaviMed'), findsOneWidget);
    expect(find.text('نافيميد  •  Dental & Health Network'), findsOneWidget);
    expect(find.text('الرئيسية'), findsOneWidget);
  });
}
