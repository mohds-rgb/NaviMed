# Android host

The Android host is included as a source-level template. The current verification environment does not contain the Flutter SDK, Android SDK, or Gradle wrapper, so the Android project has **not** been built here.

Before the first local build, run the Flutter tooling in `mobile/` and regenerate/refresh platform support if your installed Flutter template requires newer host files:

```bash
flutter pub get
flutter create --platforms=android .
```

Then re-apply the NaviMed application ID and manifest requirements documented in this directory before committing any generated changes.
