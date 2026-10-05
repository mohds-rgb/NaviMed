# NaviMed Mobile

Flutter Android-first client. The app treats the backend as the authority for appointments, pharmacy publication and authorization. Local storage is limited to safe-read caches/settings and schema-version metadata.

Supabase credentials are supplied using `--dart-define`; they are never stored in source.


## Implemented flow coverage

- Public provider discovery and provider availability browsing.
- Public daily pharmacy-duty lookup.
- Supabase Auth sign-in, sign-up and password-reset request UI.
- Authenticated appointment listing.
- Slot hold + appointment creation with idempotency headers.
- Authenticated appointment cancellation.
- Arabic/English UI direction switching.

The mobile client has not been built or device-tested in this environment because Flutter/Dart/Android SDK are unavailable here.


## Branding and data boundary

The supplied NaviMed icon is stored under `assets/branding/` and is used by the mobile shell and Android launcher resources. The app does not display the project owner's name.

The mobile client never embeds real provider, patient, pharmacy, or emergency-contact datasets in source code. It obtains operational data from the configured backend.
