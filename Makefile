test:
	cd backend && python -m pytest

compile:
	python -m compileall backend/app backend/scripts

run-api:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

mobile-get:
	cd mobile && flutter pub get

mobile-run:
	cd mobile && flutter run --dart-define=NAVIMED_API_BASE_URL=http://10.0.2.2:8000/v1
