import 'package:flutter/widgets.dart';

class AppStrings {
  AppStrings(this.locale);
  final Locale locale;
  bool get ar => locale.languageCode == 'ar';

  String get appName => 'NaviMed';
  String get home => ar ? 'الرئيسية' : 'Home';
  String get providers => ar ? 'الأطباء' : 'Providers';
  String get appointments => ar ? 'المواعيد' : 'Appointments';
  String get pharmacies => ar ? 'الصيدليات' : 'Pharmacies';
  String get settings => ar ? 'الإعدادات' : 'Settings';
  String get findProvider => ar ? 'ابحث عن طبيب أسنان' : 'Find a dentist';
  String get onDuty => ar ? 'صيدليات مناوبة اليوم' : 'Pharmacies on duty today';
  String get myAppointments => ar ? 'مواعيدي' : 'My appointments';
  String get coordination => ar ? 'تنسيق الرعاية الصحية والمواعيد' : 'Healthcare coordination & appointments';
  String get selectLanguage => ar ? 'اللغة' : 'Language';
  String get arabic => ar ? 'العربية' : 'Arabic';
  String get english => ar ? 'الإنجليزية' : 'English';
  String get loading => ar ? 'جارٍ التحميل...' : 'Loading...';
  String get city => ar ? 'المدينة' : 'City';
  String get noData => ar ? 'لا توجد بيانات متاحة حالياً' : 'No data available';
  String get lastVerified => ar ? 'آخر تحقق' : 'Last verified';
  String get safeInformation => ar ? 'معلومة خدمية — لا تُعد بديلاً عن الاستشارة الطبية' : 'Service information — not a substitute for professional medical advice';
  String get authoritativeServiceNotice => ar ? 'المعلومات الخدمية المعروضة يجب أن تأتي من المصدر المركزي المعتمد.' : 'Service information shown here must come from the authoritative backend.';
  String get provider => ar ? 'الطبيب' : 'Provider';
  String get serverAuthoritative => ar ? 'التوفر مصدره النظام المركزي المعتمد.' : 'Availability is server-authoritative.';
  String get bookingPolicyNotice => ar ? 'تأكيد الحجز يعتمد على سياسة العيادة.' : 'Booking confirmation depends on the clinic policy.';
  String get settingsTitle => ar ? 'الإعدادات' : 'Settings';
  String get language => ar ? 'اللغة' : 'Language';
  String get signIn => ar ? 'تسجيل الدخول' : 'Sign in';
  String get email => ar ? 'البريد الإلكتروني' : 'Email';
  String get password => ar ? 'كلمة المرور' : 'Password';
  String get authFailed => ar ? 'تعذر تسجيل الدخول. تحقق من بيانات الحساب.' : 'Sign-in failed. Check the account details.';
  String get authNotConfigured => ar ? 'Supabase Auth غير مضبوط في هذا البناء. استخدم إعدادات --dart-define قبل تشغيل الحسابات.' : 'Supabase Auth is not configured in this build. Provide the required --dart-define values to enable accounts.';
  String get secureApiNotice => ar ? 'المواعيد تُحمّل من النظام المركزي المعتمد. قم بإعداد Supabase Auth وواجهة API لاستخدام التدفق.' : 'Appointments are loaded from the authoritative backend. Configure Supabase Auth and API access to use this flow.';

  String get status => ar ? 'الحالة' : 'Status';
  String get cancel => ar ? 'إلغاء الموعد' : 'Cancel appointment';
  String get book => ar ? 'حجز' : 'Book';
  String get availableSlots => ar ? 'المواعيد المتاحة' : 'Available slots';
  String get bookingCreated => ar ? 'تم إنشاء طلب الموعد من خلال الخادم.' : 'Appointment request created through the authoritative backend.';
  String get close => ar ? 'إغلاق' : 'Close';
  String get createAccount => ar ? 'إنشاء حساب' : 'Create account';
  String get haveAccount => ar ? 'لدي حساب بالفعل' : 'I already have an account';
  String get needAccount => ar ? 'إنشاء حساب جديد' : 'Create a new account';
  String get resetPassword => ar ? 'نسيت كلمة المرور' : 'Forgot password';
  String get registrationSubmitted => ar ? 'تم إرسال طلب التسجيل. اتبع تعليمات مزود الهوية عند الحاجة.' : 'Registration submitted. Follow the identity provider confirmation flow when required.';
  String get registrationFailed => ar ? 'تعذر إنشاء الحساب.' : 'Account creation failed.';
  String get resetSubmitted => ar ? 'تم إرسال طلب إعادة تعيين كلمة المرور.' : 'Password reset request submitted.';
  String get resetFailed => ar ? 'تعذر إرسال طلب إعادة التعيين.' : 'Password reset request failed.';
  String get authInvalidInput => ar ? 'أدخل البريد الإلكتروني وكلمة المرور.' : 'Enter an email address and password.';
  String get authBoundary => ar ? 'الهوية والجلسة تتم إدارتهما عبر Supabase Auth.' : 'Identity and session lifecycle are managed through Supabase Auth.';
  String get authRequired => ar ? 'تحتاج إلى تسجيل الدخول للوصول إلى مواعيدك.' : 'Sign in to access your appointments.';
  String get signOut => ar ? 'تسجيل الخروج' : 'Sign out';
  String get signedIn => ar ? 'تم تسجيل الدخول.' : 'Signed in.';
  String get signedOut => ar ? 'غير مسجل الدخول.' : 'Signed out.';
}
