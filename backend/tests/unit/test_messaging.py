from app.services.messaging import DemoMessagingProvider, DisabledMessagingProvider


def test_demo_provider_never_claims_delivery():
    result = DemoMessagingProvider().send_template_message(recipient="+963000000000", template_key="appointment_confirmed", variables={})
    assert result.accepted is True
    assert result.evidence == "demo"
    assert DemoMessagingProvider().query_delivery_status(provider_message_id="demo-message") == "provider_accepted"


def test_disabled_provider_fails_closed():
    result = DisabledMessagingProvider().send_template_message(recipient="+963000000000", template_key="appointment_confirmed", variables={})
    assert result.accepted is False
    assert result.error_code == "MESSAGE_PROVIDER_UNAVAILABLE"
